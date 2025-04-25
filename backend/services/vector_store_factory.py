"""
Factory pour le service de vector store.
"""
import logging
from config.vector_store_config import get_vector_store_type, get_vector_store_config
from services.vector_store_service import VectorStoreService
from services.vector_store_faiss_service import VectorStoreFaissService

# Configuration du logging
logger = logging.getLogger(__name__)

class VectorStoreFactory:
    """
    Factory pour créer l'instance appropriée du service de vector store.
    """
    
    @staticmethod
    def create_vector_store(client_id=None):
        """
        Crée et retourne l'instance appropriée du service de vector store.
        
        Args:
            client_id: ID du client par défaut
            
        Returns:
            Une instance du service de vector store
        """
        config = get_vector_store_config()
        store_type = config["type"]
        data_dir = config["data_dir"]
        
        if store_type == "faiss":
            model_name = config["model"]
            logger.info(f"Création d'un VectorStoreFaissService avec le modèle {model_name}")
            return VectorStoreFaissService(
                model_name=model_name,
                data_dir=data_dir,
                client_id=client_id
            )
        else:
            logger.info("Création d'un VectorStoreService (legacy)")
            return VectorStoreService(
                data_dir=data_dir,
                client_id=client_id
            )
