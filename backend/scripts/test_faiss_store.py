"""
Script de test pour le nouveau vector store basé sur FAISS.
"""
import os
import sys
import logging
import argparse
import time
from tabulate import tabulate

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
        logging.FileHandler('test_vector_store.log')
    ]
)
logger = logging.getLogger(__name__)

def test_query_performance(legacy_store, faiss_store, queries, client_id=None):
    """
    Compare les performances de recherche entre l'ancien et le nouveau vector store.
    
    Args:
        legacy_store: Instance de l'ancien VectorStoreService
        faiss_store: Instance du nouveau VectorStoreFaissService
        queries: Liste de requêtes de test
        client_id: ID du client pour filtrer les résultats
    """
    results = []
    
    for query_info in queries:
        query = query_info["query"]
        section_type = query_info.get("section_type")
        
        # Test avec l'ancien store
        start_time = time.time()
        legacy_result = legacy_store.query_relevant_context(
            query=query,
            client_id=client_id,
            top_k=5,
            section_type=section_type
        )
        legacy_time = time.time() - start_time
        
        # Test avec le nouveau store
        start_time = time.time()
        faiss_result = faiss_store.query_relevant_context(
            query=query,
            client_id=client_id,
            top_k=5,
            section_type=section_type
        )
        faiss_time = time.time() - start_time
        
        # Comparer les résultats
        legacy_chunks = [chunk.chunk_id for chunk in legacy_result.chunks]
        faiss_chunks = [chunk.chunk_id for chunk in faiss_result.chunks]
        
        # Calculer l'intersection des résultats
        common_chunks = set(legacy_chunks).intersection(set(faiss_chunks))
        overlap_percent = len(common_chunks) / max(len(legacy_chunks), 1) * 100
        
        results.append({
            "query": query[:50] + "..." if len(query) > 50 else query,
            "section_type": section_type,
            "legacy_chunks": len(legacy_chunks),
            "faiss_chunks": len(faiss_chunks),
            "common_chunks": len(common_chunks),
            "overlap_percent": f"{overlap_percent:.1f}%",
            "legacy_time": f"{legacy_time*1000:.1f}ms",
            "faiss_time": f"{faiss_time*1000:.1f}ms",
            "speedup": f"{legacy_time/faiss_time:.1f}x"
        })
    
    # Afficher les résultats sous forme de tableau
    headers = ["Query", "Section", "Legacy", "FAISS", "Common", "Overlap", "Legacy Time", "FAISS Time", "Speedup"]
    table_data = [
        [
            r["query"], 
            r["section_type"] or "-", 
            r["legacy_chunks"], 
            r["faiss_chunks"], 
            r["common_chunks"],
            r["overlap_percent"],
            r["legacy_time"],
            r["faiss_time"],
            r["speedup"]
        ] 
        for r in results
    ]
    
    print("\nRésultats des tests de performance:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Calculer les moyennes
    avg_legacy_time = sum([time.time() - time.time() + float(r["legacy_time"].replace("ms", ""))/1000 for r in results]) / len(results)
    avg_faiss_time = sum([time.time() - time.time() + float(r["faiss_time"].replace("ms", ""))/1000 for r in results]) / len(results)
    avg_overlap = sum([float(r["overlap_percent"].replace("%", "")) for r in results]) / len(results)
    
    print(f"\nMoyennes:")
    print(f"Temps moyen (Legacy): {avg_legacy_time*1000:.1f}ms")
    print(f"Temps moyen (FAISS): {avg_faiss_time*1000:.1f}ms")
    print(f"Accélération moyenne: {avg_legacy_time/avg_faiss_time:.1f}x")
    print(f"Chevauchement moyen des résultats: {avg_overlap:.1f}%")

def main(data_dir="data/vector_store", model_name="all-MiniLM-L6-v2", client_id=None):
    """
    Exécute les tests de performance.
    
    Args:
        data_dir: Répertoire de stockage des données
        model_name: Nom du modèle SentenceTransformer à utiliser
        client_id: ID du client pour filtrer les résultats
    """
    try:
        logger.info(f"Démarrage des tests avec le modèle {model_name}")
        
        # Initialiser les services
        legacy_store = VectorStoreService(data_dir=data_dir)
        faiss_store = VectorStoreFaissService(model_name=model_name, data_dir=data_dir)
        
        # Définir les requêtes de test
        test_queries = [
            {"query": "caractéristiques techniques d'une cuve à eau de pluie", "section_type": "Caractéristiques techniques"},
            {"query": "avantages de l'utilisation d'une cuve à eau de pluie", "section_type": "Avantages"},
            {"query": "installation d'une cuve à eau de pluie", "section_type": "Installation et mise en service"},
            {"query": "entretien et maintenance d'une cuve à eau de pluie", "section_type": "Entretien et maintenance"},
            {"query": "cas d'utilisation d'une cuve à eau de pluie", "section_type": "Cas d'utilisation"},
            {"query": "description générale d'une cuve à eau de pluie", "section_type": "Introduction"}
        ]
        
        # Exécuter les tests
        test_query_performance(legacy_store, faiss_store, test_queries, client_id)
        
        logger.info("Tests terminés avec succès")
    
    except Exception as e:
        logger.error(f"Erreur lors des tests: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tests du vector store FAISS")
    parser.add_argument("--data-dir", default="data/vector_store", help="Répertoire de stockage des données")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Modèle SentenceTransformer à utiliser")
    parser.add_argument("--client-id", default=None, help="ID du client pour filtrer les résultats")
    args = parser.parse_args()
    
    main(data_dir=args.data_dir, model_name=args.model, client_id=args.client_id)
