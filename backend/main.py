from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import logging
import traceback
import uuid
from dotenv import load_dotenv
from services.langchain_service import ProductDescriptionGenerator
from services.tone_analyzer import ToneAnalyzer, ToneLibrary
from services.competitor_analyzer import CompetitorAnalyzer
from services.thot_seo_service import ThotSeoService
from services.self_improving_chain import SelfImprovingChain
from services.prompt_manager import PromptManager
from services.specs_extractor import SpecsExtractor
from services.batch_processor import BatchProcessor
from services.ai_provider_service import AIProviderFactory
from services.vector_store_factory import VectorStoreFactory
from services.document_processor import DocumentProcessor
from services.file_processor import FileProcessor
from services.product_description_service import ProductDescriptionService
from routes.template_routes import router as template_router
import json

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Vérification des clés API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VALUESERP_API_KEY = os.getenv("VALUESERP_API_KEY")
THOT_API_KEY = os.getenv("THOT_API_KEY")

if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
    logger.error("⚠️ Attention: OPENAI_API_KEY n'est pas configurée correctement dans le fichier .env")

if not VALUESERP_API_KEY or VALUESERP_API_KEY == "your_valueserp_api_key_here":
    logger.error("⚠️ Attention: VALUESERP_API_KEY n'est pas configurée correctement dans le fichier .env")

if not THOT_API_KEY or THOT_API_KEY == "your_thot_api_key_here":
    logger.error("⚠️ Attention: THOT_API_KEY n'est pas configurée correctement dans le fichier .env")

logger.info(f"OPENAI_API_KEY configurée: {'Oui' if OPENAI_API_KEY else 'Non'}")
logger.info(f"VALUESERP_API_KEY configurée: {'Oui' if VALUESERP_API_KEY else 'Non'}")
logger.info(f"THOT_API_KEY configurée: {'Oui' if THOT_API_KEY else 'Non'}")

app = FastAPI(
    title="API de Génération de Fiches Produit",
    description="API pour générer des fiches produit enrichies par IA",
    version="0.1.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8045", "http://51.75.124.6:8045"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montage des routes
app.include_router(template_router, prefix="/templates")

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les origines exactes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes de templates
app.include_router(template_router)

@app.get("/")
async def health_check():
    """Endpoint de santé pour vérifier que l'application est en cours d'exécution."""
    return {"status": "ok", "message": "API de génération de fiches produit opérationnelle"}

# Modèles de données
class ProductInfo(BaseModel):
    name: str
    description: str
    technical_specs: Optional[dict] = None
    category: Optional[str] = None
    keywords: Optional[List[str]] = None

class ToneStyle(BaseModel):
    brand_name: Optional[str] = None
    tone_description: Optional[str] = None
    tone_example: Optional[str] = None
    persona_target: Optional[str] = None  # Persona cible (lecteur)
    predefined_tone_id: Optional[str] = None

class ProductRequest(BaseModel):
    product_info: ProductInfo
    tone_style: Optional[ToneStyle] = None
    seo_optimization: bool = True
    competitor_analysis: bool = False

class ProductResponse(BaseModel):
    product_description: str
    seo_suggestions: Optional[List[str]] = None
    competitor_insights: Optional[List[str]] = None
    ai_provider: Optional[Dict[str, Any]] = None

class ToneAnalysisRequest(BaseModel):
    text: str

class ToneCharacteristic(BaseModel):
    name: str
    description: str

class ToneAnalysisResponse(BaseModel):
    tone_description: str
    tone_characteristics: List[str]
    writing_style: str
    vocabulary_level: str
    sentence_structure: str

class PredefinedToneResponse(BaseModel):
    id: str
    name: str
    description: str
    characteristics: List[str]
    example: str

class CompetitorAnalysisRequest(BaseModel):
    product_name: str
    product_category: str
    search_query: Optional[str] = None
    debug_mode: bool = False

class CompetitorAnalysisResponse(BaseModel):
    key_features: List[str]
    unique_selling_points: List[str]
    common_specifications: List[str]
    content_structure: str
    seo_keywords: List[str]

class SeoGuideRequest(BaseModel):
    keywords: str
    debug_mode: bool = False

class SeoGuideResponse(BaseModel):
    required_keywords: List[Dict[str, Any]]
    complementary_keywords: List[Dict[str, Any]]
    expressions: List[str]
    questions: List[str]
    word_count: int
    target_score: int
    max_overoptimization: int
    competition: List[Dict[str, Any]]

class ProductDescriptionRequest(BaseModel):
    product_info: Dict[str, Any]
    tone_style: Dict[str, str]
    seo_optimization: bool = False
    competitor_analysis: bool = False
    competitor_insights: Optional[Dict[str, Any]] = None
    use_seo_guide: bool = False
    seo_guide_keywords: Optional[str] = None
    seo_guide_insights: Optional[Dict[str, Any]] = None
    auto_improve: bool = False
    ai_provider: Optional[Dict[str, str]] = None

class SelfImprovingResponse(BaseModel):
    original_description: str
    evaluation: Dict[str, Any]
    improved_description: str
    verification: str

class PromptUpdateRequest(BaseModel):
    name: str
    template: str

class PromptResponse(BaseModel):
    id: str
    name: str
    template: str

class AllPromptsResponse(BaseModel):
    prompts: Dict[str, PromptResponse]

class ExtractSpecsRequest(BaseModel):
    text: str

class ExtractSpecsResponse(BaseModel):
    specs: List[Dict[str, str]]

class BatchProductRequest(BaseModel):
    products: List[Dict[str, Any]] = Field(..., description="Liste des informations de produits")
    tone_style: Dict[str, Any] = Field(..., description="Style et ton à utiliser")
    seo_optimization: bool = Field(True, description="Activer l'optimisation SEO")
    use_auto_improvement: bool = Field(False, description="Utiliser la chaîne d'auto-amélioration")
    competitor_analysis: bool = Field(False, description="Activer l'analyse des concurrents")
    use_seo_guide: bool = Field(False, description="Utiliser le guide SEO")

class AIProviderModel(BaseModel):
    id: str
    name: str
    description: str

class AIProviderInfo(BaseModel):
    name: str
    models: List[AIProviderModel]

class AIProvidersResponse(BaseModel):
    providers: List[AIProviderInfo]

# Modèles pour le RAG (Retrieval-Augmented Generation)
class ClientDocumentUpload(BaseModel):
    client_id: str = Field(..., description="Identifiant du client")
    title: str = Field(..., description="Titre du document")
    content: str = Field(..., description="Contenu textuel du document")
    source_type: str = Field(..., description="Type de source (catalogue, fiche technique, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Métadonnées additionnelles")

class ClientDocumentResponse(BaseModel):
    document_id: str = Field(..., description="Identifiant unique du document")
    client_id: str = Field(..., description="Identifiant du client")
    title: str = Field(..., description="Titre du document")
    source_type: str = Field(..., description="Type de source")
    chunk_count: int = Field(..., description="Nombre de chunks créés")
    status: str = Field(..., description="Statut de l'indexation")

class ClientDataSummaryResponse(BaseModel):
    client_id: str = Field(..., description="Identifiant du client")
    document_count: int = Field(..., description="Nombre total de documents")
    document_types: Dict[str, int] = Field(..., description="Nombre de documents par type")
    documents: List[Dict[str, Any]] = Field(..., description="Liste des documents avec métadonnées de base")

class RAGProductDescriptionRequest(BaseModel):
    product_info: Dict[str, Any] = Field(..., description="Informations sur le produit")
    tone_style: Dict[str, str] = Field(..., description="Style et ton à utiliser")
    seo_optimization: bool = Field(False, description="Activer l'optimisation SEO")
    competitor_analysis: bool = Field(False, description="Activer l'analyse des concurrents")
    competitor_insights: Optional[Dict[str, Any]] = Field(None, description="Insights concurrentiels")
    use_seo_guide: bool = Field(False, description="Utiliser le guide SEO")
    seo_guide_keywords: Optional[str] = Field(None, description="Mots-clés pour le guide SEO")
    seo_guide_insights: Optional[Dict[str, Any]] = Field(None, description="Insights du guide SEO")
    auto_improve: bool = Field(False, description="Utiliser la chaîne d'auto-amélioration")
    ai_provider: Optional[Dict[str, str]] = Field(None, description="Fournisseur d'IA à utiliser")
    use_rag: bool = Field(True, description="Utiliser le RAG pour enrichir la génération")
    client_id: str = Field(..., description="ID du client pour le RAG")
    client_data_ids: Optional[List[str]] = Field(None, description="IDs des documents client à utiliser")

# Dépendances
def get_product_generator(
    provider_type: str = "openai", 
    model_name: str = None
) -> ProductDescriptionGenerator:
    """
    Retourne une instance du générateur de descriptions de produits.
    
    Args:
        provider_type: Type de fournisseur d'IA ('openai' ou 'gemini')
        model_name: Nom du modèle à utiliser
    """
    logger.debug(f"Création d'une instance de ProductDescriptionGenerator avec {provider_type} {model_name}")
    try:
        return ProductDescriptionGenerator(
            provider_type=provider_type,
            model_name=model_name
        )
    except Exception as e:
        logger.error(f"Erreur lors de la création du générateur de descriptions: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def get_tone_analyzer():
    logger.debug("Initialisation de l'analyseur de ton")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="Clé API OpenAI non configurée")
    return ToneAnalyzer(openai_api_key=openai_api_key)

def get_tone_library():
    logger.debug("Initialisation de la bibliothèque de tons")
    return ToneLibrary()

def get_competitor_analyzer():
    logger.debug("Initialisation de l'analyseur de concurrents")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    valueserp_api_key = os.getenv("VALUESERP_API_KEY")
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="Clé API OpenAI non configurée")
    if not valueserp_api_key:
        raise HTTPException(status_code=500, detail="Clé API ValueSERP non configurée")
    return CompetitorAnalyzer(valueserp_api_key=valueserp_api_key, openai_api_key=openai_api_key)

def get_thot_seo_service():
    logger.debug("Initialisation du service THOT SEO")
    thot_api_key = os.getenv("THOT_API_KEY")
    if not thot_api_key:
        raise HTTPException(status_code=500, detail="Clé API THOT SEO non configurée")
    return ThotSeoService()

def get_self_improving_chain():
    logger.debug("Initialisation de la chaîne d'auto-amélioration")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="Clé API OpenAI non configurée")
    return SelfImprovingChain(openai_api_key=openai_api_key)

def get_prompt_manager():
    logger.debug("Initialisation du gestionnaire de prompts")
    return PromptManager()

def get_batch_processor():
    """
    Retourne une instance du processeur par lots.
    """
    try:
        # Création des dépendances
        product_generator = get_product_generator()
        self_improving_chain = get_self_improving_chain()
        competitor_analyzer = get_competitor_analyzer()
        thot_seo_service = get_thot_seo_service()
        
        # Création du processeur par lots
        batch_processor = BatchProcessor(
            product_generator=product_generator,
            self_improving_chain=self_improving_chain,
            competitor_analyzer=competitor_analyzer,
            thot_seo_service=thot_seo_service
        )
        
        return batch_processor
    except Exception as e:
        logger.error(f"Erreur lors de la création du processeur par lots: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du processeur par lots: {str(e)}")

def get_vector_store_service():
    """
    Retourne une instance du service Vector Store (RAG) en utilisant la factory.
    """
    try:
        # Utiliser la factory pour créer le service Vector Store approprié
        # selon la configuration dans le fichier .env
        vector_store_service = VectorStoreFactory.create_vector_store()
        
        return vector_store_service
    except Exception as e:
        logger.error(f"Erreur lors de la création du service Vector Store: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du service Vector Store: {str(e)}")

def get_document_processor():
    """
    Retourne une instance du processeur de documents.
    """
    try:
        # Création du processeur de documents
        document_processor = DocumentProcessor()
        
        return document_processor
    except Exception as e:
        logger.error(f"Erreur lors de la création du processeur de documents: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du processeur de documents: {str(e)}")

# Routes API
@app.get("/")
async def read_root():
    logger.info("Accès à la route racine")
    return {"message": "Bienvenue sur l'API de Génération de Fiches Produit"}

@app.post("/generate-product-description", response_model=ProductResponse)
async def generate_product_description(
    request: ProductDescriptionRequest,
    thot_seo_service: ThotSeoService = Depends(get_thot_seo_service)
):
    """
    Génère une description de produit enrichie à partir des informations fournies.
    """
    try:
        logger.info("Demande de génération de description de produit reçue")
        
        # Récupérer les informations du fournisseur d'IA
        provider_type = "openai"  # Par défaut
        model_name = None
        
        if request.ai_provider:
            provider_type = request.ai_provider.get("provider_type", "openai")
            model_name = request.ai_provider.get("model_name")
        
        # Créer une instance du générateur avec le fournisseur d'IA spécifié
        product_generator = get_product_generator(provider_type, model_name)
        
        # Si l'optimisation SEO est activée et que des mots-clés sont fournis, récupérer le guide SEO
        if request.use_seo_guide and request.seo_guide_keywords:
            logger.info(f"Récupération du guide SEO pour les mots-clés: {request.seo_guide_keywords}")
            try:
                seo_guide = thot_seo_service.get_seo_guide(request.seo_guide_keywords)
                request.seo_guide_insights = seo_guide
                logger.info("Guide SEO récupéré avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de la récupération du guide SEO: {str(e)}")
                logger.error(traceback.format_exc())
                # On continue sans le guide SEO
                request.seo_guide_insights = None
        
        # Génération de la description
        logger.info("Génération de la description de produit")
        response = product_generator.generate_product_description(request.dict())
        logger.info("Description de produit générée avec succès")
        
        return ProductResponse(
            product_description=response.get("product_description", ""),
            seo_suggestions=response.get("seo_suggestions", []),
            competitor_insights=response.get("competitor_insights", []),
            ai_provider=response.get("ai_provider", {})
        )
    
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la description de produit: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.post("/analyze-tone", response_model=ToneAnalysisResponse)
async def analyze_tone(
    request: ToneAnalysisRequest,
    tone_analyzer: ToneAnalyzer = Depends(get_tone_analyzer)
):
    """
    Analyse le ton éditorial d'un exemple de texte.
    """
    try:
        logger.info("Demande d'analyse de ton")
        logger.debug(f"Texte à analyser (premiers 100 caractères): {request.text[:100]}...")
        
        result = tone_analyzer.analyze_tone(request.text)
        logger.debug(f"Résultat de l'analyse: {result}")
        
        response = ToneAnalysisResponse(
            tone_description=result["tone_description"],
            tone_characteristics=result["tone_characteristics"],
            writing_style=result["writing_style"],
            vocabulary_level=result["vocabulary_level"],
            sentence_structure=result["sentence_structure"]
        )
        logger.info("Analyse de ton terminée avec succès")
        return response
    except Exception as e:
        error_msg = f"Erreur lors de l'analyse du ton: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/predefined-tones", response_model=Dict[str, PredefinedToneResponse])
async def get_predefined_tones(
    tone_library: ToneLibrary = Depends(get_tone_library)
):
    """
    Récupère la liste des tons prédéfinis disponibles.
    """
    try:
        logger.info("Demande de récupération des tons prédéfinis")
        
        predefined_tones = tone_library.get_all_tones()
        
        # Conversion en format de réponse
        response = {}
        for tone_id, tone_data in predefined_tones.items():
            response[tone_id] = PredefinedToneResponse(
                id=tone_id,
                name=tone_data["name"],
                description=tone_data["description"],
                characteristics=tone_data["characteristics"],
                example=tone_data["example"]
            )
        
        logger.info(f"Retour de {len(response)} tons prédéfinis")
        return response
    except Exception as e:
        error_msg = f"Erreur lors de la récupération des tons prédéfinis: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/predefined-tone/{tone_id}", response_model=PredefinedToneResponse)
async def get_predefined_tone(
    tone_id: str,
    tone_library: ToneLibrary = Depends(get_tone_library)
):
    """
    Récupère les informations d'un ton prédéfini spécifique.
    """
    try:
        logger.info(f"Demande de récupération du ton prédéfini: {tone_id}")
        
        tone_data = tone_library.get_tone(tone_id)
        
        if not tone_data:
            logger.warning(f"Ton prédéfini non trouvé: {tone_id}")
            raise HTTPException(status_code=404, detail=f"Ton prédéfini non trouvé: {tone_id}")
        
        response = PredefinedToneResponse(
            id=tone_id,
            name=tone_data["name"],
            description=tone_data["description"],
            characteristics=tone_data["characteristics"],
            example=tone_data["example"]
        )
        
        logger.info(f"Ton prédéfini récupéré: {tone_data['name']}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Erreur lors de la récupération du ton prédéfini: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/analyze-competitors", response_model=CompetitorAnalysisResponse)
async def analyze_competitors(
    request: CompetitorAnalysisRequest,
    competitor_analyzer: CompetitorAnalyzer = Depends(get_competitor_analyzer)
):
    """
    Analyse les concurrents pour un produit donné.
    
    Args:
        request: Informations sur le produit et la requête de recherche
        
    Returns:
        CompetitorAnalysisResponse: Résultats de l'analyse des concurrents
    """
    logger.info(f"Demande d'analyse des concurrents pour: {request.product_name}")
    
    # Configurer le niveau de log en fonction du mode debug
    if request.debug_mode:
        logger.setLevel(logging.DEBUG)
        logger.info("Mode debug activé pour cette analyse")
    else:
        logger.setLevel(logging.INFO)
    
    try:
        # Analyse des concurrents
        result = competitor_analyzer.analyze_competitors(
            product_name=request.product_name,
            product_category=request.product_category,
            search_query=request.search_query
        )
        
        logger.info("Analyse des concurrents terminée avec succès")
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des concurrents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse des concurrents: {str(e)}")
    finally:
        # Rétablir le niveau de log par défaut
        logger.setLevel(logging.DEBUG)

@app.post("/get-seo-guide", response_model=SeoGuideResponse)
async def get_seo_guide(
    request: SeoGuideRequest,
    thot_seo_service: ThotSeoService = Depends(get_thot_seo_service)
):
    """
    Récupère un guide SEO pour un produit donné.
    
    Args:
        request: Informations sur le produit et la requête de recherche
        
    Returns:
        SeoGuideResponse: Résultats du guide SEO
    """
    logger.info(f"Demande de récupération du guide SEO pour: {request.keywords}")
    
    # Configurer le niveau de log en fonction du mode debug
    if request.debug_mode:
        logger.setLevel(logging.DEBUG)
        logger.info("Mode debug activé pour cette analyse")
    else:
        logger.setLevel(logging.INFO)
    
    try:
        # Récupération du guide SEO
        raw_data = thot_seo_service.get_seo_guide(
            keywords=request.keywords,
            debug_mode=request.debug_mode
        )
        
        if not raw_data:
            raise HTTPException(status_code=500, detail="Impossible de récupérer le guide SEO")
            
        # Extraction des insights SEO
        insights = thot_seo_service.extract_seo_insights(raw_data)
        
        logger.info("Récupération du guide SEO terminée avec succès")
        return insights
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du guide SEO: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du guide SEO: {str(e)}")
    finally:
        # Rétablir le niveau de log par défaut
        logger.setLevel(logging.DEBUG)

@app.post("/generate-improved-description", response_model=SelfImprovingResponse)
async def generate_improved_description(
    request: ProductDescriptionRequest,
    self_improving_chain: SelfImprovingChain = Depends(get_self_improving_chain),
    thot_seo_service: ThotSeoService = Depends(get_thot_seo_service)
):
    """
    Génère une description de produit améliorée en utilisant une chaîne d'auto-amélioration.
    
    Args:
        request: Informations sur le produit et options de génération
        
    Returns:
        SelfImprovingResponse: Description originale, évaluation, description améliorée et vérification
    """
    try:
        logger.info(f"Demande de génération améliorée pour le produit: {request.product_info.get('name', 'Inconnu')}")
        logger.debug(f"Données de la requête: {request.model_dump_json()}")
        
        # Si l'option de guide SEO est activée mais que les insights ne sont pas fournis
        if request.use_seo_guide and request.seo_guide_keywords and not request.seo_guide_insights:
            logger.info(f"Récupération du guide SEO pour les mots-clés: {request.seo_guide_keywords}")
            
            # Récupération du guide SEO
            raw_data = thot_seo_service.get_seo_guide(
                keywords=request.seo_guide_keywords,
                debug_mode=True  # Activer le mode debug pour le guide SEO
            )
            
            if raw_data:
                # Extraction des insights SEO
                seo_insights = thot_seo_service.extract_seo_insights(raw_data)
                
                # Ajout des insights SEO à la requête
                request.seo_guide_insights = seo_insights
                logger.info("Guide SEO récupéré avec succès")
            else:
                logger.warning("Impossible de récupérer le guide SEO")
        
        # Conversion du modèle Pydantic en dictionnaire
        request_data = request.model_dump()
        logger.debug(f"Requête convertie en dict: {request_data}")
        
        # Génération de la description améliorée via la chaîne d'auto-amélioration
        logger.info("Appel de la chaîne d'auto-amélioration")
        result = self_improving_chain.generate_improved_description(request_data)
        logger.debug(f"Résultat de la génération améliorée: {json.dumps(result, ensure_ascii=False)[:500]}...")
        
        response = SelfImprovingResponse(
            original_description=result["original_description"],
            evaluation=result["evaluation"],
            improved_description=result["improved_description"],
            verification=result["verification"]
        )
        
        logger.info("Génération améliorée terminée avec succès")
        return response
        
    except Exception as e:
        error_msg = f"Erreur lors de la génération améliorée: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/prompts", response_model=AllPromptsResponse)
async def get_all_prompts(
    prompt_manager: PromptManager = Depends(get_prompt_manager)
):
    """
    Récupère tous les prompts disponibles.
    
    Returns:
        AllPromptsResponse: Tous les prompts disponibles
    """
    try:
        logger.info("Demande de récupération de tous les prompts")
        
        # Récupération de tous les prompts
        prompts_data = prompt_manager.get_all_prompts()
        
        # Conversion en format de réponse
        prompts_response = {}
        for prompt_id, prompt_data in prompts_data.items():
            prompts_response[prompt_id] = PromptResponse(
                id=prompt_id,
                name=prompt_data["name"],
                template=prompt_data["template"]
            )
        
        logger.info(f"Récupération de {len(prompts_response)} prompts terminée avec succès")
        return AllPromptsResponse(prompts=prompts_response)
        
    except Exception as e:
        error_msg = f"Erreur lors de la récupération des prompts: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/prompts/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: str,
    prompt_manager: PromptManager = Depends(get_prompt_manager)
):
    """
    Récupère un prompt spécifique.
    
    Args:
        prompt_id: Identifiant du prompt
        
    Returns:
        PromptResponse: Le prompt demandé
    """
    try:
        logger.info(f"Demande de récupération du prompt: {prompt_id}")
        
        # Récupération du prompt
        prompt_data = prompt_manager.get_prompt(prompt_id)
        
        if not prompt_data:
            logger.warning(f"Prompt non trouvé: {prompt_id}")
            raise HTTPException(status_code=404, detail=f"Prompt non trouvé: {prompt_id}")
        
        response = PromptResponse(
            id=prompt_id,
            name=prompt_data["name"],
            template=prompt_data["template"]
        )
        
        logger.info(f"Récupération du prompt {prompt_id} terminée avec succès")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Erreur lors de la récupération du prompt: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

@app.put("/prompts/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: str,
    request: PromptUpdateRequest,
    prompt_manager: PromptManager = Depends(get_prompt_manager)
):
    """
    Met à jour un prompt existant.
    
    Args:
        prompt_id: Identifiant du prompt
        request: Nouvelles données du prompt
        
    Returns:
        PromptResponse: Le prompt mis à jour
    """
    try:
        logger.info(f"Demande de mise à jour du prompt: {prompt_id}")
        
        # Vérification que le prompt existe
        existing_prompt = prompt_manager.get_prompt(prompt_id)
        if not existing_prompt:
            logger.warning(f"Prompt non trouvé: {prompt_id}")
            raise HTTPException(status_code=404, detail=f"Prompt non trouvé: {prompt_id}")
        
        # Mise à jour du prompt
        prompt_data = {
            "name": request.name,
            "template": request.template
        }
        
        success = prompt_manager.update_prompt(prompt_id, prompt_data)
        
        if not success:
            logger.error(f"Échec de la mise à jour du prompt: {prompt_id}")
            raise HTTPException(status_code=500, detail=f"Échec de la mise à jour du prompt: {prompt_id}")
        
        response = PromptResponse(
            id=prompt_id,
            name=request.name,
            template=request.template
        )
        
        logger.info(f"Mise à jour du prompt {prompt_id} terminée avec succès")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Erreur lors de la mise à jour du prompt: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/prompts/reset", response_model=Dict[str, bool])
async def reset_prompts(
    prompt_id: Optional[str] = None,
    prompt_manager: PromptManager = Depends(get_prompt_manager)
):
    """
    Réinitialise un prompt ou tous les prompts aux valeurs par défaut.
    
    Args:
        prompt_id: Identifiant du prompt à réinitialiser, ou None pour tous les réinitialiser
        
    Returns:
        Dict[str, bool]: Résultat de la réinitialisation
    """
    try:
        if prompt_id:
            logger.info(f"Demande de réinitialisation du prompt: {prompt_id}")
        else:
            logger.info("Demande de réinitialisation de tous les prompts")
        
        success = prompt_manager.reset_to_default(prompt_id)
        
        if not success:
            logger.error("Échec de la réinitialisation des prompts")
            raise HTTPException(status_code=500, detail="Échec de la réinitialisation des prompts")
        
        logger.info("Réinitialisation des prompts terminée avec succès")
        return {"success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Erreur lors de la réinitialisation des prompts: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/extract-specs", response_model=ExtractSpecsResponse)
async def extract_specs(request: ExtractSpecsRequest):
    """
    Extrait les spécifications techniques à partir d'un texte brut.
    """
    try:
        extractor = SpecsExtractor()
        specs = extractor.extract_from_text(request.text)
        return {"specs": specs}
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des spécifications: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'extraction des spécifications: {str(e)}")

@app.post("/batch-generate")
async def batch_generate_descriptions(
    request: BatchProductRequest,
    batch_processor: BatchProcessor = Depends(get_batch_processor)
):
    """
    Génère des descriptions pour plusieurs produits en parallèle.
    """
    try:
        results = await batch_processor.process_batch(
            products=request.products,
            tone_style=request.tone_style,
            seo_optimization=request.seo_optimization,
            use_auto_improvement=request.use_auto_improvement,
            competitor_analysis=request.competitor_analysis,
            use_seo_guide=request.use_seo_guide
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-csv")
async def upload_csv_file(file: UploadFile = File(...)):
    """
    Traite un fichier CSV contenant des informations de produits.
    """
    try:
        # Lire le contenu du fichier
        content = await file.read()
        
        # Vérifier le type de fichier
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Le fichier doit être au format CSV")
        
        # Convertir le contenu en texte
        text = content.decode('utf-8')
        
        # Traiter le CSV (implémentation simplifiée)
        lines = text.strip().split('\n')
        headers = lines[0].split(',')
        
        products = []
        for line in lines[1:]:
            if not line.strip():
                continue
                
            values = line.split(',')
            product = {}
            
            for i, header in enumerate(headers):
                if i < len(values):
                    # Nettoyer les valeurs (enlever les guillemets)
                    value = values[i].strip().strip('"')
                    product[header.strip().strip('"')] = value
            
            products.append(product)
        
        return {"products": products, "headers": headers}
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Impossible de décoder le fichier CSV. Vérifiez l'encodage.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai-providers", response_model=AIProvidersResponse)
async def get_ai_providers():
    """
    Récupère la liste des fournisseurs d'IA disponibles.
    
    Returns:
        AIProvidersResponse: Liste des fournisseurs d'IA disponibles
    """
    try:
        # Vérifier les clés API disponibles
        has_openai_key = bool(os.getenv("OPENAI_API_KEY"))
        has_google_key = bool(os.getenv("GOOGLE_API_KEY"))
        
        providers_list = AIProviderFactory.get_available_providers()
        
        # Filtrer les fournisseurs en fonction des clés API disponibles
        filtered_providers = []
        for provider in providers_list:
            if provider["name"] == "OpenAI" and not has_openai_key:
                continue
            if provider["name"] == "Google Gemini" and not has_google_key:
                continue
                
            # Convertir les modèles au format attendu par Pydantic
            models = [
                AIProviderModel(
                    id=model["id"],
                    name=model["name"],
                    description=model["description"]
                )
                for model in provider["models"]
            ]
            
            filtered_providers.append(
                AIProviderInfo(
                    name=provider["name"],
                    models=models
                )
            )
        
        return AIProvidersResponse(providers=filtered_providers)
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des fournisseurs d'IA: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@app.get("/ai-providers", response_model=AIProvidersResponse)
def get_ai_providers():
    """
    Récupère la liste des fournisseurs d'IA disponibles.
    
    Returns:
        AIProvidersResponse: Liste des fournisseurs d'IA disponibles
    """
    try:
        logger.debug("Récupération des fournisseurs d'IA disponibles")
        
        # Récupération des fournisseurs et modèles disponibles
        providers = []
        
        # OpenAI
        openai_models = [
            AIProviderModel(id="gpt-4o", name="GPT-4o", description="Modèle le plus avancé d'OpenAI, excellente qualité"),
            AIProviderModel(id="gpt-4-turbo", name="GPT-4 Turbo", description="Version plus rapide de GPT-4"),
            AIProviderModel(id="gpt-3.5-turbo", name="GPT-3.5 Turbo", description="Bon équilibre entre coût et qualité")
        ]
        providers.append(AIProviderInfo(name="OpenAI", models=openai_models))
        
        # Google Gemini
        gemini_models = [
            AIProviderModel(id="gemini-pro", name="Gemini Pro", description="Modèle avancé de Google, bonne qualité"),
            AIProviderModel(id="gemini-flash", name="Gemini Flash", description="Version plus rapide de Gemini")
        ]
        providers.append(AIProviderInfo(name="Google Gemini", models=gemini_models))
        
        return AIProvidersResponse(providers=providers)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des fournisseurs d'IA: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des fournisseurs d'IA: {str(e)}")

# Endpoints pour le RAG (Retrieval-Augmented Generation)

@app.post("/upload-client-document", response_model=ClientDocumentResponse, tags=["RAG"])
async def upload_client_document(
    document: ClientDocumentUpload,
    vector_store_service = Depends(get_vector_store_service),
    document_processor: DocumentProcessor = Depends(get_document_processor)
):
    """
    Télécharge et indexe un document client dans le vector store.
    
    Args:
        document: Document client à indexer
        
    Returns:
        ClientDocumentResponse: Informations sur le document indexé
    """
    try:
        logger.debug(f"Téléchargement d'un document client pour {document.client_id}")
        
        # Traiter le document avec le processeur de documents
        document_chunks = document_processor.process_document(document)
        
        # Ajouter les chunks individuellement au vector store
        document_id = document_chunks[0].document_id if document_chunks else str(uuid.uuid4())
        
        # Ajouter chaque chunk individuellement
        for chunk in document_chunks:
            vector_store_service.add_chunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                content=chunk.content,
                metadata=chunk.metadata,
                client_id=document.client_id
            )
        
        return ClientDocumentResponse(
            document_id=document_id,
            client_id=document.client_id,
            title=document.title,
            source_type=document.source_type,
            chunk_count=len(document_chunks),
            status="indexed"
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'indexation du document: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'indexation du document: {str(e)}")

@app.post("/upload-client-file", response_model=ClientDocumentResponse, tags=["RAG"])
async def upload_client_file(
    file: UploadFile = File(...),
    client_id: str = Form(...),
    title: Optional[str] = Form(None),
    source_type: str = Form("uploaded_file"),
    vector_store_service = Depends(get_vector_store_service),
    document_processor: DocumentProcessor = Depends(get_document_processor)
):
    """
    Télécharge et indexe un fichier client dans le vector store.
    
    Args:
        file: Fichier à traiter et indexer
        client_id: ID du client
        title: Titre du document (facultatif, utilisera le nom du fichier si non fourni)
        source_type: Type de source du document
        
    Returns:
        ClientDocumentResponse: Informations sur le document indexé
    """
    try:
        # Traiter le fichier uploadé
        file_processor = FileProcessor()
        document = await file_processor.process_uploaded_file(
            file=file,
            client_id=client_id,
            title=title,
            source_type=source_type
        )
        
        # Traiter le document avec le processeur de documents
        document_chunks = document_processor.process_document(document)
        
        # Ajouter les chunks individuellement au vector store
        document_id = document_chunks[0].document_id if document_chunks else str(uuid.uuid4())
        
        # Ajouter chaque chunk individuellement
        for chunk in document_chunks:
            vector_store_service.add_chunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                content=chunk.content,
                metadata=chunk.metadata,
                client_id=document.client_id
            )
        
        return ClientDocumentResponse(
            document_id=document_id,
            client_id=document.client_id,
            title=document.title,
            source_type=document.source_type,
            chunk_count=len(document_chunks),
            status="indexed"
        )
    except ValueError as e:
        logger.error(f"Erreur de validation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de l'indexation du fichier: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'indexation du fichier: {str(e)}")

@app.get("/client-data/{client_id}", response_model=ClientDataSummaryResponse)
async def get_client_data(
    client_id: str,
    vector_store_service = Depends(get_vector_store_service)
):
    """
    Récupère un résumé des données client disponibles.
    
    Args:
        client_id: ID du client
        
    Returns:
        ClientDataSummaryResponse: Résumé des données client
    """
    try:
        logger.debug(f"Récupération des données client pour {client_id}")
        
        # Récupération du résumé des données client
        summary = vector_store_service.get_client_data_summary(client_id)
        
        # Création de la réponse
        response = ClientDataSummaryResponse(
            client_id=summary["client_id"],
            document_count=summary["document_count"],
            document_types=summary["document_types"],
            documents=summary["documents"]
        )
        
        logger.debug(f"Données client récupérées avec succès, {response.document_count} documents trouvés")
        return response
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données client: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données client: {str(e)}")

@app.delete("/client-document/{document_id}")
async def delete_client_document(
    document_id: str,
    vector_store_service = Depends(get_vector_store_service)
):
    """
    Supprime un document client du vector store.
    
    Args:
        document_id: ID du document à supprimer
        
    Returns:
        Dict[str, bool]: Résultat de la suppression
    """
    try:
        logger.debug(f"Suppression du document client {document_id}")
        
        # Suppression du document
        result = vector_store_service.delete_document(document_id)
        
        if result:
            logger.debug(f"Document client {document_id} supprimé avec succès")
            return {"success": True}
        else:
            logger.warning(f"Document client {document_id} non trouvé")
            raise HTTPException(status_code=404, detail=f"Document client {document_id} non trouvé")
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du document client: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression du document client: {str(e)}")

@app.post("/generate-with-rag", response_model=ProductResponse)
async def generate_with_rag(
    request: RAGProductDescriptionRequest,
    product_generator: ProductDescriptionGenerator = Depends(get_product_generator),
    thot_seo_service: ThotSeoService = Depends(get_thot_seo_service)
):
    """
    Génère une description de produit enrichie avec RAG.
    
    Args:
        request: Informations sur le produit et options de génération
        
    Returns:
        ProductResponse: Description générée et suggestions SEO
    """
    try:
        logger.debug("Début de la génération avec RAG")
        logger.debug(f"Client ID: {request.client_id}")
        
        # Préparation des données pour la génération
        product_data = {
            "product_info": request.product_info,
            "tone_style": request.tone_style,
            "seo_optimization": request.seo_optimization,
            "competitor_analysis": request.competitor_analysis,
            "competitor_insights": request.competitor_insights,
            "use_seo_guide": request.use_seo_guide,
            "seo_guide_insights": None,
            "use_rag": True,  # Activer le RAG
            "client_id": request.client_id
        }
        
        # Si le guide SEO est demandé, récupérer les insights
        if request.use_seo_guide and request.seo_guide_keywords:
            logger.debug(f"Récupération du guide SEO pour les mots-clés: {request.seo_guide_keywords}")
            
            try:
                seo_guide = thot_seo_service.get_seo_guide(request.seo_guide_keywords)
                product_data["seo_guide_insights"] = seo_guide
                logger.debug("Guide SEO récupéré avec succès")
            except Exception as seo_error:
                logger.error(f"Erreur lors de la récupération du guide SEO: {str(seo_error)}")
                # Continuer sans guide SEO
                product_data["use_seo_guide"] = False
        
        # Génération de la description
        result = product_generator.generate_product_description(product_data)
        
        # Création de la réponse
        response = ProductResponse(
            product_description=result["product_description"],
            seo_suggestions=result.get("seo_suggestions", []),
            competitor_insights=result.get("competitor_insights", []),
            ai_provider=result.get("ai_provider")
        )
        
        logger.debug("Génération avec RAG terminée avec succès")
        return response
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération avec RAG: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération avec RAG: {str(e)}")

# Démarrage de l'application
if __name__ == "__main__":
    import uvicorn
    logger.info("Démarrage du serveur FastAPI sur le port 8050")
    uvicorn.run("main:app", host="0.0.0.0", port=8050, reload=True)