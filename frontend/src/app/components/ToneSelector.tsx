'use client';

import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";

interface ToneCharacteristic {
  name: string;
  description: string;
}

interface PredefinedTone {
  id: string;
  name: string;
  description: string;
  characteristics: string[];
  example: string;
}

interface ToneAnalysis {
  tone_description: string;
  tone_characteristics: string[];
  writing_style: string;
  vocabulary_level: string;
  sentence_structure: string;
}

interface ToneOption {
  id: string;
  name: string;
  description: string;
  tone_description: string;
  tone_example: string;
  brand_name?: string;
  persona_target?: string;
  characteristics?: string[];
}

interface ToneSelectorProps {
  onToneSelect: (toneData: {
    predefined_tone_id?: string;
    tone_description?: string;
    tone_example?: string;
    brand_name?: string;
    persona_target?: string;
  }) => void;
}

const predefinedTones: ToneOption[] = [
  {
    id: "professional",
    name: "Professionnel",
    description: "Un ton formel et informatif, adapté aux entreprises B2B",
    tone_description: "Ton professionnel, formel et informatif",
    tone_example: "Notre solution offre une productivité accrue grâce à son interface intuitive et ses fonctionnalités avancées.",
    persona_target: "Professionnels du secteur qui recherchent des informations techniques précises et des avantages concrets"
  },
  {
    id: "casual",
    name: "Décontracté",
    description: "Un ton amical et conversationnel, idéal pour les produits grand public",
    tone_description: "Ton décontracté, amical et conversationnel",
    tone_example: "Vous allez adorer ce produit qui simplifie votre quotidien tout en étant super facile à utiliser !",
    persona_target: "Particuliers qui recherchent des solutions pratiques et faciles à comprendre pour leur usage personnel"
  },
  {
    id: "luxury",
    name: "Luxe",
    description: "Un ton sophistiqué et exclusif pour les produits haut de gamme",
    tone_description: "Ton sophistiqué, exclusif et raffiné",
    tone_example: "Cette création d'exception incarne l'alliance parfaite entre artisanat d'excellence et innovation discrète.",
    persona_target: "Clients exigeants à la recherche de produits exclusifs et de qualité supérieure"
  },
  {
    id: "technical",
    name: "Technique",
    description: "Un ton précis et détaillé, idéal pour les produits complexes",
    tone_description: "Ton technique, précis et détaillé",
    tone_example: "Ce système intègre un processeur octa-core cadencé à 2,8 GHz avec 16 Go de mémoire vive DDR4.",
    persona_target: "Experts qui apprécient les détails techniques avancés et les spécifications précises"
  },
  {
    id: "educational",
    name: "Éducatif",
    description: "Un ton pédagogique et explicatif, parfait pour les nouveaux concepts",
    tone_description: "Ton pédagogique, explicatif et informatif",
    tone_example: "Voici comment fonctionne ce produit : d'abord, il analyse vos données, puis il les traite pour vous offrir des résultats clairs.",
    persona_target: "Débutants qui ont besoin d'explications claires, simples et pédagogiques sans jargon technique excessif"
  },
  {
    id: "enthusiastic",
    name: "Enthousiaste",
    description: "Un ton énergique et passionné, idéal pour les produits innovants",
    tone_description: "Ton énergique, passionné et enthousiaste",
    tone_example: "Cette innovation révolutionnaire va transformer votre façon de travailler et vous faire gagner un temps précieux !",
    persona_target: "Utilisateurs enthousiastes à la recherche des dernières innovations et tendances"
  },
  {
    id: "custom",
    name: "Personnalisé",
    description: "Définissez votre propre ton",
    tone_description: "",
    tone_example: "",
    persona_target: ""
  }
];

const ToneSelector = ({ onToneSelect }: ToneSelectorProps) => {
  const [activeTab, setActiveTab] = useState<string>("predefined");
  const [selectedTone, setSelectedTone] = useState<string>("");
  const [customToneDescription, setCustomToneDescription] = useState<string>("");
  const [customToneExample, setCustomToneExample] = useState<string>("");
  const [customBrandName, setCustomBrandName] = useState<string>("");
  const [customPersonaTarget, setCustomPersonaTarget] = useState<string>("");
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [toneAnalysis, setToneAnalysis] = useState<ToneAnalysis | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const fetchPredefinedTones = async () => {
      try {
        // Utiliser directement les tons prédéfinis au lieu de faire un appel API
        // qui n'existe pas encore
        if (predefinedTones.length > 0) {
          const firstTone = predefinedTones[0];
          setSelectedTone(firstTone.id);
          
          // Appeler directement onToneSelect au lieu de handleToneSelect
          // pour éviter les dépendances circulaires
          onToneSelect({
            predefined_tone_id: firstTone.id,
            tone_description: firstTone.tone_description,
            tone_example: firstTone.tone_example,
            brand_name: firstTone.brand_name,
            persona_target: firstTone.persona_target
          });
          
          // Initialiser les champs personnalisés
          setCustomToneDescription(firstTone.tone_description || "");
          setCustomToneExample(firstTone.tone_example || "");
          setCustomBrandName(firstTone.brand_name || "");
          setCustomPersonaTarget(firstTone.persona_target || "");
        }
      } catch (error) {
        console.error("Erreur lors du chargement des tons prédéfinis:", error);
        setError("Impossible de charger les tons prédéfinis. Veuillez réessayer.");
      }
    };
    
    fetchPredefinedTones();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Exécuté uniquement au montage du composant

  const handleToneSelect = (tone: ToneOption) => {
    setSelectedTone(tone.id);
    
    if (tone.id === "custom") {
      onToneSelect({
        predefined_tone_id: tone.id,
        tone_description: customToneDescription,
        tone_example: customToneExample,
        brand_name: customBrandName,
        persona_target: customPersonaTarget
      });
    } else {
      onToneSelect({
        predefined_tone_id: tone.id,
        tone_description: tone.tone_description,
        tone_example: tone.tone_example,
        brand_name: tone.brand_name,
        persona_target: tone.persona_target
      });
      
      setCustomToneDescription(tone.tone_description);
      setCustomToneExample(tone.tone_example);
      setCustomBrandName(tone.brand_name || "");
      setCustomPersonaTarget(tone.persona_target || "");
    }
  };

  const handleAnalyzeCustomText = async () => {
    if (!customToneDescription || !customToneDescription.trim()) {
      setError("Veuillez entrer une description de ton.");
      return;
    }

    try {
      setIsAnalyzing(true);
      setError("");
      
      const response = await fetch("http://localhost:8000/analyze-tone", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: customToneDescription }),
      });

      if (!response.ok) {
        throw new Error(`Erreur lors de l'analyse: ${response.status}`);
      }
      const data = await response.json();
      setToneAnalysis(data);
      
      onToneSelect({
        tone_description: data.tone_description,
        tone_example: customToneExample,
        brand_name: customBrandName,
        persona_target: customPersonaTarget
      });
      
    } catch (error) {
      console.error("Erreur lors de l'analyse du ton:", error);
      setError(`Erreur lors de l'analyse: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleTabChange = (value: string) => {
    setActiveTab(value);
    
    if (value === "predefined" && selectedTone) {
      // Quand on revient à l'onglet prédéfini, on applique le ton sélectionné
      const selectedPredefinedTone = predefinedTones.find((tone) => tone.id === selectedTone);
      if (selectedPredefinedTone) {
        handleToneSelect(selectedPredefinedTone);
      }
    }
    // On ne fait plus de onToneSelect automatique quand on passe à l'onglet personnalisé
  };
  
  // Nouvelle fonction pour appliquer le ton personnalisé
  const applyCustomTone = () => {
    onToneSelect({
      predefined_tone_id: "custom",
      tone_description: customToneDescription,
      tone_example: customToneExample,
      brand_name: customBrandName,
      persona_target: customPersonaTarget
    });
  };

  return (
    <div className="w-full space-y-4">
      <h2 className="text-2xl font-semibold mb-4">Ton éditorial</h2>
      
      <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="predefined">Tons prédéfinis</TabsTrigger>
          <TabsTrigger value="custom">Ton personnalisé</TabsTrigger>
        </TabsList>
        
        {/* Onglet des tons prédéfinis */}
        <TabsContent value="predefined" className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {predefinedTones.map((tone) => (
              <div 
                key={tone.id}
                className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedTone === tone.id 
                    ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20" 
                    : "border-gray-200 hover:border-blue-300 dark:border-gray-700"
                }`}
                onClick={() => handleToneSelect(tone)}
              >
                <h3 className="font-medium text-lg mb-2">{tone.name}</h3>
                <p className="text-gray-600 dark:text-gray-300 text-sm mb-3">{tone.description}</p>
                
                <div className="space-y-1 mb-3">
                  <h4 className="text-xs font-medium text-gray-500 dark:text-gray-400">Caractéristiques:</h4>
                  <ul className="text-xs text-gray-600 dark:text-gray-300 pl-4 list-disc">
                    {tone.characteristics ? tone.characteristics.slice(0, 3).map((char: string, index: number) => (
                      <li key={index}>{char}</li>
                    )) : <li>Aucune caractéristique spécifiée</li>}
                    {tone.characteristics && tone.characteristics.length > 3 && <li>...</li>}
                  </ul>
                </div>
                
                <div className="text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded border border-gray-200 dark:border-gray-700 line-clamp-3">
                  <span className="italic">Exemple: </span>
                  {tone.tone_example.substring(0, 100)}...
                </div>
                
                <div className="text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded border border-gray-200 dark:border-gray-700 line-clamp-3">
                  <span className="italic">Persona cible: </span>
                  {tone.persona_target}
                </div>
              </div>
            ))}
          </div>
        </TabsContent>
        
        {/* Onglet du ton personnalisé */}
        <TabsContent value="custom" className="space-y-4">
          <div className="space-y-4">
            <div>
              <label htmlFor="customBrandName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Nom de la marque (optionnel)
              </label>
              <input
                type="text"
                id="customBrandName"
                value={customBrandName}
                onChange={(e) => {
                  setCustomBrandName(e.target.value);
                }}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                placeholder="ex: Apple, Nike, votre marque..."
              />
            </div>
            
            <div>
              <label htmlFor="customToneDescription" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Description du ton
              </label>
              <textarea
                id="customToneDescription"
                value={customToneDescription}
                onChange={(e) => {
                  setCustomToneDescription(e.target.value);
                }}
                rows={2}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                placeholder="ex: Ton professionnel mais chaleureux, avec une touche d'humour..."
              />
            </div>
            
            <div>
              <label htmlFor="customToneExample" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Exemple de ton (optionnel)
              </label>
              <textarea
                id="customToneExample"
                value={customToneExample}
                onChange={(e) => {
                  setCustomToneExample(e.target.value);
                }}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                placeholder="ex: Notre produit vous offre une expérience unique qui combine simplicité et puissance..."
              />
            </div>
            
            <div>
              <label htmlFor="customPersonaTarget" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Persona cible (optionnel)
              </label>
              <textarea
                id="customPersonaTarget"
                value={customPersonaTarget}
                onChange={(e) => {
                  setCustomPersonaTarget(e.target.value);
                }}
                rows={2}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                placeholder="ex: Professionnels du secteur, débutants, experts techniques..."
              />
            </div>
            
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}
            
            <div className="flex space-x-2">
              <button
                type="button"
                onClick={applyCustomTone}
                disabled={!(customToneDescription && customToneDescription.trim())}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-300 text-white rounded-lg transition-colors"
              >
                Appliquer ce ton
              </button>
              
              <button
                type="button"
                onClick={handleAnalyzeCustomText}
                disabled={isAnalyzing || !(customToneDescription && customToneDescription.trim())}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white rounded-lg transition-colors"
              >
                {isAnalyzing ? "Analyse en cours..." : "Analyser le ton"}
              </button>
            </div>
            
            {toneAnalysis && (
              <div className="mt-6 border border-green-200 rounded-lg p-4 bg-green-50 dark:bg-green-900/20 dark:border-green-800">
                <h3 className="font-medium text-lg mb-2 text-green-800 dark:text-green-300">Analyse du ton</h3>
                
                <div className="space-y-3">
                  <div>
                    <h4 className="text-sm font-medium text-green-700 dark:text-green-400">Description</h4>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{toneAnalysis.tone_description}</p>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-green-700 dark:text-green-400">Style d'écriture</h4>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{toneAnalysis.writing_style}</p>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-green-700 dark:text-green-400">Caractéristiques</h4>
                    <ul className="text-sm text-gray-700 dark:text-gray-300 pl-4 list-disc">
                      {toneAnalysis.tone_characteristics.map((char, index) => (
                        <li key={index}>{char}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-medium text-green-700 dark:text-green-400">Niveau de vocabulaire</h4>
                      <p className="text-sm text-gray-700 dark:text-gray-300">{toneAnalysis.vocabulary_level}</p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-green-700 dark:text-green-400">Structure des phrases</h4>
                      <p className="text-sm text-gray-700 dark:text-gray-300">{toneAnalysis.sentence_structure}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ToneSelector;
