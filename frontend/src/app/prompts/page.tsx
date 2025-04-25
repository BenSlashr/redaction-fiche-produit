"use client";

import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, CheckCircle2, RefreshCw } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/components/ui/use-toast";
import { Skeleton } from "@/components/ui/skeleton";

interface Prompt {
  id: string;
  name: string;
  template: string;
}

interface AllPromptsResponse {
  prompts: Record<string, Prompt>;
}

const PromptManager = () => {
  const { toast } = useToast();
  const [prompts, setPrompts] = useState<Record<string, Prompt>>({});
  const [activePrompt, setActivePrompt] = useState<string | null>(null);
  const [editedName, setEditedName] = useState<string>('');
  const [editedTemplate, setEditedTemplate] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isResetting, setIsResetting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Charger tous les prompts au chargement de la page
  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        setIsLoading(true);
        // Appel direct à l'API backend
        const response = await fetch('http://localhost:8050/prompts', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          cache: 'no-store',
        });
        if (!response.ok) {
          throw new Error(`Erreur lors du chargement des prompts: ${response.status}`);
        }
        const data: AllPromptsResponse = await response.json();
        setPrompts(data.prompts);
        
        // Définir le premier prompt comme actif par défaut
        if (Object.keys(data.prompts).length > 0) {
          const firstPromptId = Object.keys(data.prompts)[0];
          setActivePrompt(firstPromptId);
          setEditedName(data.prompts[firstPromptId].name);
          setEditedTemplate(data.prompts[firstPromptId].template);
        }
      } catch (err) {
        setError(`Erreur lors du chargement des prompts: ${err instanceof Error ? err.message : String(err)}`);
        toast({
          title: "Erreur",
          description: "Impossible de charger les prompts. Veuillez réessayer.",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchPrompts();
  }, [toast]);

  // Gérer le changement de prompt actif
  const handlePromptChange = (promptId: string) => {
    if (activePrompt === promptId) return;
    
    setActivePrompt(promptId);
    setEditedName(prompts[promptId].name);
    setEditedTemplate(prompts[promptId].template);
    setError(null);
    setSuccess(null);
  };

  // Sauvegarder les modifications
  const handleSave = async () => {
    if (!activePrompt) return;

    try {
      setIsSaving(true);
      setError(null);
      setSuccess(null);

      // Appel direct à l'API backend
      const response = await fetch(`http://localhost:8050/prompts/${activePrompt}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: editedName,
          template: editedTemplate,
        }),
        cache: 'no-store',
      });

      if (!response.ok) {
        throw new Error(`Erreur lors de la sauvegarde: ${response.status}`);
      }

      const updatedPrompt = await response.json();
      
      // Mettre à jour l'état local
      setPrompts(prev => ({
        ...prev,
        [activePrompt]: {
          id: activePrompt,
          name: updatedPrompt.name,
          template: updatedPrompt.template,
        },
      }));

      setSuccess("Prompt sauvegardé avec succès");
      toast({
        title: "Succès",
        description: "Le prompt a été sauvegardé avec succès.",
      });
    } catch (err) {
      setError(`Erreur lors de la sauvegarde: ${err instanceof Error ? err.message : String(err)}`);
      toast({
        title: "Erreur",
        description: "Impossible de sauvegarder le prompt. Veuillez réessayer.",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  // Réinitialiser un prompt
  const handleReset = async () => {
    if (!activePrompt) return;

    try {
      setIsResetting(true);
      setError(null);
      setSuccess(null);

      // Appel direct à l'API backend
      const response = await fetch(`http://localhost:8050/prompts/reset?prompt_id=${activePrompt}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      });

      if (!response.ok) {
        throw new Error(`Erreur lors de la réinitialisation: ${response.status}`);
      }

      // Recharger tous les prompts pour obtenir la version réinitialisée
      const promptsResponse = await fetch('http://localhost:8050/prompts', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      });
      
      if (!promptsResponse.ok) {
        throw new Error(`Erreur lors du rechargement des prompts: ${promptsResponse.status}`);
      }
      
      const data: AllPromptsResponse = await promptsResponse.json();
      setPrompts(data.prompts);
      
      // Mettre à jour le prompt actif
      setEditedName(data.prompts[activePrompt].name);
      setEditedTemplate(data.prompts[activePrompt].template);

      setSuccess("Prompt réinitialisé avec succès");
      toast({
        title: "Succès",
        description: "Le prompt a été réinitialisé avec succès.",
      });
    } catch (err) {
      setError(`Erreur lors de la réinitialisation: ${err instanceof Error ? err.message : String(err)}`);
      toast({
        title: "Erreur",
        description: "Impossible de réinitialiser le prompt. Veuillez réessayer.",
        variant: "destructive",
      });
    } finally {
      setIsResetting(false);
    }
  };

  // Réinitialiser tous les prompts
  const handleResetAll = async () => {
    if (!window.confirm("Êtes-vous sûr de vouloir réinitialiser tous les prompts ? Cette action est irréversible.")) {
      return;
    }

    try {
      setIsResetting(true);
      setError(null);
      setSuccess(null);

      // Appel direct à l'API backend
      const response = await fetch(`http://localhost:8050/prompts/reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      });

      if (!response.ok) {
        throw new Error(`Erreur lors de la réinitialisation: ${response.status}`);
      }

      // Recharger tous les prompts
      const promptsResponse = await fetch('http://localhost:8050/prompts', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      });
      
      if (!promptsResponse.ok) {
        throw new Error(`Erreur lors du rechargement des prompts: ${promptsResponse.status}`);
      }
      
      const data: AllPromptsResponse = await promptsResponse.json();
      setPrompts(data.prompts);
      
      // Mettre à jour le prompt actif s'il existe encore
      if (activePrompt && data.prompts[activePrompt]) {
        setEditedName(data.prompts[activePrompt].name);
        setEditedTemplate(data.prompts[activePrompt].template);
      }

      setSuccess("Tous les prompts ont été réinitialisés avec succès");
      toast({
        title: "Succès",
        description: "Tous les prompts ont été réinitialisés avec succès.",
      });
    } catch (err) {
      setError(`Erreur lors de la réinitialisation: ${err instanceof Error ? err.message : String(err)}`);
      toast({
        title: "Erreur",
        description: "Impossible de réinitialiser les prompts. Veuillez réessayer.",
        variant: "destructive",
      });
    } finally {
      setIsResetting(false);
    }
  };

  // Rendu du squelette de chargement
  if (isLoading) {
    return (
      <div className="container mx-auto py-8">
        <h1 className="text-3xl font-bold mb-6">Gestion des Prompts</h1>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="md:col-span-1">
            <Skeleton className="h-10 w-full mb-2" />
            <Skeleton className="h-10 w-full mb-2" />
            <Skeleton className="h-10 w-full mb-2" />
            <Skeleton className="h-10 w-full mb-2" />
          </div>
          <div className="md:col-span-3">
            <Skeleton className="h-10 w-full mb-4" />
            <Skeleton className="h-64 w-full mb-4" />
            <Skeleton className="h-10 w-32" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">Gestion des Prompts</h1>
      
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Erreur</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {success && (
        <Alert className="mb-4 bg-green-50 border-green-200">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertTitle className="text-green-600">Succès</AlertTitle>
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Liste des prompts */}
        <div className="md:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Prompts disponibles</CardTitle>
              <CardDescription>Sélectionnez un prompt à modifier</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col space-y-2">
                {Object.entries(prompts).map(([id, prompt]) => (
                  <Button
                    key={id}
                    variant={activePrompt === id ? "default" : "outline"}
                    onClick={() => handlePromptChange(id)}
                    className="justify-start text-left"
                  >
                    {prompt.name}
                  </Button>
                ))}
              </div>
            </CardContent>
            <CardFooter>
              <Button 
                variant="outline" 
                className="w-full" 
                onClick={handleResetAll}
                disabled={isResetting}
              >
                {isResetting ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Réinitialisation...
                  </>
                ) : (
                  "Réinitialiser tous les prompts"
                )}
              </Button>
            </CardFooter>
          </Card>
        </div>

        {/* Éditeur de prompt */}
        <div className="md:col-span-3">
          {activePrompt ? (
            <Card>
              <CardHeader>
                <CardTitle>Modifier le prompt</CardTitle>
                <CardDescription>
                  Personnalisez le prompt selon vos besoins
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label htmlFor="promptName" className="block text-sm font-medium mb-1">
                    Nom du prompt
                  </label>
                  <Input
                    id="promptName"
                    value={editedName}
                    onChange={(e) => setEditedName(e.target.value)}
                    placeholder="Nom du prompt"
                  />
                </div>
                <div>
                  <label htmlFor="promptTemplate" className="block text-sm font-medium mb-1">
                    Template du prompt
                  </label>
                  <Textarea
                    id="promptTemplate"
                    value={editedTemplate}
                    onChange={(e) => setEditedTemplate(e.target.value)}
                    placeholder="Template du prompt"
                    className="font-mono h-96 whitespace-pre"
                  />
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button 
                  variant="outline" 
                  onClick={handleReset}
                  disabled={isResetting}
                >
                  {isResetting ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Réinitialisation...
                    </>
                  ) : (
                    "Réinitialiser ce prompt"
                  )}
                </Button>
                <Button 
                  onClick={handleSave}
                  disabled={isSaving}
                >
                  {isSaving ? "Sauvegarde en cours..." : "Sauvegarder"}
                </Button>
              </CardFooter>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-10">
                <p className="text-center text-muted-foreground">
                  Sélectionnez un prompt à modifier
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Guide d'utilisation des variables</h2>
        <Card>
          <CardContent className="py-6">
            <p className="mb-4">
              Les prompts utilisent des variables qui sont remplacées par les valeurs correspondantes lors de la génération.
              Voici les principales variables disponibles selon le type de prompt :
            </p>
            
            <h3 className="text-xl font-semibold mt-4 mb-2">Variables communes</h3>
            <ul className="list-disc pl-6 space-y-1">
              <li><code className="bg-muted px-1 rounded">{"{product_name}"}</code> - Nom du produit</li>
              <li><code className="bg-muted px-1 rounded">{"{product_description}"}</code> - Description du produit</li>
              <li><code className="bg-muted px-1 rounded">{"{product_category}"}</code> - Catégorie du produit</li>
              <li><code className="bg-muted px-1 rounded">{"{keywords}"}</code> - Mots-clés du produit</li>
              <li><code className="bg-muted px-1 rounded">{"{technical_specs}"}</code> - Spécifications techniques</li>
              <li><code className="bg-muted px-1 rounded">{"{tone_instructions}"}</code> - Instructions de ton</li>
              <li><code className="bg-muted px-1 rounded">{"{seo_optimization}"}</code> - Niveau d'optimisation SEO</li>
              <li><code className="bg-muted px-1 rounded">{"{competitor_insights}"}</code> - Insights concurrentiels</li>
              <li><code className="bg-muted px-1 rounded">{"{seo_guide_info}"}</code> - Informations du guide SEO</li>
              <li><code className="bg-muted px-1 rounded bg-yellow-100 font-bold border border-yellow-300">{"{client_data_context}"}</code> - <span className="font-semibold text-blue-600">Contexte RAG</span> : Informations pertinentes extraites des documents clients</li>
            </ul>

            <h3 className="text-xl font-semibold mt-4 mb-2">Variables spécifiques à l'auto-amélioration</h3>
            <ul className="list-disc pl-6 space-y-1">
              <li><code className="bg-muted px-1 rounded">{"{generated_description}"}</code> - Description générée initialement</li>
              <li><code className="bg-muted px-1 rounded">{"{evaluation_summary}"}</code> - Résumé de l'évaluation</li>
              <li><code className="bg-muted px-1 rounded">{"{improvement_points}"}</code> - Points à améliorer</li>
              <li><code className="bg-muted px-1 rounded">{"{improved_description}"}</code> - Description améliorée</li>
              <li><code className="bg-muted px-1 rounded">{"{format_instructions}"}</code> - Instructions de formatage (pour l'évaluation)</li>
            </ul>

            <h3 className="text-xl font-semibold mt-6 mb-2 text-blue-600">Utilisation du RAG (Retrieval Augmented Generation)</h3>
            <div className="bg-blue-50 p-4 rounded-md border border-blue-200 mb-6">
              <h4 className="font-bold mb-2">Comment utiliser la variable <code className="bg-muted px-1 rounded">{"client_data_context"}</code></h4>
              <p className="mb-3">
                Cette variable est <span className="font-semibold">essentielle</span> pour le fonctionnement du RAG. Elle contient toutes les informations pertinentes extraites automatiquement des documents clients en fonction du produit à décrire.
              </p>
              <p className="mb-3">
                <span className="font-semibold">Placement recommandé</span> : Placez cette variable après les informations produit et avant les instructions de génération pour que l'IA puisse s'en servir efficacement.
              </p>
              <div className="bg-white p-3 rounded-md border border-gray-200 font-mono text-sm whitespace-pre-wrap mb-3">
                INFORMATIONS PRODUIT:
- Nom: {"product_name"}
- Description: {"product_description"}
...

<span className="bg-yellow-100 px-1">{"client_data_context"}</span>

INSTRUCTIONS:
- Crée une description complète et persuasive
- Utilise les informations techniques précises du contexte client
...</div>
              <p className="font-semibold text-blue-700">
                ⚠️ Important : Si vous supprimez cette variable de votre prompt, le système l'ajoutera automatiquement, mais pour un meilleur contrôle, gardez-la et positionnez-la stratégiquement.
              </p>
            </div>
            
            <div className="bg-yellow-50 p-4 rounded-md mt-6 border border-yellow-200">
              <h4 className="text-lg font-semibold text-yellow-800 mb-2">Important</h4>
              <p className="text-yellow-700">
                Assurez-vous de conserver toutes les variables nécessaires dans vos prompts personnalisés.
                La suppression de variables essentielles peut entraîner des erreurs lors de la génération.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PromptManager;
