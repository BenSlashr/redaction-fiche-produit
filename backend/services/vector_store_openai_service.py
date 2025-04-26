"""
Service de vector store basé sur FAISS avec embeddings OpenAI pour la recherche sémantique avancée.
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
from openai import OpenAI

from models.rag_models import RAGQuery, RAGResult, DocumentChunk
from services.embedding_enrichment_service import EmbeddingEnrichmentService

# Configuration du logging
logger = logging.getLogger(__name__)

class VectorStoreOpenAIService:
    """
    Service de vector store utilisant FAISS et l'API OpenAI pour la recherche sémantique.
    """
    
    def __init__(self, 
                 model_name: str = "text-embedding-3-small",
                 data_dir: str = "data/vector_store",
                 client_id: str = None):
        """
        Initialise le service de vector store avec FAISS et OpenAI.
        
        Args:
            model_name: Nom du modèle OpenAI à utiliser pour les embeddings
            data_dir: Répertoire de stockage des données
            client_id: ID du client par défaut
        """
        logger.debug(f"Initialisation du VectorStoreOpenAIService avec le modèle {model_name}")
        
        # Répertoires de stockage
        self.data_dir = data_dir
        self.index_dir = os.path.join(data_dir, "faiss_indexes")
        self.chunks_dir = os.path.join(data_dir, "chunks")
        self.metadata_dir = os.path.join(data_dir, "metadata")
        
        # Créer les répertoires s'ils n'existent pas
        for directory in [self.data_dir, self.index_dir, self.chunks_dir, self.metadata_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Initialiser le client OpenAI et le modèle d'embeddings
        try:
            self.model_name = model_name
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Définir la dimension d'embedding en fonction du modèle
            if model_name == "text-embedding-3-small":
                self.embedding_dim = 1536
            elif model_name == "text-embedding-3-large":
                self.embedding_dim = 3072
            else:
                # Valeur par défaut pour d'autres modèles
                self.embedding_dim = 1536
                
            logger.info(f"Client OpenAI initialisé avec le modèle d'embeddings: {model_name} (dimension: {self.embedding_dim})")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du client OpenAI: {str(e)}")
            raise
        
        # Initialiser le service d'enrichissement
        self.embedding_enrichment = EmbeddingEnrichmentService()
        
        # Client ID par défaut
        self.default_client_id = client_id
        
        # Charger ou créer les index FAISS
        self.indexes = {}
        self.chunks_metadata = {}
        self.load_indexes()
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Génère un embedding pour le texte donné en utilisant l'API OpenAI.
        
        Args:
            text: Texte à encoder
            
        Returns:
            np.ndarray: Vecteur d'embedding
        """
        try:
            # Tronquer le texte si nécessaire (limite de tokens OpenAI)
            if len(text) > 8000:
                text = text[:8000]
                
            response = self.openai_client.embeddings.create(
                model=self.model_name,
                input=text
            )
            
            # Convertir en numpy array
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            return embedding
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'embedding OpenAI: {str(e)}")
            # Retourner un vecteur de zéros en cas d'erreur
            return np.zeros(self.embedding_dim, dtype=np.float32)
    
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
                    logger.error(f"Erreur lors du chargement de l'index FAISS pour le client {client_id}: {str(e)}")
    
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
                logger.error(f"Erreur lors de la sauvegarde de l'index FAISS pour le client {client_id}: {str(e)}")
    
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
        if client_id is None:
            client_id = self.default_client_id or "default"
        
        # Générer l'embedding pour le contenu
        embedding = self.get_embedding(content)
        
        # Créer ou mettre à jour l'index FAISS pour ce client
        if client_id not in self.indexes:
            # Créer un nouvel index
            index = faiss.IndexFlatL2(self.embedding_dim)
            self.indexes[client_id] = index
        
        # Ajouter l'embedding à l'index
        self.indexes[client_id].add(np.array([embedding]))
        
        # Stocker les métadonnées du chunk
        chunk_key = f"{client_id}:{chunk_id}"
        self.chunks_metadata[chunk_key] = {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "content": content,
            "metadata": metadata,
            "client_id": client_id,
            "index": self.indexes[client_id].ntotal - 1,  # Index dans le vector store
            "created_at": datetime.now().isoformat()
        }
        
        # Sauvegarder les modifications
        self.save_indexes()
        
        logger.info(f"Chunk {chunk_id} ajouté pour le client {client_id}")
    
    def query_relevant_context(self, 
                              query: str, 
                              product_info: Dict[str, Any] = None,
                              client_id: str = None,
                              filters: Dict[str, Any] = None, 
                              top_k: int = 10,
                              section_type: str = None):
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
        if client_id is None:
            client_id = self.default_client_id or "default"
        
        # Vérifier si l'index existe pour ce client
        if client_id not in self.indexes or self.indexes[client_id].ntotal == 0:
            logger.warning(f"Aucun index FAISS trouvé pour le client {client_id}")
            return RAGResult(
                query=RAGQuery(text=query, product_info=product_info),
                chunks=[],
                total_chunks=0
            )
        
        # Enrichir la requête si nécessaire
        enriched_query = query
        if section_type and product_info:
            enriched_query = self.embedding_enrichment.enrich_query(query, product_info, section_type)
            logger.debug(f"Requête enrichie: {enriched_query}")
        
        # Générer l'embedding pour la requête
        query_embedding = self.get_embedding(enriched_query)
        
        # Rechercher les chunks similaires
        D, I = self.indexes[client_id].search(np.array([query_embedding]), min(top_k * 2, self.indexes[client_id].ntotal))
        
        # Filtrer et formater les résultats
        chunks = []
        for i, idx in enumerate(I[0]):
            # Trouver le chunk correspondant à cet index
            chunk_key = None
            for key, metadata in self.chunks_metadata.items():
                if metadata["client_id"] == client_id and metadata["index"] == idx:
                    chunk_key = key
                    break
            
            if chunk_key is None:
                continue
            
            chunk_metadata = self.chunks_metadata[chunk_key]
            
            # Appliquer les filtres si spécifiés
            if filters:
                skip = False
                for filter_key, filter_value in filters.items():
                    if filter_key in chunk_metadata["metadata"]:
                        if chunk_metadata["metadata"][filter_key] != filter_value:
                            skip = True
                            break
                if skip:
                    continue
            
            # Ajouter le chunk aux résultats
            chunks.append(DocumentChunk(
                id=chunk_metadata["chunk_id"],
                document_id=chunk_metadata["document_id"],
                content=chunk_metadata["content"],
                metadata=chunk_metadata["metadata"],
                score=float(D[0][i])
            ))
            
            # Limiter le nombre de résultats
            if len(chunks) >= top_k:
                break
        
        # Trier les chunks par score (du plus pertinent au moins pertinent)
        chunks.sort(key=lambda x: x.score)
        
        return RAGResult(
            query=RAGQuery(text=query, product_info=product_info),
            chunks=chunks,
            total_chunks=len(chunks)
        )
    
    def get_client_data_summary(self, client_id: str):
        """
        Récupère un résumé des données client disponibles.
        
        Args:
            client_id: ID du client
            
        Returns:
            Dictionnaire contenant le résumé des données client
        """
        if not client_id:
            return {
                "client_id": None,
                "document_count": 0,
                "document_types": {},
                "documents": []
            }
        
        # Récupérer tous les chunks pour ce client
        client_chunks = {k: v for k, v in self.chunks_metadata.items() if v["client_id"] == client_id}
        
        # Regrouper par document
        documents = {}
        document_types = {}
        
        for chunk_key, chunk_data in client_chunks.items():
            doc_id = chunk_data["document_id"]
            if doc_id not in documents:
                doc_type = chunk_data["metadata"].get("source_type", "unknown")
                documents[doc_id] = {
                    "document_id": doc_id,
                    "title": chunk_data["metadata"].get("title", "Document sans titre"),
                    "source_type": doc_type,
                    "chunk_count": 0
                }
                document_types[doc_type] = document_types.get(doc_type, 0) + 1
            
            documents[doc_id]["chunk_count"] += 1
        
        return {
            "client_id": client_id,
            "document_count": len(documents),
            "document_types": document_types,
            "documents": list(documents.values())
        }
    
    def delete_document(self, document_id: str):
        """
        Supprime un document du stockage.
        
        Args:
            document_id: ID du document à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        if not document_id:
            return False
        
        # Trouver tous les chunks associés à ce document
        chunks_to_delete = {}
        for chunk_key, chunk_data in self.chunks_metadata.items():
            if chunk_data["document_id"] == document_id:
                chunks_to_delete[chunk_key] = chunk_data
        
        if not chunks_to_delete:
            logger.warning(f"Aucun chunk trouvé pour le document {document_id}")
            return False
        
        # Supprimer les chunks par client
        clients_to_update = set()
        for chunk_key, chunk_data in chunks_to_delete.items():
            client_id = chunk_data["client_id"]
            clients_to_update.add(client_id)
            del self.chunks_metadata[chunk_key]
        
        # Reconstruire les index FAISS pour les clients affectés
        for client_id in clients_to_update:
            # Récupérer tous les chunks restants pour ce client
            client_chunks = {k: v for k, v in self.chunks_metadata.items() if v["client_id"] == client_id}
            
            if not client_chunks:
                # Supprimer l'index si plus aucun chunk
                if client_id in self.indexes:
                    del self.indexes[client_id]
                continue
            
            # Créer un nouvel index
            new_index = faiss.IndexFlatL2(self.embedding_dim)
            
            # Ajouter les embeddings restants
            embeddings = []
            for chunk_key, chunk_data in sorted(client_chunks.items(), key=lambda x: x[1]["index"]):
                # Générer l'embedding pour le contenu
                embedding = self.get_embedding(chunk_data["content"])
                embeddings.append(embedding)
                
                # Mettre à jour l'index dans les métadonnées
                self.chunks_metadata[chunk_key]["index"] = len(embeddings) - 1
            
            # Ajouter les embeddings au nouvel index
            if embeddings:
                new_index.add(np.array(embeddings))
            
            # Remplacer l'ancien index
            self.indexes[client_id] = new_index
        
        # Sauvegarder les modifications
        self.save_indexes()
        
        logger.info(f"Document {document_id} supprimé avec succès")
        return True
