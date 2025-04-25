"""
Service de gestion des templates de fiches produit.
"""
import json
import os
import logging
from typing import List, Dict, Any, Optional
from models.product_template import ProductTemplate, ProductSectionTemplate, DEFAULT_PRODUCT_TEMPLATES

logger = logging.getLogger(__name__)

# Chemin vers le fichier de templates personnalisés
CUSTOM_TEMPLATES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'custom_product_templates.json')

class TemplateService:
    """
    Service de gestion des templates de fiches produit.
    """
    
    def __init__(self):
        """
        Initialise le service de templates.
        """
        # Charger les templates par défaut
        self.default_templates = DEFAULT_PRODUCT_TEMPLATES
        
        # Charger les templates personnalisés
        self.custom_templates = self._load_custom_templates()
        
        # Combiner les templates
        self.templates = self.default_templates + self.custom_templates
        
        logger.debug(f"Service de templates initialisé avec {len(self.templates)} templates ({len(self.default_templates)} par défaut, {len(self.custom_templates)} personnalisés)")
    
    def get_all_templates(self) -> List[ProductTemplate]:
        """
        Récupère tous les templates disponibles.
        
        Returns:
            List[ProductTemplate]: Liste des templates
        """
        return self.templates
    
    def get_template_by_id(self, template_id: str) -> Optional[ProductTemplate]:
        """
        Récupère un template par son ID.
        
        Args:
            template_id: ID du template à récupérer
            
        Returns:
            Optional[ProductTemplate]: Template trouvé ou None
        """
        for template in self.templates:
            if template.id == template_id:
                return template
        return None
    
    def get_default_template(self) -> ProductTemplate:
        """
        Récupère le template par défaut.
        
        Returns:
            ProductTemplate: Template par défaut
        """
        for template in self.templates:
            if template.is_default:
                return template
        
        # Si aucun template n'est marqué comme défaut, retourner le premier
        if self.templates:
            return self.templates[0]
        
        # Cas improbable: aucun template disponible
        raise ValueError("Aucun template disponible")
    
    def _load_custom_templates(self) -> List[ProductTemplate]:
        """
        Charge les templates personnalisés depuis le fichier JSON.
        
        Returns:
            List[ProductTemplate]: Liste des templates personnalisés
        """
        if not os.path.exists(CUSTOM_TEMPLATES_FILE):
            # Créer le fichier s'il n'existe pas
            os.makedirs(os.path.dirname(CUSTOM_TEMPLATES_FILE), exist_ok=True)
            with open(CUSTOM_TEMPLATES_FILE, 'w', encoding='utf-8') as f:
                json.dump({"templates": []}, f, ensure_ascii=False, indent=2)
            return []
        
        try:
            with open(CUSTOM_TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            custom_templates = []
            for template_data in data.get("templates", []):
                # Convertir les sections en objets ProductSectionTemplate
                sections = []
                for section_data in template_data.get("sections", []):
                    sections.append(ProductSectionTemplate(**section_data))
                
                # Créer le template
                template = ProductTemplate(
                    id=template_data["id"],
                    name=template_data["name"],
                    description=template_data["description"],
                    sections=sections,
                    is_default=template_data.get("is_default", False)
                )
                custom_templates.append(template)
            
            return custom_templates
        except Exception as e:
            logger.error(f"Erreur lors du chargement des templates personnalisés: {str(e)}")
            return []
    
    def save_custom_template(self, template: ProductTemplate) -> bool:
        """
        Sauvegarde un template personnalisé dans le fichier JSON.
        
        Args:
            template: Template à sauvegarder
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            # Charger les templates existants
            with open(CUSTOM_TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convertir le template en dictionnaire
            template_dict = template.dict()
            
            # Vérifier si le template existe déjà
            template_exists = False
            for i, existing_template in enumerate(data.get("templates", [])):
                if existing_template["id"] == template.id:
                    # Mettre à jour le template existant
                    data["templates"][i] = template_dict
                    template_exists = True
                    break
            
            # Ajouter le template s'il n'existe pas
            if not template_exists:
                if "templates" not in data:
                    data["templates"] = []
                data["templates"].append(template_dict)
            
            # Sauvegarder les templates
            with open(CUSTOM_TEMPLATES_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Recharger les templates
            self.custom_templates = self._load_custom_templates()
            self.templates = self.default_templates + self.custom_templates
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du template personnalisé: {str(e)}")
            return False
    
    def delete_custom_template(self, template_id: str) -> bool:
        """
        Supprime un template personnalisé du fichier JSON.
        
        Args:
            template_id: ID du template à supprimer
            
        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        try:
            # Charger les templates existants
            with open(CUSTOM_TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Filtrer les templates pour exclure celui à supprimer
            data["templates"] = [t for t in data.get("templates", []) if t["id"] != template_id]
            
            # Sauvegarder les templates
            with open(CUSTOM_TEMPLATES_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Recharger les templates
            self.custom_templates = self._load_custom_templates()
            self.templates = self.default_templates + self.custom_templates
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du template personnalisé: {str(e)}")
            return False
    
    def customize_template(self, base_template_id: str, section_ids: List[str]) -> ProductTemplate:
        """
        Crée un template personnalisé basé sur un template existant.
        
        Args:
            base_template_id: ID du template de base
            section_ids: Liste des IDs de sections à inclure
            
        Returns:
            ProductTemplate: Template personnalisé
        """
        base_template = self.get_template_by_id(base_template_id)
        if not base_template:
            base_template = self.get_default_template()
        
        # Filtrer les sections selon la liste fournie
        custom_sections = []
        for section in base_template.sections:
            if section.id in section_ids or section.required:
                custom_sections.append(section)
        
        # Trier les sections selon leur ordre d'origine
        custom_sections.sort(key=lambda x: x.order)
        
        # Créer le template personnalisé
        custom_template = ProductTemplate(
            id="custom",
            name="Template personnalisé",
            description=f"Template personnalisé basé sur {base_template.name}",
            sections=custom_sections,
            is_default=False
        )
        
        return custom_template
