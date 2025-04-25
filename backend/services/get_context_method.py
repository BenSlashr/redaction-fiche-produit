    def get_context(self, query: str, client_id: str = None, top_k: int = 5, section_type: str = None) -> List[DocumentChunk]:
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
