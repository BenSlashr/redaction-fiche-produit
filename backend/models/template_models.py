"""
Modèles Pydantic pour les templates de fiches produit.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SectionInfo(BaseModel):
    """Informations sur une section de template."""
    id: str = Field(..., description="Identifiant unique de la section")
    name: str = Field(..., description="Nom de la section")
    description: str = Field(..., description="Description de la section")
    required: bool = Field(..., description="Indique si la section est obligatoire")
    default_enabled: bool = Field(..., description="Indique si la section est activée par défaut")
    order: int = Field(..., description="Ordre d'affichage de la section")


class TemplateInfo(BaseModel):
    """Informations sur un template de fiche produit."""
    id: str = Field(..., description="Identifiant unique du template")
    name: str = Field(..., description="Nom du template")
    description: str = Field(..., description="Description du template")
    is_default: bool = Field(..., description="Indique si c'est le template par défaut")
    sections: List[SectionInfo] = Field(..., description="Sections du template")


class TemplatesResponse(BaseModel):
    """Réponse contenant la liste des templates disponibles."""
    templates: List[TemplateInfo] = Field(..., description="Liste des templates disponibles")


class GeneratedSection(BaseModel):
    """Section générée d'une fiche produit."""
    id: str = Field(..., description="Identifiant de la section")
    name: str = Field(..., description="Nom de la section")
    content: str = Field(..., description="Contenu généré pour la section")


class SectionedProductDescription(BaseModel):
    """Description de produit générée par sections."""
    template: Dict[str, str] = Field(..., description="Informations sur le template utilisé")
    sections: List[GeneratedSection] = Field(..., description="Sections générées")


class SectionedProductResponse(BaseModel):
    """Réponse contenant une description de produit générée par sections."""
    product_description: SectionedProductDescription = Field(..., description="Description du produit par sections")
    metadata: Dict[str, Any] = Field(..., description="Métadonnées sur la génération")


class SectionedProductRequest(BaseModel):
    """Requête pour générer une description de produit par sections."""
    product_info: Dict[str, Any] = Field(..., description="Informations sur le produit")
    tone_style: Dict[str, Any] = Field(..., description="Style et ton à utiliser")
    template_id: str = Field("standard", description="ID du template à utiliser")
    sections: Optional[List[str]] = Field(None, description="IDs des sections à inclure (si personnalisé)")
    use_rag: bool = Field(False, description="Utiliser le RAG pour enrichir la génération")
    client_id: Optional[str] = Field(None, description="ID du client pour le RAG")
    seo_optimization: bool = Field(False, description="Activer l'optimisation SEO")
    competitor_analysis: bool = Field(False, description="Activer l'analyse des concurrents")
    competitor_insights: Optional[Dict[str, Any]] = Field(None, description="Insights concurrentiels")
    use_seo_guide: bool = Field(False, description="Utiliser le guide SEO")
    seo_guide_insights: Optional[Dict[str, Any]] = Field(None, description="Insights du guide SEO")
    ai_provider: Optional[Dict[str, str]] = Field(None, description="Fournisseur d'IA à utiliser")


class SectionTemplateUpdate(BaseModel):
    """Modèle pour la mise à jour d'une section de template."""
    id: str = Field(..., description="Identifiant unique de la section")
    name: str = Field(..., description="Nom de la section")
    description: str = Field(..., description="Description de la section")
    required: bool = Field(..., description="Indique si la section est obligatoire")
    default_enabled: bool = Field(..., description="Indique si la section est activée par défaut")
    order: int = Field(..., description="Ordre d'affichage de la section")
    rag_query_template: str = Field(..., description="Template de requête RAG spécifique à cette section")
    prompt_template: str = Field(..., description="Template de prompt spécifique à cette section")


class TemplateCreate(BaseModel):
    """Modèle pour la création d'un nouveau template."""
    name: str = Field(..., description="Nom du template")
    description: str = Field(..., description="Description du template")
    sections: List[SectionTemplateUpdate] = Field(..., description="Sections du template")
    is_default: bool = Field(False, description="Indique si c'est le template par défaut")


class TemplateUpdate(BaseModel):
    """Modèle pour la mise à jour d'un template existant."""
    name: str = Field(..., description="Nom du template")
    description: str = Field(..., description="Description du template")
    sections: List[SectionTemplateUpdate] = Field(..., description="Sections du template")
    is_default: bool = Field(False, description="Indique si c'est le template par défaut")


class TemplateResponse(BaseModel):
    """Réponse contenant un template."""
    id: str = Field(..., description="Identifiant unique du template")
    name: str = Field(..., description="Nom du template")
    description: str = Field(..., description="Description du template")
    sections: List[SectionTemplateUpdate] = Field(..., description="Sections du template")
    is_default: bool = Field(..., description="Indique si c'est le template par défaut")
    is_custom: bool = Field(..., description="Indique si c'est un template personnalisé")
