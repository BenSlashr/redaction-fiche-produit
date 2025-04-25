import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // Utiliser l'URL complète avec http://
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8050';
    const response = await fetch(`${apiUrl}/prompts`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Ajouter ces options pour éviter les problèmes de CORS et de certificats
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`Erreur API: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Erreur lors de la récupération des prompts:', error);
    return NextResponse.json(
      { error: 'Erreur lors de la récupération des prompts' },
      { status: 500 }
    );
  }
}
