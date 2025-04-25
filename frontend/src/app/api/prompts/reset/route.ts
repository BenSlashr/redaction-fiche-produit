import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Récupérer le prompt_id de la requête s'il existe
    const { searchParams } = new URL(request.url);
    const promptId = searchParams.get('prompt_id');
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8050';
    
    let url = `${apiUrl}/prompts/reset`;
    
    // Ajouter le prompt_id à l'URL si présent
    if (promptId) {
      url += `?prompt_id=${promptId}`;
    }
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`Erreur API: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Erreur lors de la réinitialisation des prompts:', error);
    return NextResponse.json(
      { error: 'Erreur lors de la réinitialisation des prompts' },
      { status: 500 }
    );
  }
}
