"""
Script de migration des données de l'ancien vector store vers le nouveau basé sur FAISS.
"""
import os
import sys
import logging
import argparse
from tqdm import tqdm

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vector_store_service import VectorStoreService
from services.vector_store_faiss_service import VectorStoreFaissService

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('migration_vector_store.log')
    ]
)
logger = logging.getLogger(__name__)

def migrate_vector_store(data_dir="data/vector_store", model_name="all-MiniLM-L6-v2"):
    """
    Migre les données de l'ancien vector store vers le nouveau basé sur FAISS.
    
    Args:
        data_dir: Répertoire de stockage des données
        model_name: Nom du modèle SentenceTransformer à utiliser
    """
    try:
        logger.info(f"Démarrage de la migration vers le vector store FAISS avec le modèle {model_name}")
        
        # Initialiser l'ancien service
        legacy_store = VectorStoreService(data_dir=data_dir)
        logger.info(f"Ancien vector store chargé: {len(legacy_store.chunks_index)} chunks")
        
        # Initialiser le nouveau service
        faiss_store = VectorStoreFaissService(model_name=model_name, data_dir=data_dir)
        
        # Migrer les données
        migrated_count = faiss_store.migrate_from_legacy_store(legacy_store)
        
        logger.info(f"Migration terminée: {migrated_count} chunks migrés sur {len(legacy_store.chunks_index)}")
        
        return migrated_count
    
    except Exception as e:
        logger.error(f"Erreur lors de la migration: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migration vers le vector store FAISS")
    parser.add_argument("--data-dir", default="data/vector_store", help="Répertoire de stockage des données")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Modèle SentenceTransformer à utiliser")
    args = parser.parse_args()
    
    migrate_vector_store(data_dir=args.data_dir, model_name=args.model)
