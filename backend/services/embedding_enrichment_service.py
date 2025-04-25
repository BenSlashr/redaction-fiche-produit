"""
Service d'enrichissement des embeddings pour améliorer la pertinence des résultats RAG.
"""
import re
import logging
from typing import Dict, List, Any, Optional

# Configuration du logging
logger = logging.getLogger(__name__)

class EmbeddingEnrichmentService:
    """
    Service d'enrichissement des embeddings pour améliorer la pertinence des résultats RAG.
    Détecte et catégorise les informations techniques dans les textes pour enrichir les embeddings.
    """
    
    def __init__(self):
        """
        Initialise le service d'enrichissement des embeddings.
        """
        logger.debug("Initialisation du EmbeddingEnrichmentService")
        
        # Patterns pour différentes catégories d'informations techniques
        self.patterns = {
            "dimensions": [
                r'\d+\s*(?:cm|mm|m|pouces|po|inch)(?:\s*[xX]\s*\d+\s*(?:cm|mm|m|pouces|po|inch))+', 
                r'(?:hauteur|largeur|longueur|diamètre|profondeur|épaisseur)\s*:?\s*\d+\s*(?:cm|mm|m|pouces|po|inch)',
                r'(?:dimensions|taille|mesure)\s*:?\s*\d+',
                r'\d+\s*(?:cm|mm|m)\s*(?:de|d\')\s*(?:hauteur|largeur|longueur|diamètre|profondeur|épaisseur)'
            ],
            "poids": [
                r'\d+(?:[.,]\d+)?\s*(?:kg|g|tonnes|lbs|t)',
                r'(?:poids|masse|charge)\s*:?\s*\d+(?:[.,]\d+)?',
                r'(?:pèse|pesant)\s*\d+(?:[.,]\d+)?\s*(?:kg|g|tonnes|lbs|t)'
            ],
            "capacité": [
                r'\d+(?:[.,]\d+)?\s*(?:L|l|litres|litre|m3|mL|cl|m³)',
                r'(?:capacité|contenance|volume|stockage)\s*:?\s*\d+(?:[.,]\d+)?',
                r'(?:peut contenir|contient jusqu\'à)\s*\d+(?:[.,]\d+)?\s*(?:L|l|litres|litre|m3|mL|cl|m³)'
            ],
            "matériaux": [
                r'(?:fabriqué|composé|constitué|conçu)\s*(?:en|de|d\')\s*(?:plastique|métal|acier|bois|aluminium|PE|PVC|PEHD|polypropylène|polyéthylène|inox)',
                r'(?:matériau|matière|composition|structure)\s*:?\s*(?:plastique|métal|acier|bois|aluminium|PE|PVC|PEHD|polypropylène|polyéthylène|inox)',
                r'(?:en|de)\s*(?:plastique|métal|acier|bois|aluminium|PE|PVC|PEHD|polypropylène|polyéthylène|inox)\s*(?:de qualité|résistant|durable)'
            ],
            "couleur": [
                r'(?:couleur|coloris|teinte)\s*:?\s*(?:blanc|noir|gris|bleu|vert|rouge|jaune|marron|beige|anthracite|transparent)',
                r'(?:disponible en|existe en|proposé en|livré en)\s*(?:blanc|noir|gris|bleu|vert|rouge|jaune|marron|beige|anthracite|transparent)',
                r'(?:blanc|noir|gris|bleu|vert|rouge|jaune|marron|beige|anthracite|transparent)\s*(?:mat|brillant|satiné)'
            ],
            "performance": [
                r'(?:débit|pression|résistance|performance|puissance|rendement)\s*:?\s*\d+(?:[.,]\d+)?\s*(?:W|kW|bar|l/min|m³/h)',
                r'(?:consommation|rendement|efficacité|productivité)\s*:?\s*\d+(?:[.,]\d+)?',
                r'(?:jusqu\'à|max|maximum|jusqu\'à)\s*\d+(?:[.,]\d+)?\s*(?:W|kW|bar|l/min|m³/h|%)'
            ],
            "garantie": [
                r'(?:garantie|durée de vie|assurance qualité)\s*:?\s*\d+\s*(?:an|ans|mois|année|années)',
                r'garantie\s*(?:constructeur|fabricant|usine)\s*(?:de)?\s*\d+\s*(?:an|ans|mois|année|années)',
                r'(?:garanti|assuré)\s*(?:pendant|durant|pour)\s*\d+\s*(?:an|ans|mois|année|années)'
            ],
            "installation": [
                r'(?:installation|montage|assemblage|mise en place)\s*(?:facile|simple|rapide|sans outil)',
                r'(?:s\'installe|se monte|s\'assemble)\s*(?:facilement|simplement|rapidement|sans outil)',
                r'(?:temps d\'installation|durée de montage)\s*:?\s*\d+\s*(?:min|minute|minutes|heure|heures)'
            ],
            "normes": [
                r'(?:norme|certification|homologation|standard)\s*:?\s*(?:CE|NF|ISO|EN|DIN)\s*\d*',
                r'(?:conforme|répond|respecte)\s*(?:à la|aux)\s*(?:norme|certification|homologation|standard)\s*(?:CE|NF|ISO|EN|DIN)\s*\d*',
                r'(?:CE|NF|ISO|EN|DIN)\s*\d*\s*(?:certifié|homologué|approuvé)'
            ],
            "compatibilité": [
                r'(?:compatible|adapté|conçu)\s*(?:avec|pour)\s*(?:les|tous les|différents)?\s*(?:modèles|marques|systèmes|appareils)',
                r'(?:compatibilité|adaptation)\s*(?:avec|pour)\s*(?:les|tous les|différents)?\s*(?:modèles|marques|systèmes|appareils)',
                r'(?:s\'adapte|se connecte|s\'intègre)\s*(?:à|avec|sur)\s*(?:les|tous les|différents)?\s*(?:modèles|marques|systèmes|appareils)'
            ]
        }
        
        logger.debug("EmbeddingEnrichmentService initialisé avec succès")
    
    def categorize_technical_content(self, text: str) -> Dict[str, List[str]]:
        """
        Détecte et catégorise les informations techniques dans un texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire des catégories détectées avec les extraits correspondants
        """
        categories = {}
        
        for category, pattern_list in self.patterns.items():
            matches = []
            for pattern in pattern_list:
                found = re.findall(pattern, text, re.IGNORECASE)
                if found:
                    matches.extend(found)
            
            if matches:
                categories[category] = matches
        
        return categories
    
    def enrich_text_for_embedding(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Enrichit un texte pour améliorer la pertinence des embeddings.
        
        Args:
            text: Texte à enrichir
            metadata: Métadonnées associées au texte
            
        Returns:
            Texte enrichi
        """
        # Détecter les catégories d'informations techniques
        categories_with_matches = self.categorize_technical_content(text)
        categories = list(categories_with_matches.keys())
        
        # Si aucune catégorie n'est détectée, retourner le texte original
        if not categories:
            return text
        
        # Créer un préfixe d'enrichissement
        prefix = "Ce texte contient des informations techniques sur: " + ", ".join(categories) + ". "
        
        # Ajouter des extraits pour chaque catégorie
        for category, matches in categories_with_matches.items():
            if matches:
                # Limiter à 2 extraits par catégorie pour éviter un préfixe trop long
                extraits = matches[:2]
                prefix += f"[{category}: {' | '.join(extraits)}] "
        
        # Ajouter des métadonnées si disponibles
        if metadata:
            if "source_type" in metadata:
                prefix += f"[source: {metadata['source_type']}] "
            if "title" in metadata:
                prefix += f"[document: {metadata['title']}] "
        
        # Combiner le préfixe et le texte original
        enriched_text = prefix + text
        
        return enriched_text
    
    def enrich_query(self, query: str, section_type: Optional[str] = None) -> str:
        """
        Enrichit une requête en fonction du type de section demandée.
        
        Args:
            query: Requête à enrichir
            section_type: Type de section (Caractéristiques techniques, Avantages, etc.)
            
        Returns:
            Requête enrichie
        """
        enriched_query = query
        
        if section_type:
            # Sections techniques
            if section_type.lower() in ["caractéristiques techniques", "spécifications", "fiche technique", "specs", "technique"]:
                enriched_query = "Recherche exhaustive d'informations techniques détaillées sur: dimensions, poids, capacité, matériaux, performance, normes, compatibilité, résistance, garantie, couleur, composition. Inclure toutes les mesures, valeurs et spécifications précises. " + query
            
            # Sections avantages
            elif section_type.lower() in ["avantages", "bénéfices", "points forts", "atouts"]:
                enriched_query = "Recherche exhaustive d'informations sur les avantages, bénéfices et points forts: atouts, valeur ajoutée, différenciation, innovation, exclusivité, économies, facilité, confort, durabilité, fiabilité, praticité. " + query
            
            # Sections utilisation
            elif section_type.lower() in ["utilisation", "mode d'emploi", "fonctionnement", "usage", "emploi"]:
                enriched_query = "Recherche exhaustive d'informations sur l'utilisation, le fonctionnement et le mode d'emploi: étapes détaillées, procédure complète, manipulation, réglages, paramètres, précautions, conseils pratiques, astuces d'utilisation. " + query
            
            # Sections description
            elif section_type.lower() in ["description", "présentation", "introduction", "aperçu"]:
                enriched_query = "Recherche exhaustive d'une description générale et complète du produit: vue d'ensemble, introduction, contexte, positionnement, public cible, besoins adressés, problèmes résolus, histoire du produit. " + query
            
            # Sections fonctionnalités
            elif section_type.lower() in ["fonctionnalités", "fonctions", "usages", "caractéristiques", "features"]:
                enriched_query = "Recherche exhaustive des fonctionnalités, fonctions et usages du produit: toutes les capacités, options, modes, réglages, paramètres configurables, variantes, extensions possibles. " + query
            
            # Sections cas d'usage
            elif section_type.lower() in ["cas d'usage", "applications", "utilisations", "exemples", "scénarios"]:
                enriched_query = "Recherche exhaustive des cas d'usage, applications et exemples d'utilisation concrets: tous les scénarios, situations, contextes d'utilisation, témoignages, retours d'expérience, secteurs d'application. " + query
            
            # Sections installation
            elif section_type.lower() in ["installation", "montage", "mise en service", "assemblage", "configuration"]:
                enriched_query = "Recherche exhaustive sur l'installation, le montage et la mise en service: toutes les étapes de configuration, préparation, outils nécessaires, temps requis, précautions, connexions, branchements, tests. " + query
            
            # Sections entretien
            elif section_type.lower() in ["entretien", "maintenance", "nettoyage", "conservation"]:
                enriched_query = "Recherche exhaustive sur l'entretien, la maintenance et le nettoyage: fréquence, méthodes, produits recommandés, précautions, durabilité, conservation, stockage, hivernage, protection. " + query
            
            # Sections environnement
            elif section_type.lower() in ["environnement", "écologie", "développement durable", "impact"]:
                enriched_query = "Recherche exhaustive sur l'impact environnemental, l'écologie et le développement durable: matériaux recyclables, économie d'énergie, réduction des déchets, empreinte carbone, certifications environnementales. " + query
            
            # Sections sécurité
            elif section_type.lower() in ["sécurité", "protection", "précautions", "avertissements"]:
                enriched_query = "Recherche exhaustive sur la sécurité, les protections et précautions: normes de sécurité, dispositifs de protection, avertissements, contre-indications, risques potentiels, mesures préventives. " + query
        
        return enriched_query
