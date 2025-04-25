"""
Service de gestion du vector store pour le système RAG.
Responsable de l'indexation et de la recherche des documents client.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import uuid
import json
import shutil
from datetime import datetime

from langchain_openai import OpenAIEmbeddings

# Importation conditionnelle de HuggingFaceEmbeddings
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("Module langchain_community non disponible. Les embeddings locaux ne seront pas disponibles.")
    HUGGINGFACE_AVAILABLE = False

from langchain.schema import Document

from models.rag_models import ClientDocument, DocumentChunk, RAGQuery, RAGResult
from services.document_processor import DocumentProcessor
from services.embedding_enrichment_service import EmbeddingEnrichmentService

# Configuration du logging
logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    Service de gestion du vector store pour le système RAG.
    Responsable de l'indexation et de la recherche des documents client.
    """
    
    def __init__(self, 
                embedding_service: str = "openai", 
                openai_api_key: str = None,
                persist_directory: str = None):
        """
        Initialise le service de vector store.
        
        Args:
            embedding_service: Service d'embeddings à utiliser ("openai" ou "local")
            openai_api_key: Clé API OpenAI (requise si embedding_service="openai")
            persist_directory: Répertoire de persistance pour le stockage
        """
        logger.debug(f"Initialisation du VectorStoreService avec {embedding_service}")
        
        self.embedding_service = embedding_service
        self.openai_api_key = openai_api_key
        
        # Répertoire par défaut pour la persistance
        if not persist_directory:
            persist_directory = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data",
                "document_store"
            )
        
        self.persist_directory = persist_directory
        
        # Initialisation du processeur de documents
        self.document_processor = DocumentProcessor()
        
        # Initialisation du service d'enrichissement des embeddings
        self.embedding_enrichment = EmbeddingEnrichmentService()
        
        # Initialisation des embeddings
        self._initialize_embeddings()
        
        # Initialisation du stockage
        self._initialize_storage()
        
        logger.debug("VectorStoreService initialisé avec succès")
    
    def _initialize_embeddings(self):
        """
        Initialise le service d'embeddings selon la configuration.
        """
        if self.embedding_service == "openai" or not HUGGINGFACE_AVAILABLE:
            if not self.openai_api_key:
                raise ValueError("La clé API OpenAI est requise pour utiliser les embeddings OpenAI")
            
            # Si HuggingFace n'est pas disponible mais était demandé, afficher un avertissement
            if self.embedding_service != "openai" and not HUGGINGFACE_AVAILABLE:
                logger.warning("Les embeddings locaux (HuggingFace) ont été demandés mais ne sont pas disponibles. Utilisation des embeddings OpenAI à la place.")
            
            logger.debug("Initialisation des embeddings OpenAI")
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        else:
            # Utilisation d'un modèle local pour les embeddings
            logger.debug("Initialisation des embeddings locaux (HuggingFace)")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
    
    def _initialize_storage(self):
        """
        Initialise le stockage de documents.
        """
        logger.debug(f"Initialisation du stockage dans {self.persist_directory}")
        
        try:
            # Créer le répertoire s'il n'existe pas
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Créer les sous-répertoires pour les documents et les chunks
            self.documents_dir = os.path.join(self.persist_directory, "documents")
            self.chunks_dir = os.path.join(self.persist_directory, "chunks")
            
            os.makedirs(self.documents_dir, exist_ok=True)
            os.makedirs(self.chunks_dir, exist_ok=True)
            
            # Fichier d'index pour les documents et les chunks
            self.documents_index_file = os.path.join(self.persist_directory, "documents_index.json")
            self.chunks_index_file = os.path.join(self.persist_directory, "chunks_index.json")
            
            # Charger ou créer les index
            if os.path.exists(self.documents_index_file):
                with open(self.documents_index_file, "r") as f:
                    self.documents_index = json.load(f)
            else:
                self.documents_index = {}
                with open(self.documents_index_file, "w") as f:
                    json.dump(self.documents_index, f)
            
            if os.path.exists(self.chunks_index_file):
                with open(self.chunks_index_file, "r") as f:
                    self.chunks_index = json.load(f)
            else:
                self.chunks_index = {}
                with open(self.chunks_index_file, "w") as f:
                    json.dump(self.chunks_index, f)
            
            logger.debug("Stockage initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du stockage: {str(e)}")
            raise
    
    def _save_document(self, document: ClientDocument) -> str:
        """
        Sauvegarde un document dans le stockage.
        
        Args:
            document: Document client à sauvegarder
            
        Returns:
            ID du document sauvegardé
        """
        document_id = document.document_id
        document_file = os.path.join(self.documents_dir, f"{document_id}.json")
        
        # Convertir le document en dictionnaire
        document_dict = {
            "document_id": document_id,
            "client_id": document.client_id,
            "title": document.title,
            "content": document.content,
            "source_type": document.source_type,
            "metadata": document.metadata,
            "created_at": datetime.now().isoformat()
        }
        
        # Sauvegarder le document
        with open(document_file, "w") as f:
            json.dump(document_dict, f, indent=2)
        
        # Mettre à jour l'index des documents
        self.documents_index[document_id] = {
            "document_id": document_id,
            "client_id": document.client_id,
            "title": document.title,
            "source_type": document.source_type,
            "created_at": document_dict["created_at"]
        }
        
        # Sauvegarder l'index
        with open(self.documents_index_file, "w") as f:
            json.dump(self.documents_index, f, indent=2)
        
        return document_id
    
    def _save_chunks(self, chunks: List[DocumentChunk]) -> List[str]:
        """
        Sauvegarde des chunks dans le stockage.
        
        Args:
            chunks: Liste de chunks à sauvegarder
            
        Returns:
            Liste des IDs des chunks sauvegardés
        """
        chunk_ids = []
        
        for chunk in chunks:
            chunk_id = chunk.chunk_id
            chunk_ids.append(chunk_id)
            
            chunk_file = os.path.join(self.chunks_dir, f"{chunk_id}.json")
            
            # Convertir le chunk en dictionnaire
            chunk_dict = {
                "chunk_id": chunk_id,
                "document_id": chunk.document_id,
                "content": chunk.content,
                "metadata": chunk.metadata
            }
            
            # Sauvegarder le chunk
            with open(chunk_file, "w") as f:
                json.dump(chunk_dict, f, indent=2)
            
            # Mettre à jour l'index des chunks
            # Utiliser directement les métadonnées du chunk pour le client_id et le titre
            self.chunks_index[chunk_id] = {
                "chunk_id": chunk_id,
                "document_id": chunk.document_id,
                "client_id": chunk.metadata.get("client_id"),
                "title": chunk.metadata.get("title", "")
            }
        
        # Sauvegarder l'index
        with open(self.chunks_index_file, "w") as f:
            json.dump(self.chunks_index, f, indent=2)
        
        return chunk_ids
    
    def add_document(self, document: Union[ClientDocument, List[DocumentChunk]]) -> str:
        """
        Ajoute un document au stockage.
        
        Args:
            document: Document client ou liste de chunks à ajouter
            
        Returns:
            ID du document ajouté
        """
        logger.debug(f"Ajout du document au stockage")
        
        try:
            # Traitement du document en chunks si c'est un ClientDocument
            chunks = []
            document_id = ""
            
            if isinstance(document, ClientDocument):
                # Sauvegarder le document
                document_id = self._save_document(document)
                
                # Traiter le document en chunks
                chunks = self.document_processor.process_document(document)
            else:
                chunks = document
                # Tous les chunks doivent avoir le même document_id
                if chunks:
                    document_id = chunks[0].metadata.get("document_id", str(uuid.uuid4()))
            
            # Sauvegarder les chunks
            chunk_ids = self._save_chunks(chunks)
            
            logger.debug(f"Document {document_id} ajouté avec succès, {len(chunks)} chunks indexés")
            return document_id
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du document: {str(e)}")
            raise
    
    def add_documents(self, documents: List[ClientDocument]) -> Dict[str, str]:
        """
        Ajoute plusieurs documents au stockage.
        
        Args:
            documents: Liste de documents client à ajouter
            
        Returns:
            Dictionnaire des IDs de document
        """
        logger.debug(f"Ajout de {len(documents)} documents au stockage")
        
        result = {}
        for document in documents:
            document_id = self.add_document(document)
            result[document.document_id] = document_id
        
        return result
    
    def query_relevant_context(self, 
                              query: str, 
                              product_info: Dict[str, Any] = None,
                              client_id: str = None,
                              filters: Dict[str, Any] = None, 
                              top_k: int = 5,
                              section_type: str = None) -> RAGResult:
        """
        Recherche le contexte pertinent pour une requête.
        
        Args:
            query: Requête textuelle
            product_info: Informations sur le produit
            client_id: ID du client pour filtrer les résultats
            filters: Filtres supplémentaires à appliquer
            top_k: Nombre de résultats à retourner
            section_type: Type de section pour enrichir la requête (Caractéristiques techniques, Avantages, etc.)
            
        Returns:
            Résultat RAG avec les chunks pertinents
        """
        logger.debug(f"Recherche de contexte pour la requête: {query}")
        
        try:
            logger.info(f"🔎 VECTOR_DEBUG: Début de la requête pour '{query[:100]}...'")
            if client_id:
                logger.info(f"🔎 VECTOR_DEBUG: Filtrage par client_id: {client_id}")
            
            # Construction de la requête enrichie avec le service d'enrichissement
            # Enrichir d'abord avec les informations de section
            enriched_query = self.embedding_enrichment.enrich_query(query, section_type)
            
            # Puis ajouter les informations produit si disponibles
            if product_info:
                product_name = product_info.get("name", "")
                product_category = product_info.get("category", "")
                if product_name:
                    enriched_query += f" pour le produit {product_name}"
                if product_category:
                    enriched_query += f" dans la catégorie {product_category}"
            
            # Préparation des filtres
            search_filters = {}
            if client_id:
                search_filters["client_id"] = client_id
            
            if filters:
                search_filters.update(filters)
            
            # Récupérer tous les chunks qui correspondent aux filtres
            filtered_chunks = []
            
            for chunk_id, chunk_info in self.chunks_index.items():
                # Appliquer les filtres
                match = True
                for key, value in search_filters.items():
                    if key == "client_id" and chunk_info.get("client_id") != value:
                        match = False
                        break
                
                if match:
                    # Charger le chunk
                    chunk_file = os.path.join(self.chunks_dir, f"{chunk_id}.json")
                    if os.path.exists(chunk_file):
                        with open(chunk_file, "r") as f:
                            chunk_data = json.load(f)
                            filtered_chunks.append(chunk_data)
            
            logger.info(f"🔎 VECTOR_DEBUG: {len(filtered_chunks)} chunks trouvés après filtrage")
            
            # Recherche améliorée avec enrichissement des contenus
            query_terms = enriched_query.lower().split()
            scored_chunks = []
            
            for chunk_data in filtered_chunks:
                # Enrichir le contenu du chunk pour la comparaison
                content = chunk_data["content"]
                metadata = chunk_data.get("metadata", {})
                
                # Catégoriser le contenu pour améliorer le scoring
                categories = self.embedding_enrichment.categorize_technical_content(content)
                
                # Calcul du score avec une pondération améliorée
                score = 0
                content_lower = content.lower()
                
                # Score de base sur les termes de la requête
                for term in query_terms:
                    if term in content_lower:
                        score += 1
                
                # Bonus selon le type de section
                if section_type:
                    # Bonus pour les chunks contenant des informations techniques
                    if section_type.lower() in ["caractéristiques techniques", "spécifications", "fiche technique"]:
                        # Bonus pour chaque catégorie technique trouvée
                        score += len(categories) * 2
                        
                        # Bonus spécifique pour les dimensions, poids, etc.
                        for key_category in ["dimensions", "poids", "capacité", "matériaux"]:
                            if key_category in categories:
                                score += 3
                    
                    # Bonus pour les avantages et bénéfices
                    elif section_type.lower() in ["avantages", "bénéfices", "points forts"]:
                        if any(term in content_lower for term in ["avantage", "bénéfice", "atout", "point fort", "meilleur"]):
                            score += 5
                    
                    # Bonus pour la description
                    elif section_type.lower() in ["description", "présentation", "introduction"]:
                        if any(term in content_lower for term in ["description", "présentation", "introduction", "vue d'ensemble"]):
                            score += 5
                    
                    # Bonus pour les fonctionnalités
                    elif section_type.lower() in ["fonctionnalités", "fonctions", "usages"]:
                        if any(term in content_lower for term in ["fonction", "fonctionnalité", "utilisation", "usage"]):
                            score += 5
                    
                    # Bonus pour les cas d'usage
                    elif section_type.lower() in ["cas d'usage", "applications", "utilisations"]:
                        if any(term in content_lower for term in ["cas d'usage", "application", "utilisation", "exemple"]):
                            score += 5
                
                if score > 0:
                    # Ajouter un identifiant unique (chunk_id) comme deuxième élément du tuple
                    # pour éviter la comparaison de dictionnaires lors du tri
                    scored_chunks.append((score, chunk_data["chunk_id"], chunk_data))
            
            logger.info(f"🔎 VECTOR_DEBUG: {len(scored_chunks)} chunks avec des scores")
            
            # Trier par score et prendre les top_k
            # Les tuples sont triés d'abord par le premier élément (score), puis par le deuxième (chunk_id)
            scored_chunks.sort(reverse=True)
            
            # Définir un seuil de score minimal selon le type de section
            min_score_threshold = 1  # Seuil par défaut
            
            if section_type:
                section_type_lower = section_type.lower()
                # Sections techniques nécessitent un score plus élevé pour garantir la pertinence
                if section_type_lower in ["caractéristiques techniques", "spécifications", "fiche technique"]:
                    min_score_threshold = 2
                # Sections d'installation et maintenance nécessitent aussi une bonne pertinence
                elif section_type_lower in ["installation", "mise en service", "entretien", "maintenance"]:
                    min_score_threshold = 2
            
            # Filtrer les chunks qui ont un score inférieur au seuil minimal
            filtered_scored_chunks = [chunk for chunk in scored_chunks if chunk[0] >= min_score_threshold]
            
            # Prendre les top_k chunks qui dépassent le seuil minimal
            top_chunks = filtered_scored_chunks[:top_k]
            
            logger.info(f"🔎 VECTOR_DEBUG: {len(scored_chunks)} chunks avec scores, {len(filtered_scored_chunks)} dépassent le seuil minimal")
            logger.info(f"🔎 VECTOR_DEBUG: {len(top_chunks)} chunks pertinents retenus après filtrage")
            
            # Conversion des résultats en chunks
            chunks = []
            for _, _, chunk_data in top_chunks:
                chunk = DocumentChunk(
                    chunk_id=chunk_data["chunk_id"],
                    document_id=chunk_data["document_id"],
                    content=chunk_data["content"],
                    metadata=chunk_data["metadata"]
                )
                chunks.append(chunk)
            
            # Construction du résultat
            result = RAGResult(
                query=RAGQuery(
                    query_text=query,
                    enriched_query=enriched_query,
                    filters=search_filters
                ),
                chunks=chunks,
                total_chunks=len(chunks)
            )
            
            logger.debug(f"Recherche terminée, {len(chunks)} chunks trouvés")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {str(e)}")
            raise
    
    def get_client_documents(self, client_id: str) -> List[Dict[str, Any]]:
        """
        Récupère les documents d'un client.
        
        Args:
            client_id: ID du client
            
        Returns:
            Liste des documents du client
        """
        logger.debug(f"Récupération des documents pour le client {client_id}")
        
        try:
            # Filtrer les documents par client_id
            client_documents = []
            
            for document_id, document_info in self.documents_index.items():
                if document_info.get("client_id") == client_id:
                    # Compter les chunks pour ce document
                    chunk_count = 0
                    for chunk_info in self.chunks_index.values():
                        if chunk_info.get("document_id") == document_id:
                            chunk_count += 1
                    
                    # Ajouter aux résultats
                    client_documents.append({
                        "document_id": document_id,
                        "client_id": client_id,
                        "title": document_info.get("title", ""),
                        "source_type": document_info.get("source_type", ""),
                        "chunk_count": chunk_count,
                        "created_at": document_info.get("created_at", "")
                    })
            
            logger.debug(f"Récupération terminée, {len(client_documents)} documents trouvés")
            return client_documents
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des documents: {str(e)}")
            raise
    
    def get_client_data_summary(self, client_id: str) -> Dict[str, Any]:
        """
        Récupère un résumé des données client disponibles.
        
        Args:
            client_id: ID du client
            
        Returns:
            Dictionnaire contenant le résumé des données client
        """
        logger.debug(f"Récupération du résumé des données client pour {client_id}")
        
        # Afficher la structure de l'index des documents pour le débogage
        logger.debug(f"Structure de l'index des documents: {self.documents_index}")
        logger.debug(f"Structure de l'index des chunks: {self.chunks_index}")
        
        # Filtrer les chunks par client_id
        client_chunks = {}
        for chunk_id, chunk in self.chunks_index.items():
            logger.debug(f"Chunk {chunk_id}: {chunk}")
            if chunk.get("client_id") == client_id:
                client_chunks[chunk_id] = chunk
        
        # Récupérer les documents uniques à partir des chunks
        client_documents = {}
        for chunk in client_chunks.values():
            doc_id = chunk.get("document_id")
            if doc_id and doc_id not in client_documents:
                # Récupérer le document complet si disponible
                if doc_id in self.documents_index:
                    client_documents[doc_id] = self.documents_index[doc_id]
                else:
                    # Sinon, créer une entrée à partir des informations du chunk
                    client_documents[doc_id] = {
                        "document_id": doc_id,
                        "client_id": client_id,
                        "title": chunk.get("title", "Document sans titre"),
                        "source_type": "unknown",
                        "created_at": chunk.get("created_at", datetime.now().isoformat())
                    }
        
        logger.debug(f"Documents trouvés pour le client {client_id}: {len(client_documents)}")
        
        # Compter les types de documents
        document_types = {}
        for doc in client_documents.values():
            source_type = doc.get("source_type", "unknown")
            document_types[source_type] = document_types.get(source_type, 0) + 1
        
        # Créer le résumé
        summary = {
            "client_id": client_id,
            "document_count": len(client_documents),
            "document_types": document_types,
            "documents": list(client_documents.values())
        }
        
        return summary
    
    def delete_document(self, document_id: str) -> bool:
        """
        Supprime un document du stockage.
        
        Args:
            document_id: ID du document à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        logger.debug(f"Suppression du document {document_id}")
        
        try:
            # Vérifier si le document existe
            if document_id not in self.documents_index:
                logger.warning(f"Document {document_id} non trouvé, aucune suppression effectuée")
                return False
            
            # Supprimer le fichier du document
            document_file = os.path.join(self.documents_dir, f"{document_id}.json")
            if os.path.exists(document_file):
                os.remove(document_file)
            
            # Supprimer les chunks associés
            chunks_to_delete = []
            for chunk_id, chunk_info in self.chunks_index.items():
                if chunk_info.get("document_id") == document_id:
                    chunks_to_delete.append(chunk_id)
            
            for chunk_id in chunks_to_delete:
                chunk_file = os.path.join(self.chunks_dir, f"{chunk_id}.json")
                if os.path.exists(chunk_file):
                    os.remove(chunk_file)
                del self.chunks_index[chunk_id]
            
            # Mettre à jour les index
            del self.documents_index[document_id]
            
            with open(self.documents_index_file, "w") as f:
                json.dump(self.documents_index, f, indent=2)
            
            with open(self.chunks_index_file, "w") as f:
                json.dump(self.chunks_index, f, indent=2)
            
            logger.debug(f"Document {document_id} supprimé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du document {document_id}: {str(e)}")
            raise
    
    def delete_client_documents(self, client_id: str) -> int:
        """
        Supprime tous les documents d'un client.
        
        Args:
            client_id: ID du client
            
        Returns:
            Nombre de documents supprimés
        """
        logger.debug(f"Suppression des documents pour le client {client_id}")
        
        try:
            # Récupérer les documents du client
            client_docs = self.get_client_documents(client_id)
            
            # Supprimer chaque document
            deleted_count = 0
            for doc in client_docs:
                document_id = doc["document_id"]
                if self.delete_document(document_id):
                    deleted_count += 1
            
            logger.debug(f"{deleted_count} documents supprimés pour le client {client_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression des documents du client {client_id}: {str(e)}")
            raise
