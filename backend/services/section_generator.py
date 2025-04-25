"""
Service de génération de sections de fiches produit.
"""
import logging
import traceback
from typing import Dict, Any, List, Optional
import json
import os
from dotenv import load_dotenv

from services.ai_provider_service import AIProviderFactory
from services.vector_store_factory import VectorStoreFactory
from models.product_template import ProductSectionTemplate

# Configuration du logging
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Récupération de la clé API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class SectionGenerator:
    """
    Générateur de sections de fiches produit.
    """
    
    def __init__(self, openai_api_key: str = None, provider_type: str = "openai", model_name: str = None):
        """
        Initialise le générateur de sections.
        
        Args:
            openai_api_key: Clé API OpenAI
            provider_type: Type de fournisseur d'IA ('openai' ou 'gemini')
            model_name: Nom du modèle à utiliser
        """
        try:
            logger.debug("Initialisation du générateur de sections")
            
            # Initialisation du modèle LLM via le factory
            self.provider_type = provider_type
            self.model_name = model_name
            
            # Déterminer la clé API à utiliser
            api_key = None
            if provider_type.lower() == "openai":
                api_key = openai_api_key or OPENAI_API_KEY
            elif provider_type.lower() == "gemini":
                api_key = os.getenv("GOOGLE_API_KEY")
            
            # Création du fournisseur d'IA
            self.ai_provider = AIProviderFactory.get_provider(
                provider_type=provider_type,
                model_name=model_name,
                temperature=0.7,
                api_key=api_key
            )
            
            logger.debug(f"Fournisseur d'IA initialisé: {self.ai_provider.get_name()} {self.ai_provider.get_model_name()}")
            
            # Initialisation du service Vector Store (RAG)
            self.vector_store_service = None
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du générateur de sections: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def _initialize_vector_store_service(self):
        """
        Initialise le service Vector Store (RAG) si ce n'est pas déjà fait.
        """
        if self.vector_store_service is None:
            logger.debug("Initialisation du service Vector Store (RAG)")
            try:
                # Utiliser la factory pour créer le service Vector Store approprié
                self.vector_store_service = VectorStoreFactory.create_vector_store()
                logger.debug("Service Vector Store (RAG) initialisé avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du service Vector Store: {str(e)}")
                logger.error(traceback.format_exc())
                # Ne pas lever d'exception pour ne pas bloquer le reste du processus
                # Le service continuera sans RAG
                self.vector_store_service = None
    
    def _get_section_context(self, section: ProductSectionTemplate, product_info: Dict[str, Any], client_id: str) -> str:
        """
        Récupère le contexte spécifique à une section via RAG.
        
        Args:
            section: Template de la section
            product_info: Informations sur le produit
            client_id: ID du client
            
        Returns:
            str: Contexte formaté pour le prompt
        """
        if not client_id or not self.vector_store_service:
            return ""
        
        try:
            # Formater la requête RAG spécifique à la section
            product_name = product_info.get("name", "")
            product_category = product_info.get("category", "")
            product_description = product_info.get("description", "")
            keywords = ", ".join(product_info.get("keywords", [])[:3]) if product_info.get("keywords") else ""
            
            # Construire la requête RAG
            query = section.rag_query_template.format(
                product_name=product_name,
                product_category=product_category,
                product_description=product_description,
                keywords=keywords,
                section_name=section.name
            )
            
            logger.info(f"RAG_DEBUG: Requête RAG pour section '{section.name}': '{query}'")
            
            # Déterminer le nombre optimal de chunks selon le type de section
            section_type_lower = section.name.lower()
            
            # Sections techniques et détaillées nécessitent plus de contexte
            if section_type_lower in ["caractéristiques techniques", "spécifications", "fiche technique"]:
                top_k = 5
            # Sections d'installation et de maintenance nécessitent un contexte détaillé
            elif section_type_lower in ["installation", "mise en service", "entretien", "maintenance"]:
                top_k = 4
            # Sections générales comme l'introduction nécessitent moins de contexte spécifique
            elif section_type_lower in ["introduction", "présentation"]:
                top_k = 2
            # Valeur par défaut pour les autres sections
            else:
                top_k = 3
                
            logger.info(f"RAG_DEBUG: Utilisation de top_k={top_k} pour la section '{section.name}'")
            
            # Rechercher le contexte pertinent
            rag_result = self.vector_store_service.query_relevant_context(
                query=query,
                product_info=product_info,
                client_id=client_id,
                top_k=top_k,
                section_type=section.name  # Passer le nom de la section comme section_type
            )
            
            # Formater le contexte
            context_parts = []
            context_parts.append(f"CONTEXTE CLIENT PERTINENT POUR LA SECTION '{section.name.upper()}':")
            
            if not rag_result or not rag_result.chunks:
                context_parts.append("Aucune information client pertinente trouvée pour cette section.")
                return "\n".join(context_parts)
            
            # Log du nombre de chunks trouvés
            logger.info(f"RAG_DEBUG: {len(rag_result.chunks)} chunks trouvés pour la section '{section.name}'")
            
            # Formater chaque chunk
            for i, chunk in enumerate(rag_result.chunks):
                try:
                    # Extraire les métadonnées
                    title = chunk.metadata.get('title', 'Sans titre') if hasattr(chunk, 'metadata') else 'Sans titre'
                    source = chunk.metadata.get('source', 'Source inconnue') if hasattr(chunk, 'metadata') else 'Source inconnue'
                    
                    # Formater le contenu
                    content = chunk.page_content if hasattr(chunk, 'page_content') else str(chunk)
                    
                    # Ajouter au contexte
                    context_parts.append(f"Document {i+1}: {title} (Source: {source})")
                    if content and len(content) > 500:
                        content = content[:497] + "..."
                    context_parts.append(content)
                    context_parts.append("---")
                except Exception as e:
                    logger.error(f"RAG_DEBUG: Erreur lors du formatage du chunk {i}: {str(e)}")
                    context_parts.append(f"Document {i+1}: [Erreur de formatage]")
                    context_parts.append("---")
            
            formatted_context = "\n".join(context_parts)
            logger.info(f"RAG_DEBUG: Contexte formaté pour section '{section.name}': {len(formatted_context)} caractères")
            return formatted_context
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du contexte RAG pour la section '{section.name}': {str(e)}")
            return f"CONTEXTE CLIENT PERTINENT POUR LA SECTION '{section.name.upper()}':\nErreur lors de la récupération du contexte."
    
    def generate_section(self, 
                        section: ProductSectionTemplate, 
                        product_info: Dict[str, Any], 
                        tone_style: Dict[str, Any] = None,
                        client_id: str = None,
                        competitor_insights: Dict[str, Any] = None,
                        seo_guide_insights: Dict[str, Any] = None) -> str:
        """
        Génère le contenu d'une section spécifique.
        
        Args:
            section: Template de la section
            product_info: Informations sur le produit
            tone_style: Style et ton à utiliser
            client_id: ID du client pour le RAG
            competitor_insights: Insights sur les concurrents
            seo_guide_insights: Insights du guide SEO
            
        Returns:
            str: Contenu généré pour la section
        """
        try:
            logger.debug(f"Génération de la section '{section.name}'")
            
            # Initialiser le service Vector Store si nécessaire
            if client_id:
                self._initialize_vector_store_service()
            
            # Récupérer le contexte RAG spécifique à la section
            section_context = ""
            if client_id and self.vector_store_service:
                section_context = self._get_section_context(section, product_info, client_id)
            
            # Formatage des spécifications techniques
            tech_specs_formatted = ""
            if "technical_specs" in product_info:
                tech_specs = product_info.get("technical_specs", {})
                if isinstance(tech_specs, dict):
                    tech_specs_formatted = "\n".join([f"- {key}: {value}" for key, value in tech_specs.items()])
                elif isinstance(tech_specs, str):
                    tech_specs_formatted = tech_specs
            
            # Formatage des instructions de ton
            tone_instructions = ""
            if tone_style:
                tone_parts = []
                if "tone" in tone_style and tone_style["tone"]:
                    tone_parts.append(f"Ton: {tone_style['tone']}")
                if "style" in tone_style and tone_style["style"]:
                    tone_parts.append(f"Style: {tone_style['style']}")
                if "formality" in tone_style and tone_style["formality"]:
                    tone_parts.append(f"Formalité: {tone_style['formality']}")
                tone_instructions = ". ".join(tone_parts)
            
            # Formatage des instructions de persona cible
            persona_instructions = ""
            if tone_style and "persona_target" in tone_style and tone_style["persona_target"]:
                persona_instructions = f"Le public cible est: {tone_style['persona_target']}. Adapte le langage et les arguments pour ce public."
            
            # Formatage des insights concurrentiels
            competitor_info = ""
            if competitor_insights:
                competitor_parts = []
                for key, value in competitor_insights.items():
                    if isinstance(value, str) and value:
                        competitor_parts.append(f"{key}: {value}")
                competitor_info = "\n".join(competitor_parts)
            
            # Formatage des insights SEO
            seo_info = ""
            if seo_guide_insights:
                seo_parts = []
                for key, value in seo_guide_insights.items():
                    if isinstance(value, str) and value:
                        seo_parts.append(f"{key}: {value}")
                seo_info = "\n".join(seo_parts)
            
            # Variables pour le template de prompt
            prompt_vars = {
                "product_name": product_info.get("name", ""),
                "product_description": product_info.get("description", ""),
                "product_category": product_info.get("category", ""),
                "keywords": ", ".join(product_info.get("keywords", [])),
                "technical_specs": tech_specs_formatted,
                "tone_instructions": tone_instructions,
                "persona_instructions": persona_instructions,
                "competitor_insights": competitor_info,
                "seo_guide_info": seo_info,
                "section_context": section_context
            }
            
            # Formatage du prompt avec toutes les variables
            prompt_template = f"""
Tu es un expert en rédaction de fiches produit pour le e-commerce.

SECTION À GÉNÉRER: {section.name}

INSTRUCTIONS:
{section.prompt_template.format(**prompt_vars)}

INFORMATIONS SUR LE PRODUIT:
- Nom: {prompt_vars['product_name']}
- Catégorie: {prompt_vars['product_category']}
- Description: {prompt_vars['product_description']}
- Mots-clés: {prompt_vars['keywords']}

{prompt_vars['technical_specs'] if prompt_vars['technical_specs'] else ""}

STYLE ET TON:
{prompt_vars['tone_instructions']}
{prompt_vars['persona_instructions']}

{prompt_vars['section_context'] if prompt_vars['section_context'] else ""}

{'INSIGHTS CONCURRENTIELS:' + chr(10) + prompt_vars['competitor_insights'] if prompt_vars['competitor_insights'] else ''}

{'GUIDE SEO:' + chr(10) + prompt_vars['seo_guide_info'] if prompt_vars['seo_guide_info'] else ''}

IMPORTANT:
- Génère UNIQUEMENT le contenu de la section demandée, pas l'intégralité de la fiche produit.
- Ne pas inclure le titre de la section dans la réponse.
- Rédige un contenu factuel, précis et persuasif.
- Utilise un format adapté au web (paragraphes courts, listes à puces si pertinent).
"""
            
            # Log du prompt pour débogage
            logger.debug(f"Prompt pour la section '{section.name}':\n{prompt_template[:500]}...")
            
            # Création du message pour le modèle
            messages = [
                {"role": "user", "content": prompt_template}
            ]
            
            # Appel au modèle via le fournisseur d'IA
            response_content = self.ai_provider.generate_content(messages)
            
            # Nettoyage de la réponse
            response_content = response_content.strip()
            
            logger.debug(f"Section '{section.name}' générée avec succès: {len(response_content)} caractères")
            return response_content
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la section '{section.name}': {str(e)}")
            logger.error(traceback.format_exc())
            return f"[Erreur lors de la génération de la section {section.name}]"
