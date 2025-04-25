import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

// Récupérer l'URL de l'API depuis les variables d'environnement
// Utiliser explicitement l'adresse IPv4 pour éviter les problèmes avec IPv6
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8050';

export async function GET() {
  try {
    console.log('Proxy template - Requête GET reçue');
    
    // Transférer la requête au backend
    const response = await axios.get(`${API_URL}/templates`);
    
    console.log('Proxy template - Réponse reçue du backend');
    
    // Retourner la réponse du backend
    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error('Erreur dans proxy-template (GET):', error.message);
    
    // Retourner une erreur
    return NextResponse.json(
      { 
        error: 'Erreur lors de la récupération des templates', 
        details: error.message,
        stack: error.stack
      }, 
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    // Récupérer les données de la requête
    const data = await request.json();
    
    console.log('Proxy template - Requête POST reçue:', JSON.stringify(data));
    
    // Transférer la requête au backend
    const response = await axios.post(`${API_URL}/templates/generate`, data);
    
    console.log('Proxy template - Réponse reçue du backend');
    
    // Retourner la réponse du backend
    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error('Erreur dans proxy-template (POST):', error.message);
    
    // Retourner une erreur
    return NextResponse.json(
      { 
        error: 'Erreur lors de la génération avec template', 
        details: error.message,
        stack: error.stack
      }, 
      { status: 500 }
    );
  }
}
