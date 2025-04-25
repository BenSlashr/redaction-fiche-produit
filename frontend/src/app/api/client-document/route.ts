import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8050';
    
    const response = await fetch(`${apiUrl}/upload-client-document`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`Erreur API: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Erreur lors du téléchargement du document:', error);
    return NextResponse.json(
      { error: 'Erreur lors du téléchargement du document' },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    // Extraire l'ID du document de l'URL
    const url = new URL(request.url);
    const documentId = url.pathname.split('/').pop();
    
    if (!documentId) {
      return NextResponse.json(
        { error: 'ID de document manquant' },
        { status: 400 }
      );
    }
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8050';
    
    const response = await fetch(`${apiUrl}/client-document/${documentId}`, {
      method: 'DELETE',
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`Erreur API: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Erreur lors de la suppression du document:', error);
    return NextResponse.json(
      { error: 'Erreur lors de la suppression du document' },
      { status: 500 }
    );
  }
}
