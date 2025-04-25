"""
Routes pour la gestion des templates de fiches produit.
"""
import logging
import traceback
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from uuid import uuid4

from services.product_description_service import ProductDescriptionService
from services.template_service import TemplateService
from models.template_models import (
    TemplatesResponse, 
    SectionedProductRequest, 
    SectionedProductResponse,
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse
)

# Configuration du logging
logger = logging.getLogger(__name__)

# Création du router
router = APIRouter(prefix="/templates", tags=["Templates"])

# Dépendances pour obtenir les services nécessaires
def get_product_description_service(
    provider_type: str = "openai", 
    model_name: str = None
) -> ProductDescriptionService:
    """
    Retourne une instance du service de génération de fiches produit.
    
    Args:
        provider_type: Type de fournisseur d'IA ('openai' ou 'gemini')
        model_name: Nom du modèle à utiliser
        
    Returns:
        ProductDescriptionService: Service de génération de fiches produit
    """
    try:
        return ProductDescriptionService(
            provider_type=provider_type,
            model_name=model_name
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du service de génération: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'initialisation du service de génération: {str(e)}"
        )


def get_template_service() -> TemplateService:
    """
    Retourne une instance du service de gestion des templates.
    
    Returns:
        TemplateService: Service de gestion des templates
    """
    try:
        return TemplateService()
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du service de templates: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'initialisation du service de templates: {str(e)}"
        )

@router.get("/", response_model=TemplatesResponse)
async def get_templates(
    service: ProductDescriptionService = Depends(get_product_description_service)
) -> TemplatesResponse:
    """
    Récupère la liste des templates disponibles.
    
    Returns:
        TemplatesResponse: Liste des templates disponibles
    """
    try:
        templates = service.get_available_templates()
        return TemplatesResponse(templates=templates)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des templates: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des templates: {str(e)}"
        )

@router.post("/generate", response_model=SectionedProductResponse)
async def generate_sectioned_product(
    request: SectionedProductRequest,
    service: ProductDescriptionService = Depends(get_product_description_service)
) -> SectionedProductResponse:
    """
    Génère une fiche produit par sections.
    
    Args:
        request: Informations sur le produit et options de génération
        
    Returns:
        SectionedProductResponse: Fiche produit générée par sections
    """
    try:
        logger.info("Demande de génération de fiche produit par sections")
        
        # Si un fournisseur d'IA spécifique est demandé, l'utiliser
        if request.ai_provider:
            provider_type = request.ai_provider.get("provider_type")
            model_name = request.ai_provider.get("model_name")
            
            if provider_type:
                service = get_product_description_service(
                    provider_type=provider_type,
                    model_name=model_name
                )
        
        # Génération de la fiche produit
        result = service.generate_product_description(request.dict())
        
        logger.info("Génération de fiche produit par sections terminée avec succès")
        return SectionedProductResponse(product_description=result, metadata={})
    except Exception as e:
        logger.error(f"Erreur lors de la génération de fiche produit par sections: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de fiche produit par sections: {str(e)}"
        )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service)
) -> TemplateResponse:
    """
    Récupère un template spécifique.
    
    Args:
        template_id: ID du template à récupérer
        
    Returns:
        TemplateResponse: Template demandé
    """
    try:
        template = template_service.get_template_by_id(template_id)
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"Template avec l'ID {template_id} non trouvé"
            )
        
        # Déterminer si c'est un template personnalisé
        is_custom = template_id not in [t.id for t in template_service.default_templates]
        
        # Convertir en réponse
        sections = []
        for section in template.sections:
            sections.append({
                "id": section.id,
                "name": section.name,
                "description": section.description,
                "required": section.required,
                "default_enabled": section.default_enabled,
                "order": section.order,
                "rag_query_template": section.rag_query_template,
                "prompt_template": section.prompt_template
            })
        
        return TemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            sections=sections,
            is_default=template.is_default,
            is_custom=is_custom
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du template: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du template: {str(e)}"
        )


@router.post("/", response_model=TemplateResponse)
async def create_template(
    template: TemplateCreate,
    template_service: TemplateService = Depends(get_template_service)
) -> TemplateResponse:
    """
    Crée un nouveau template personnalisé.
    
    Args:
        template: Données du nouveau template
        
    Returns:
        TemplateResponse: Template créé
    """
    try:
        # Générer un ID unique pour le nouveau template
        template_id = f"custom_{str(uuid4())[:8]}"
        
        # Créer le template
        from models.product_template import ProductTemplate, ProductSectionTemplate
        
        sections = []
        for section_data in template.sections:
            sections.append(ProductSectionTemplate(
                id=section_data.id,
                name=section_data.name,
                description=section_data.description,
                required=section_data.required,
                default_enabled=section_data.default_enabled,
                order=section_data.order,
                rag_query_template=section_data.rag_query_template,
                prompt_template=section_data.prompt_template
            ))
        
        new_template = ProductTemplate(
            id=template_id,
            name=template.name,
            description=template.description,
            sections=sections,
            is_default=template.is_default
        )
        
        # Sauvegarder le template
        success = template_service.save_custom_template(new_template)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de la sauvegarde du template"
            )
        
        # Retourner le template créé
        return TemplateResponse(
            id=template_id,
            name=template.name,
            description=template.description,
            sections=template.sections,
            is_default=template.is_default,
            is_custom=True
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la création du template: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la création du template: {str(e)}"
        )


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template: TemplateUpdate,
    template_service: TemplateService = Depends(get_template_service)
) -> TemplateResponse:
    """
    Met à jour un template existant.
    
    Args:
        template_id: ID du template à mettre à jour
        template: Nouvelles données du template
        
    Returns:
        TemplateResponse: Template mis à jour
    """
    try:
        # Vérifier si le template existe
        existing_template = template_service.get_template_by_id(template_id)
        if not existing_template:
            raise HTTPException(
                status_code=404,
                detail=f"Template avec l'ID {template_id} non trouvé"
            )
        
        # Vérifier si c'est un template personnalisé
        is_custom = template_id not in [t.id for t in template_service.default_templates]
        if not is_custom:
            raise HTTPException(
                status_code=403,
                detail="Impossible de modifier un template par défaut"
            )
        
        # Mettre à jour le template
        from models.product_template import ProductTemplate, ProductSectionTemplate
        
        sections = []
        for section_data in template.sections:
            sections.append(ProductSectionTemplate(
                id=section_data.id,
                name=section_data.name,
                description=section_data.description,
                required=section_data.required,
                default_enabled=section_data.default_enabled,
                order=section_data.order,
                rag_query_template=section_data.rag_query_template,
                prompt_template=section_data.prompt_template
            ))
        
        updated_template = ProductTemplate(
            id=template_id,
            name=template.name,
            description=template.description,
            sections=sections,
            is_default=template.is_default
        )
        
        # Sauvegarder le template
        success = template_service.save_custom_template(updated_template)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de la sauvegarde du template"
            )
        
        # Retourner le template mis à jour
        return TemplateResponse(
            id=template_id,
            name=template.name,
            description=template.description,
            sections=template.sections,
            is_default=template.is_default,
            is_custom=True
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du template: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la mise à jour du template: {str(e)}"
        )


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    template_service: TemplateService = Depends(get_template_service)
) -> Dict[str, bool]:
    """
    Supprime un template personnalisé.
    
    Args:
        template_id: ID du template à supprimer
        
    Returns:
        Dict[str, bool]: Résultat de la suppression
    """
    try:
        # Vérifier si le template existe
        existing_template = template_service.get_template_by_id(template_id)
        if not existing_template:
            raise HTTPException(
                status_code=404,
                detail=f"Template avec l'ID {template_id} non trouvé"
            )
        
        # Vérifier si c'est un template personnalisé
        is_custom = template_id not in [t.id for t in template_service.default_templates]
        if not is_custom:
            raise HTTPException(
                status_code=403,
                detail="Impossible de supprimer un template par défaut"
            )
        
        # Supprimer le template
        success = template_service.delete_custom_template(template_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de la suppression du template"
            )
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du template: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression du template: {str(e)}"
        )
