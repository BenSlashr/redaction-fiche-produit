"""
Service de vector store basé sur FAISS pour la recherche sémantique avancée.
"""
import os
import json
import logging
import pickle
import re
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import faiss
from sentence_transformers import SentenceTransformer

from models.rag_models import RAGQuery, RAGResult, DocumentChunk
from services.embedding_enrichment_service import EmbeddingEnrichmentService

# Configuration du logging
logger = logging.getLogger(__name__)

class VectorStoreFaissService:
    """
    Service de vector store utilisant FAISS et SentenceTransformers pour la recherche sémantique.
    """
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 data_dir: str = "data/vector_store",
                 client_id: str = None):
        """
        Initialise le service de vector store avec FAISS.
        
        Args:
            model_name: Nom du modèle SentenceTransformer à utiliser
            data_dir: Répertoire de stockage des données
            client_id: ID du client par défaut
        """
        logger.debug(f"Initialisation du VectorStoreFaissService avec le modèle {model_name}")
        
        # Répertoires de stockage
        self.data_dir = data_dir
        self.index_dir = os.path.join(data_dir, "faiss_indexes")
        self.chunks_dir = os.path.join(data_dir, "chunks")
        self.metadata_dir = os.path.join(data_dir, "metadata")
        
        # Créer les répertoires s'ils n'existent pas
        for directory in [self.data_dir, self.index_dir, self.chunks_dir, self.metadata_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Initialiser le modèle d'embeddings
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Modèle d'embeddings chargé: {model_name} (dimension: {self.embedding_dim})")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle d'embeddings: {str(e)}")
            raise
        
        # Initialiser le service d'enrichissement
        self.embedding_enrichment = EmbeddingEnrichmentService()
        
        # Client ID par défaut
        self.default_client_id = client_id
        
        # Charger ou créer les index FAISS
        self.indexes = {}
        self.chunks_metadata = {}
        self.load_indexes()
    
    def load_indexes(self):
        """
        Charge les index FAISS existants et les métadonnées associées.
        """
        # Charger les métadonnées des chunks
        metadata_file = os.path.join(self.metadata_dir, "chunks_metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, "r") as f:
                    self.chunks_metadata = json.load(f)
                logger.info(f"Métadonnées chargées: {len(self.chunks_metadata)} chunks")
            except Exception as e:
                logger.error(f"Erreur lors du chargement des métadonnées: {str(e)}")
                self.chunks_metadata = {}
        
        # Charger les index FAISS par client
        client_dirs = [d for d in os.listdir(self.index_dir) if os.path.isdir(os.path.join(self.index_dir, d))]
        for client_id in client_dirs:
            index_file = os.path.join(self.index_dir, client_id, "faiss_index.bin")
            if os.path.exists(index_file):
                try:
                    self.indexes[client_id] = faiss.read_index(index_file)
                    logger.info(f"Index FAISS chargé pour le client {client_id}")
                except Exception as e:
                    logger.error(f"Erreur lors du chargement de l'index FAISS pour {client_id}: {str(e)}")
    
    def save_indexes(self):
        """
        Sauvegarde les index FAISS et les métadonnées associées.
        """
        # Sauvegarder les métadonnées des chunks
        metadata_file = os.path.join(self.metadata_dir, "chunks_metadata.json")
        try:
            with open(metadata_file, "w") as f:
                json.dump(self.chunks_metadata, f)
            logger.info(f"Métadonnées sauvegardées: {len(self.chunks_metadata)} chunks")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des métadonnées: {str(e)}")
        
        # Sauvegarder les index FAISS par client
        for client_id, index in self.indexes.items():
            client_dir = os.path.join(self.index_dir, client_id)
            os.makedirs(client_dir, exist_ok=True)
            index_file = os.path.join(client_dir, "faiss_index.bin")
            try:
                faiss.write_index(index, index_file)
                logger.info(f"Index FAISS sauvegardé pour le client {client_id}")
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde de l'index FAISS pour {client_id}: {str(e)}")
    
    def add_chunk(self, 
                 chunk_id: str,
                 document_id: str,
                 content: str,
                 metadata: Dict[str, Any],
                 client_id: str = None):
        """
        Ajoute un chunk au vector store.
        
        Args:
            chunk_id: ID unique du chunk
            document_id: ID du document parent
            content: Contenu textuel du chunk
            metadata: Métadonnées associées au chunk
            client_id: ID du client (utilise le client par défaut si non spécifié)
        """
        if not client_id:
            client_id = self.default_client_id or "default"
        
        try:
            # Générer l'embedding pour le contenu
            embedding = self.model.encode([content])[0]
            
            # Créer ou récupérer l'index pour ce client
            if client_id not in self.indexes:
                self.indexes[client_id] = faiss.IndexFlatL2(self.embedding_dim)
            
            # Ajouter l'embedding à l'index
            self.indexes[client_id].add(np.array([embedding], dtype=np.float32))
            
            # Sauvegarder les métadonnées du chunk
            chunk_data = {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "content": content,
                "metadata": metadata,
                "client_id": client_id,
                "index_id": self.indexes[client_id].ntotal - 1  # ID dans l'index FAISS
            }
            
            # Sauvegarder le chunk dans le fichier JSON
            chunk_file = os.path.join(self.chunks_dir, f"{chunk_id}.json")
            with open(chunk_file, "w") as f:
                json.dump(chunk_data, f)
            
            # Mettre à jour les métadonnées
            self.chunks_metadata[chunk_id] = {
                "client_id": client_id,
                "document_id": document_id,
                "index_id": chunk_data["index_id"],
                "metadata": metadata
            }
            
            logger.info(f"Chunk {chunk_id} ajouté à l'index pour le client {client_id}")
            
            # Sauvegarder les index et métadonnées
            self.save_indexes()
            
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du chunk {chunk_id}: {str(e)}")
            return False
    
    def query_relevant_context(self, 
                              query: str, 
                              product_info: Dict[str, Any] = None,
                              client_id: str = None,
                              filters: Dict[str, Any] = None, 
                              top_k: int = 10,
                              section_type: str = None) -> RAGResult:
        """
        Recherche le contexte pertinent pour une requête en utilisant FAISS.
        
        Args:
            query: Requête textuelle
            product_info: Informations sur le produit
            client_id: ID du client pour filtrer les résultats
            filters: Filtres supplémentaires à appliquer
            top_k: Nombre de résultats à retourner
            section_type: Type de section pour enrichir la requête
            
        Returns:
            Résultat RAG avec les chunks pertinents
        """
        logger.debug(f"Recherche de contexte pour la requête: {query}")
        
        try:
            if not client_id:
                client_id = self.default_client_id or "default"
            
            logger.info(f"🔎 VECTOR_DEBUG: Début de la requête pour '{query[:100]}...'")
            logger.info(f"🔎 VECTOR_DEBUG: Filtrage par client_id: {client_id}")
            
            # Vérifier si l'index existe pour ce client
            if client_id not in self.indexes:
                logger.warning(f"Aucun index trouvé pour le client {client_id}")
                return RAGResult(
                    query=RAGQuery(query_text=query, enriched_query=query, filters=filters or {}),
                    chunks=[],
                    total_chunks=0
                )
            
            # Enrichir la requête avec le service d'enrichissement
            enriched_query = self.embedding_enrichment.enrich_query(query, section_type)
            
            # Ajouter les informations produit si disponibles
            if product_info:
                product_name = product_info.get("name", "")
                product_category = product_info.get("category", "")
                if product_name:
                    enriched_query += f" pour le produit {product_name}"
                if product_category:
                    enriched_query += f" dans la catégorie {product_category}"
            
            # Générer l'embedding pour la requête enrichie
            query_embedding = self.model.encode([enriched_query])[0]
            
            # Rechercher les chunks similaires - récupérer plus de résultats pour un meilleur filtrage
            D, I = self.indexes[client_id].search(
                np.array([query_embedding], dtype=np.float32), 
                min(top_k * 4, self.indexes[client_id].ntotal)  # Récupérer plus de résultats pour le filtrage
            )
            
            # Récupérer les chunks correspondants et appliquer les filtres
            chunks = []
            chunk_ids_in_index = {}
            
            # Inverser le mapping pour trouver les chunk_ids à partir des index_ids
            for chunk_id, metadata in self.chunks_metadata.items():
                if metadata["client_id"] == client_id:
                    chunk_ids_in_index[metadata["index_id"]] = chunk_id
            
            # Récupérer les chunks et appliquer les filtres
            filtered_chunks = []
            for i, index_id in enumerate(I[0]):
                if index_id in chunk_ids_in_index:
                    chunk_id = chunk_ids_in_index[index_id]
                    chunk_file = os.path.join(self.chunks_dir, f"{chunk_id}.json")
                    
                    if os.path.exists(chunk_file):
                        with open(chunk_file, "r") as f:
                            chunk_data = json.load(f)
                        
                        # Appliquer les filtres supplémentaires si spécifiés
                        match = True
                        if filters:
                            for key, value in filters.items():
                                if key in chunk_data["metadata"] and chunk_data["metadata"][key] != value:
                                    match = False
                                    break
                        
                        if match:
                            # Ajouter le score de similarité
                            chunk_data["similarity_score"] = float(1.0 / (1.0 + D[0][i]))
                            filtered_chunks.append(chunk_data)
            
            logger.info(f"🔎 VECTOR_DEBUG: {len(filtered_chunks)} chunks trouvés après filtrage")
            
            # Appliquer un scoring supplémentaire basé sur le type de section et le contenu
            scored_chunks = []
            
            for chunk_data in filtered_chunks:
                content = chunk_data["content"]
                metadata = chunk_data.get("metadata", {})
                base_score = chunk_data["similarity_score"] * 10  # Convertir en échelle 0-10
                
                # Bonus pour la densité d'informations techniques (nombres, unités, mesures)
                technical_density = len(re.findall(r'\d+(?:[.,]\d+)?\s*(?:cm|mm|m|pouces|po|inch|kg|g|L|l|W|kW|bar|%)', content.lower()))
                additional_score = min(technical_density * 0.5, 3)  # Bonus max de 3 points pour la densité technique
                
                # Bonus pour les listes (souvent utilisées pour énumérer des caractéristiques)
                if re.search(r'[•\-\*]\s+\w+', content) or re.search(r'\d+\.\s+\w+', content):
                    additional_score += 1
                
                if section_type:
                    section_type_lower = section_type.lower()
                    
                    # Bonus pour les sections techniques
                    if section_type_lower in ["caractéristiques techniques", "spécifications", "fiche technique", "specs", "technique"]:
                        # Termes techniques généraux
                        tech_terms = ["dimension", "poids", "capacité", "matériau", "technique", "spécification", 
                                     "caractéristique", "mesure", "performance", "puissance", "résistance", "norme", 
                                     "certification", "garantie", "composition"]
                        
                        # Unités de mesure
                        units = ["cm", "mm", "m", "kg", "g", "l", "litre", "w", "kw", "bar", "°c", "db", "hz"]
                        
                        # Compter les termes techniques et les unités
                        tech_term_count = sum(1 for term in tech_terms if term in content.lower())
                        unit_count = sum(1 for unit in units if unit in content.lower())
                        
                        # Bonus proportionnel au nombre de termes techniques et d'unités trouvés
                        additional_score += min(tech_term_count * 0.5, 2.5)  # Max 2.5 points
                        additional_score += min(unit_count * 0.5, 2.5)  # Max 2.5 points
                    
                    # Bonus pour les avantages
                    elif section_type_lower in ["avantages", "bénéfices", "points forts", "atouts"]:
                        advantage_terms = ["avantage", "bénéfice", "atout", "point fort", "meilleur", "optimal", 
                                          "efficace", "pratique", "facile", "rapide", "économique", "durable", 
                                          "fiable", "robuste", "innovant", "exclusif", "unique"]
                        
                        advantage_count = sum(1 for term in advantage_terms if term in content.lower())
                        additional_score += min(advantage_count * 0.5, 5)  # Max 5 points
                    
                    # Bonus pour la description
                    elif section_type_lower in ["description", "présentation", "introduction", "aperçu"]:
                        desc_terms = ["description", "présentation", "introduction", "aperçu", "produit", 
                                     "conçu", "développé", "solution", "gamme", "modèle", "série"]
                        
                        desc_count = sum(1 for term in desc_terms if term in content.lower())
                        additional_score += min(desc_count * 0.5, 5)  # Max 5 points
                    
                    # Bonus pour les cas d'usage
                    elif section_type_lower in ["cas d'usage", "applications", "utilisations", "exemples", "scénarios"]:
                        usage_terms = ["cas d'usage", "application", "utilisation", "exemple", "scénario", 
                                      "contexte", "situation", "client", "utilisateur", "besoin", "solution"]
                        
                        usage_count = sum(1 for term in usage_terms if term in content.lower())
                        additional_score += min(usage_count * 0.5, 5)  # Max 5 points
                    
                    # Bonus pour l'installation
                    elif section_type_lower in ["installation", "montage", "mise en service", "assemblage", "configuration"]:
                        install_terms = ["installation", "mise en service", "montage", "assemblage", "configuration", 
                                        "étape", "procédure", "outil", "connecter", "brancher", "fixer", "visser"]
                        
                        install_count = sum(1 for term in install_terms if term in content.lower())
                        additional_score += min(install_count * 0.5, 5)  # Max 5 points
                    
                    # Bonus pour l'entretien
                    elif section_type_lower in ["entretien", "maintenance", "nettoyage", "conservation"]:
                        maint_terms = ["entretien", "maintenance", "nettoyage", "conservation", "stockage", 
                                      "hivernage", "protection", "durabilité", "préserver", "prolonger"]
                        
                        maint_count = sum(1 for term in maint_terms if term in content.lower())
                        additional_score += min(maint_count * 0.5, 5)  # Max 5 points
                
                # Score final
                final_score = base_score + additional_score
                scored_chunks.append((final_score, chunk_data["chunk_id"], chunk_data))
            
            logger.info(f"🔎 VECTOR_DEBUG: {len(scored_chunks)} chunks pertinents retenus après scoring")
            
            # Trier par score et prendre les top_k
            scored_chunks.sort(reverse=True)
            top_chunks = scored_chunks[:top_k]
            
            logger.info(f"🔎 VECTOR_DEBUG: {len(top_chunks)} chunks pertinents retenus après scoring")
            
            # Conversion des résultats en chunks pour le RAG
            result_chunks = []
            for score, _, chunk_data in top_chunks:
                chunk = DocumentChunk(
                    chunk_id=chunk_data["chunk_id"],
                    document_id=chunk_data["document_id"],
                    content=chunk_data["content"],
                    metadata=chunk_data["metadata"]
                )
                result_chunks.append(chunk)
            
            # Construction du résultat
            result = RAGResult(
                query=RAGQuery(
                    query_text=query,
                    enriched_query=enriched_query,
                    filters=filters or {}
                ),
                chunks=result_chunks,
                total_chunks=len(result_chunks)
            )
            
            logger.debug(f"Recherche terminée, {len(result_chunks)} chunks trouvés")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return RAGResult(
                query=RAGQuery(query_text=query, enriched_query=query, filters=filters or {}),
                chunks=[],
                total_chunks=0
            )
    
    def get_client_data_summary(self, client_id: str) -> Dict[str, Any]:
        """
        Récupère un résumé des données client disponibles.
        
        Args:
            client_id: ID du client
            
        Returns:
            Dictionnaire contenant le résumé des données client
        """
        logger.debug(f"Récupération du résumé des données client pour {client_id}")
        
        # Filtrer les chunks par client_id
        client_chunks = {}
        for chunk_id, chunk_info in self.chunks_metadata.items():
            if chunk_info.get("client_id") == client_id:
                client_chunks[chunk_id] = chunk_info
        
        # Récupérer les documents uniques à partir des chunks
        client_documents = {}
        for chunk_id, chunk_info in client_chunks.items():
            doc_id = chunk_info.get("document_id")
            if doc_id and doc_id not in client_documents:
                # Récupérer le fichier du chunk pour obtenir plus d'informations
                chunk_file = os.path.join(self.chunks_dir, f"{chunk_id}.json")
                if os.path.exists(chunk_file):
                    try:
                        with open(chunk_file, "r") as f:
                            chunk_data = json.load(f)
                        
                        # Extraire les métadonnées du document
                        metadata = chunk_data.get("metadata", {})
                        
                        client_documents[doc_id] = {
                            "document_id": doc_id,
                            "client_id": client_id,
                            "title": metadata.get("title", "Document sans titre"),
                            "source_type": metadata.get("source_type", "unknown"),
                            "created_at": metadata.get("created_at", datetime.now().isoformat())
                        }
                    except Exception as e:
                        logger.error(f"Erreur lors de la lecture du chunk {chunk_id}: {str(e)}")
        
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
            # Vérifier si le document existe (au moins un chunk avec ce document_id)
            document_exists = False
            chunks_to_delete = []
            
            # Identifier les chunks à supprimer
            for chunk_id, chunk_info in self.chunks_metadata.items():
                if chunk_info.get("document_id") == document_id:
                    document_exists = True
                    chunks_to_delete.append(chunk_id)
            
            if not document_exists:
                logger.warning(f"Document {document_id} non trouvé, aucune suppression effectuée")
                return False
            
            # Pour chaque chunk à supprimer
            for chunk_id in chunks_to_delete:
                # Récupérer les informations du chunk
                chunk_info = self.chunks_metadata.get(chunk_id)
                if not chunk_info:
                    continue
                
                client_id = chunk_info.get("client_id")
                index_id = chunk_info.get("index_id")
                
                # Supprimer le fichier du chunk
                chunk_file = os.path.join(self.chunks_dir, f"{chunk_id}.json")
                if os.path.exists(chunk_file):
                    os.remove(chunk_file)
                
                # Supprimer l'entrée des métadonnées
                if chunk_id in self.chunks_metadata:
                    del self.chunks_metadata[chunk_id]
            
            # Sauvegarder les métadonnées mises à jour
            self.save_indexes()
            
            logger.debug(f"Document {document_id} supprimé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du document {document_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
        
    def migrate_from_legacy_store(self, legacy_store):
        """
        Migre les données depuis l'ancien vector store.
        
        Args:
            legacy_store: Instance de l'ancien VectorStoreService
        """
        logger.info("Début de la migration depuis l'ancien vector store")
        
        try:
            # Parcourir tous les chunks de l'ancien store
            migrated_count = 0
            
            for chunk_id, chunk_info in legacy_store.chunks_index.items():
                chunk_file = os.path.join(legacy_store.chunks_dir, f"{chunk_id}.json")
                
                if os.path.exists(chunk_file):
                    with open(chunk_file, "r") as f:
                        chunk_data = json.load(f)
                    
                    # Ajouter le chunk au nouveau store
                    success = self.add_chunk(
                        chunk_id=chunk_data["chunk_id"],
                        document_id=chunk_data["document_id"],
                        content=chunk_data["content"],
                        metadata=chunk_data["metadata"],
                        client_id=chunk_info.get("client_id", "default")
                    )
                    
                    if success:
                        migrated_count += 1
            
            logger.info(f"Migration terminée: {migrated_count} chunks migrés")
            return migrated_count
        
        except Exception as e:
            logger.error(f"Erreur lors de la migration: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return 0
