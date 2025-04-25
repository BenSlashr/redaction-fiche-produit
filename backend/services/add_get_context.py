#!/usr/bin/env python3
"""
Script pour ajouter la méthode get_context au fichier vector_store_service.py
"""

import re

# Chemin du fichier à modifier
file_path = "services/vector_store_service.py"

# Contenu de la méthode get_context à ajouter
get_context_method = """    def get_context(self, query: str, client_id: str = None, top_k: int = 5, section_type: str = None) -> List[DocumentChunk]:
        """
        Récupère les chunks pertinents pour une requête.
        Méthode simplifiée pour l'intégration avec d'autres services.
        
        Args:
            query: Requête textuelle
            client_id: ID du client pour filtrer les résultats
            top_k: Nombre de résultats à retourner
            section_type: Type de section (Caractéristiques techniques, Avantages, etc.)
            
        Returns:
            Liste des chunks pertinents
        """
        logger.debug(f"Récupération du contexte pour la requête: {query}, section_type: {section_type}")
        
        result = self.query_relevant_context(
            query=query,
            client_id=client_id,
            top_k=top_k,
            section_type=section_type
        )
        
        return result.chunks
"""

# Lire le contenu du fichier
with open(file_path, "r") as file:
    content = file.read()

# Trouver la position de la méthode query_relevant_context
pattern = r"def query_relevant_context\(self,"
match = re.search(pattern, content)

if match:
    # Position où insérer la nouvelle méthode
    insert_position = match.start()
    
    # Trouver le début de la ligne
    line_start = content.rfind("\n", 0, insert_position) + 1
    
    # Insérer la méthode get_context avant query_relevant_context
    new_content = content[:line_start] + get_context_method + "\n    " + content[line_start:]
    
    # Écrire le contenu modifié dans le fichier
    with open(file_path, "w") as file:
        file.write(new_content)
    
    print("Méthode get_context ajoutée avec succès.")
else:
    print("Méthode query_relevant_context non trouvée dans le fichier.")
