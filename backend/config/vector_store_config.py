"""
Configuration du service de vector store.
"""
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration du vector store
VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "legacy").lower()  # 'legacy' ou 'faiss'
VECTOR_STORE_MODEL = os.getenv("VECTOR_STORE_MODEL", "all-MiniLM-L6-v2")
VECTOR_STORE_DATA_DIR = os.getenv("VECTOR_STORE_DATA_DIR", "data/vector_store")

# Fonction pour obtenir le type de vector store à utiliser
def get_vector_store_type():
    """
    Retourne le type de vector store à utiliser.
    
    Returns:
        str: 'legacy' ou 'faiss'
    """
    return VECTOR_STORE_TYPE

# Fonction pour obtenir la configuration du vector store
def get_vector_store_config():
    """
    Retourne la configuration du vector store.
    
    Returns:
        dict: Configuration du vector store
    """
    return {
        "type": VECTOR_STORE_TYPE,
        "model": VECTOR_STORE_MODEL,
        "data_dir": VECTOR_STORE_DATA_DIR
    }
