import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { clientId: string } }
) {
  try {
    const { clientId } = params;
    
    if (!clientId) {
      return NextResponse.json(
        { error: 'ID client manquant' },
        { status: 400 }
      );
    }
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8050';
    
    const response = await fetch(`${apiUrl}/client-data/${clientId}`, {
      method: 'GET',
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`Erreur API: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Erreur lors de la récupération des données client:', error);
    return NextResponse.json(
      { error: 'Erreur lors de la récupération des données client' },
      { status: 500 }
    );
  }
}
