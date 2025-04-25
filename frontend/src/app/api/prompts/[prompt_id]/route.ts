import { NextRequest, NextResponse } from 'next/server';

type Params = {
  params: {
    prompt_id: string;
  };
};

export async function GET(
  request: NextRequest,
  { params }: Params
) {
  try {
    const promptId = params.prompt_id;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8050';
    
    const response = await fetch(`${apiUrl}/prompts/${promptId}`, {
      method: 'GET',
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
    console.error(`Erreur lors de la récupération du prompt ${params.prompt_id}:`, error);
    return NextResponse.json(
      { error: `Erreur lors de la récupération du prompt ${params.prompt_id}` },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: Params
) {
  try {
    const promptId = params.prompt_id;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8050';
    const body = await request.json();
    
    const response = await fetch(`${apiUrl}/prompts/${promptId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Erreur API: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`Erreur lors de la mise à jour du prompt ${params.prompt_id}:`, error);
    return NextResponse.json(
      { error: `Erreur lors de la mise à jour du prompt ${params.prompt_id}` },
      { status: 500 }
    );
  }
}
