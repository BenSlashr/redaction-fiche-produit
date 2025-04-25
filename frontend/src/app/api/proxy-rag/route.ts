import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

// Récupérer l'URL de l'API depuis les variables d'environnement
// Utiliser explicitement l'adresse IPv4 pour éviter les problèmes avec IPv6
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8050';

export async function POST(request: NextRequest) {
  try {
    // Récupérer les données de la requête
    const data = await request.json();
    
    console.log('Proxy RAG - Requête reçue:', JSON.stringify(data));
    
    // Transférer la requête au backend
    const response = await axios.post(`${API_URL}/generate-with-rag`, data);
    
    console.log('Proxy RAG - Réponse reçue du backend');
    
    // Retourner la réponse du backend
    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error('Erreur dans proxy-rag:', error.message);
    
    // Retourner une erreur
    return NextResponse.json(
      { 
        error: 'Erreur lors de la génération avec RAG', 
        details: error.message,
        stack: error.stack
      }, 
      { status: 500 }
    );
  }
}
