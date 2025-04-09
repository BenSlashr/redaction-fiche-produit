import axios from 'axios';

// Configuration de l'URL de l'API
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// Types pour les requêtes et réponses
interface ProductInfo {
  name: string;
  description: string;
  category?: string;
  keywords?: string[];
  technical_specs?: Record<string, string>;
}

interface ToneStyle {
  tone?: string;
  style?: string;
  persona_target?: string;
  brand_name?: string;
  tone_description?: string;
  tone_example?: string;
}

interface AIProvider {
  provider_type: string;
  model_name: string;
}

interface ProductDescriptionRequest {
  product_info: ProductInfo;
  tone_style: ToneStyle;
  seo_optimization?: boolean;
  competitor_analysis?: boolean;
  use_seo_guide?: boolean;
  seo_guide_keywords?: string;
  auto_improve?: boolean;
  ai_provider?: AIProvider;
  use_rag?: boolean;
  client_id?: string;
  document_ids?: string[];
}

interface ProductResponse {
  product_description: string;
  improved_description?: string;
  seo_suggestions?: string[];
  competitor_insights?: any[];
  ai_provider?: {
    provider: string;
    model: string;
    pricing: {
      input: number;
      output: number;
      currency: string;
      unit: string;
    };
  };
}

interface ClientDocument {
  client_id: string;
  title: string;
  content: string;
  source_type: string;
}

interface ClientDocumentResponse {
  document_id: string;
  chunk_count: number;
}

interface ClientDataResponse {
  client_id: string;
  document_count: number;
  document_types: Record<string, number>;
  documents: {
    document_id: string;
    title: string;
    source_type: string;
  }[];
}

interface AIModel {
  id: string;
  name: string;
  description: string;
}

interface AIProviderInfo {
  name: string;
  models: AIModel[];
}

interface AIProvidersResponse {
  providers: AIProviderInfo[];
}

interface SeoGuideRequest {
  keywords: string;
}

interface SeoGuideResponse {
  required_keywords: any[];
  complementary_keywords: any[];
  expressions: string[];
  questions: string[];
  word_count: number;
  target_score: number;
  max_overoptimization: number;
  competition: any[];
}

interface CompetitorAnalysisRequest {
  product_name: string;
  product_category: string;
  search_query?: string;
}

interface CompetitorAnalysisResponse {
  key_features: string[];
  unique_selling_points: string[];
  common_specifications: string[];
  content_structure: string;
  seo_keywords: string[];
}

interface ExtractSpecsRequest {
  raw_text: string;
}

interface ExtractSpecsResponse {
  specs: Record<string, string>;
}

// Service API
// Types pour les templates
interface ProductSectionTemplate {
  id: string;
  name: string;
  description: string;
  prompt_template: string;
  rag_query_template: string;
}

interface ProductTemplate {
  id: string;
  name: string;
  description: string;
  sections: ProductSectionTemplate[];
}

interface TemplateResponse {
  templates: ProductTemplate[];
}

interface GenerateWithTemplateRequest extends ProductDescriptionRequest {
  template_id: string;
  sections?: string[];
}

export const api = {
  // Génération de description de produit
  async generateDescription(data: ProductDescriptionRequest): Promise<ProductResponse> {
    console.log('Appel à generateDescription via proxy');
    const response = await axios.post('/api/proxy-generate', data);
    return response.data;
  },

  // Génération de description avec RAG
  async generateWithRAG(data: ProductDescriptionRequest): Promise<ProductResponse> {
    console.log('Appel à generateWithRAG via proxy');
    const response = await axios.post('/api/proxy-rag', data);
    return response.data;
  },

  // Récupération du guide SEO
  async getSeoGuide(keywords: string): Promise<SeoGuideResponse> {
    const response = await axios.post(`${API_URL}/get-seo-guide`, { keywords });
    return response.data;
  },

  // Analyse des concurrents
  async analyzeCompetitors(data: CompetitorAnalysisRequest): Promise<CompetitorAnalysisResponse> {
    const response = await axios.post(`${API_URL}/analyze-competitors`, data);
    return response.data;
  },

  // Extraction des spécifications techniques
  async extractSpecs(rawText: string): Promise<Record<string, string>> {
    const response = await axios.post(`${API_URL}/extract-specs`, { raw_text: rawText });
    return response.data.specs;
  },

  // Téléchargement et indexation d'un document client
  async uploadClientDocument(document: ClientDocument): Promise<ClientDocumentResponse> {
    const response = await axios.post(`${API_URL}/upload-client-document`, document);
    return response.data;
  },

  // Récupération des données d'un client
  async getClientData(clientId: string): Promise<ClientDataResponse> {
    const response = await axios.get(`${API_URL}/client-data/${clientId}`);
    return response.data;
  },

  // Suppression d'un document client
  async deleteClientDocument(documentId: string): Promise<{ success: boolean }> {
    const response = await axios.delete(`${API_URL}/client-document/${documentId}`);
    return response.data;
  },

  // Génération par lot
  async batchGenerate(formData: FormData): Promise<any> {
    const response = await axios.post(`${API_URL}/batch-generate`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  // Récupération des fournisseurs d'IA disponibles
  async getAIProviders(): Promise<AIProvidersResponse> {
    const response = await axios.get(`${API_URL}/ai-providers`);
    return response.data;
  },

  // Récupération des templates disponibles
  async getTemplates(): Promise<TemplateResponse> {
    try {
      console.log('Appel à getTemplates via proxy');
      const response = await axios.get('/api/proxy-template');
      console.log('Réponse brute de l\'API templates via proxy:', response);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des templates:', error);
      throw error;
    }
  },

  // Génération avec template
  async generateWithTemplate(data: GenerateWithTemplateRequest): Promise<ProductResponse> {
    console.log('Appel à generateWithTemplate via proxy');
    const response = await axios.post('/api/proxy-template', data);
    return response.data;
  }
};
