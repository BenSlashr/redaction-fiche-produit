import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    
    // Récupérer le fichier et les autres données du formulaire
    const file = formData.get('file') as File;
    const clientId = formData.get('client_id') as string;
    const title = formData.get('title') as string | null;
    const sourceType = formData.get('source_type') as string;
    
    if (!file || !clientId) {
      return NextResponse.json(
        { error: 'Fichier et ID client requis' },
        { status: 400 }
      );
    }
    
    // Créer un nouveau FormData pour l'envoi au backend
    const backendFormData = new FormData();
    backendFormData.append('file', file);
    backendFormData.append('client_id', clientId);
    
    if (title) {
      backendFormData.append('title', title);
    }
    
    backendFormData.append('source_type', sourceType || 'uploaded_file');
    
    // Envoyer la requête au backend
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8050';
    const response = await fetch(`${backendUrl}/upload-client-file`, {
      method: 'POST',
      body: backendFormData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Erreur lors du téléchargement du fichier' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Erreur lors du traitement de la requête:', error);
    return NextResponse.json(
      { error: 'Erreur lors du traitement de la requête' },
      { status: 500 }
    );
  }
}
