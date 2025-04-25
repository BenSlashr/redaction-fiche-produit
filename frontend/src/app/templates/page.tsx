"use client";

import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, CheckCircle2, Plus, Trash2, Copy, Edit } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/components/ui/use-toast";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

// Types pour les templates
interface Section {
  id: string;
  name: string;
  description: string;
  required: boolean;
  default_enabled: boolean;
  order: number;
  rag_query_template: string;
  prompt_template: string;
}

interface Template {
  id: string;
  name: string;
  description: string;
  sections: Section[];
  is_default: boolean;
  is_custom: boolean;
}

interface TemplatesResponse {
  templates: Template[];
}

const TemplateManager = () => {
  const { toast } = useToast();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [activeTemplate, setActiveTemplate] = useState<Template | null>(null);
  const [editedTemplate, setEditedTemplate] = useState<Template | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState<boolean>(false);
  const [newTemplateName, setNewTemplateName] = useState<string>("");
  const [newTemplateDescription, setNewTemplateDescription] = useState<string>("");
  const [baseTemplateId, setBaseTemplateId] = useState<string>("");

  // Charger tous les templates au chargement de la page
  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Appel à l'API backend
      const response = await fetch('http://127.0.0.1:8050/templates', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      });
      
      if (!response.ok) {
        throw new Error(`Erreur lors du chargement des templates: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Convertir l'objet en tableau
      const templatesArray = data.templates;
      setTemplates(templatesArray);
      
      // Si aucun template actif n'est sélectionné, sélectionner le premier
      if (templatesArray.length > 0 && !activeTemplate) {
        setActiveTemplate(templatesArray[0]);
        setEditedTemplate(JSON.parse(JSON.stringify(templatesArray[0])));
      }
      
    } catch (err) {
      setError(`Erreur lors du chargement des templates: ${err instanceof Error ? err.message : String(err)}`);
      toast({
        title: "Erreur",
        description: "Impossible de charger les templates. Veuillez réessayer.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTemplateChange = (template: Template) => {
    setActiveTemplate(template);
    setEditedTemplate(JSON.parse(JSON.stringify(template)));
  };

  const handleSectionChange = (index: number, field: keyof Section, value: any) => {
    if (!editedTemplate) return;
    
    const updatedSections = [...editedTemplate.sections];
    updatedSections[index] = {
      ...updatedSections[index],
      [field]: value
    };
    
    setEditedTemplate({
      ...editedTemplate,
      sections: updatedSections
    });
  };

  const addSection = () => {
    if (!editedTemplate || !editedTemplate.is_custom) return;
    
    const newSectionId = `section_${Date.now()}`;
    const newSection: Section = {
      id: newSectionId,
      name: "Nouvelle section",
      description: "Description de la nouvelle section",
      required: false,
      default_enabled: true,
      order: editedTemplate.sections.length + 1,
      rag_query_template: "informations sur {product_name} dans la catégorie {product_category}",
      prompt_template: "Générer une section sur {product_name} en utilisant les informations suivantes: {client_data_context}"
    };
    
    setEditedTemplate({
      ...editedTemplate,
      sections: [...editedTemplate.sections, newSection]
    });
    
    toast({
      title: "Section ajoutée",
      description: "Une nouvelle section a été ajoutée au template.",
    });
  };

  const deleteSection = (index: number) => {
    if (!editedTemplate || !editedTemplate.is_custom) return;
    
    // Vérifier si la section est obligatoire
    if (editedTemplate.sections[index].required) {
      toast({
        title: "Action impossible",
        description: "Impossible de supprimer une section obligatoire.",
        variant: "destructive"
      });
      return;
    }
    
    const updatedSections = [...editedTemplate.sections];
    updatedSections.splice(index, 1);
    
    // Mettre à jour l'ordre des sections
    updatedSections.forEach((section, idx) => {
      section.order = idx + 1;
    });
    
    setEditedTemplate({
      ...editedTemplate,
      sections: updatedSections
    });
    
    toast({
      title: "Section supprimée",
      description: "La section a été supprimée du template.",
    });
  };

  const handleSave = async () => {
    if (!editedTemplate) return;
    
    try {
      setIsSaving(true);
      setError(null);
      setSuccess(null);
      
      // Vérifier que toutes les sections ont les champs requis
      const validatedSections = editedTemplate.sections.map(section => {
        // S'assurer que tous les champs requis sont présents
        return {
          id: section.id,
          name: section.name || "Section sans nom",
          description: section.description || "Description de la section",
          required: section.required !== undefined ? section.required : false,
          default_enabled: section.default_enabled !== undefined ? section.default_enabled : true,
          order: section.order !== undefined ? section.order : 0,
          rag_query_template: section.rag_query_template || "informations sur {product_name} dans la catégorie {product_category}",
          prompt_template: section.prompt_template || "Générer une section sur {product_name} en utilisant les informations suivantes: {client_data_context}"
        };
      });
      
      // Déterminer si nous créons un nouveau template ou mettons à jour un existant
      // Si le template n'a pas d'ID ou si l'ID ne commence pas par 'custom_', c'est un nouveau template
      const isNewTemplate = !editedTemplate.id || !editedTemplate.id.startsWith('custom_');
      
      // Appel à l'API backend
      const url = !isNewTemplate
        ? `http://127.0.0.1:8050/templates/${editedTemplate.id}`
        : 'http://127.0.0.1:8050/templates';
      
      const method = !isNewTemplate ? 'PUT' : 'POST';
      
      // Log pour déboguer
      console.log('Sauvegarde du template:', {
        url,
        method,
        isNewTemplate,
        template: {
          id: editedTemplate.id,
          name: editedTemplate.name,
          description: editedTemplate.description,
          is_custom: editedTemplate.is_custom,
          is_default: editedTemplate.is_default,
          sections: validatedSections.length
        }
      });
      
      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: editedTemplate.name,
          description: editedTemplate.description,
          sections: validatedSections,
          is_default: editedTemplate.is_default
        }),
      });
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Pas de détails disponibles');
        console.error('Erreur de sauvegarde:', {
          status: response.status,
          statusText: response.statusText,
          details: errorText
        });
        throw new Error(`Erreur lors de la sauvegarde: ${response.status} - ${errorText}`);
      }
      
      const savedTemplate = await response.json();
      
      // S'assurer que le champ is_custom est correctement défini
      // Les templates personnalisés ont un ID qui commence par 'custom_'
      const isCustomTemplate = savedTemplate.id && savedTemplate.id.startsWith('custom_');
      savedTemplate.is_custom = isCustomTemplate;
      
      console.log('Template sauvegardé:', {
        savedTemplate,
        isCustomTemplate
      });
      
      // Mettre à jour la liste des templates
      await fetchTemplates();
      
      // Mettre à jour le template actif avec le champ is_custom correctement défini
      setActiveTemplate(savedTemplate);
      setEditedTemplate(JSON.parse(JSON.stringify(savedTemplate)));
      
      setSuccess("Template sauvegardé avec succès");
      toast({
        title: "Succès",
        description: "Le template a été sauvegardé avec succès.",
      });
      
    } catch (err) {
      setError(`Erreur lors de la sauvegarde: ${err instanceof Error ? err.message : String(err)}`);
      toast({
        title: "Erreur",
        description: "Impossible de sauvegarder le template. Veuillez réessayer.",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!activeTemplate || !activeTemplate.is_custom) return;
    
    try {
      setIsDeleting(true);
      setError(null);
      setSuccess(null);
      
      // Appel à l'API backend
      const response = await fetch(`http://127.0.0.1:8050/templates/${activeTemplate.id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Erreur lors de la suppression: ${response.status}`);
      }
      
      // Mettre à jour la liste des templates
      await fetchTemplates();
      
      // Réinitialiser le template actif
      setActiveTemplate(null);
      setEditedTemplate(null);
      
      setSuccess("Template supprimé avec succès");
      toast({
        title: "Succès",
        description: "Le template a été supprimé avec succès.",
      });
      
    } catch (err) {
      setError(`Erreur lors de la suppression: ${err instanceof Error ? err.message : String(err)}`);
      toast({
        title: "Erreur",
        description: "Impossible de supprimer le template. Veuillez réessayer.",
        variant: "destructive",
      });
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCreateTemplate = async () => {
    try {
      if (!newTemplateName.trim()) {
        toast({
          title: "Erreur",
          description: "Le nom du template est requis.",
          variant: "destructive",
        });
        return;
      }
      
      // Trouver le template de base
      const baseTemplate = templates.find(t => t.id === baseTemplateId) || templates[0];
      
      // Créer un nouveau template basé sur le template sélectionné
      const newTemplate: Omit<Template, 'id' | 'is_custom'> = {
        name: newTemplateName,
        description: newTemplateDescription || `Template personnalisé basé sur ${baseTemplate.name}`,
        sections: JSON.parse(JSON.stringify(baseTemplate.sections)),
        is_default: false
      };
      
      // Fermer la boîte de dialogue
      setShowCreateDialog(false);
      
      // Créer le template dans l'éditeur
      const templateWithCustomProps = {
        ...newTemplate,
        id: 'new_template',
        is_custom: true
      };
      
      setActiveTemplate(templateWithCustomProps as Template);
      setEditedTemplate(templateWithCustomProps as Template);
      
      // Réinitialiser les champs
      setNewTemplateName("");
      setNewTemplateDescription("");
      setBaseTemplateId("");
      
    } catch (err) {
      setError(`Erreur lors de la création du template: ${err instanceof Error ? err.message : String(err)}`);
      toast({
        title: "Erreur",
        description: "Impossible de créer le template. Veuillez réessayer.",
        variant: "destructive",
      });
    }
  };

  // Rendu du squelette de chargement
  if (isLoading) {
    return (
      <div className="container mx-auto py-8">
        <h1 className="text-3xl font-bold mb-6">Gestion des Templates de Fiches Produit</h1>
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
      <h1 className="text-3xl font-bold mb-6">Gestion des Templates de Fiches Produit</h1>
      
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
        {/* Liste des templates */}
        <div className="md:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Templates disponibles</CardTitle>
              <CardDescription>Sélectionnez un template à modifier</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col space-y-2">
                {templates.map((template) => (
                  <Button
                    key={template.id}
                    variant={activeTemplate?.id === template.id ? "default" : "outline"}
                    onClick={() => handleTemplateChange(template)}
                    className="justify-start text-left"
                  >
                    <span className="truncate">{template.name}</span>
                    {template.is_custom && (
                      <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-1 py-0.5 rounded">
                        Personnalisé
                      </span>
                    )}
                  </Button>
                ))}
              </div>
            </CardContent>
            <CardFooter>
              <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                <DialogTrigger asChild>
                  <Button className="w-full">
                    <Plus className="mr-2 h-4 w-4" />
                    Nouveau template
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Créer un nouveau template</DialogTitle>
                    <DialogDescription>
                      Créez un nouveau template basé sur un template existant.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="templateName">Nom du template</Label>
                      <Input
                        id="templateName"
                        value={newTemplateName}
                        onChange={(e) => setNewTemplateName(e.target.value)}
                        placeholder="Nom du template"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="templateDescription">Description</Label>
                      <Textarea
                        id="templateDescription"
                        value={newTemplateDescription}
                        onChange={(e) => setNewTemplateDescription(e.target.value)}
                        placeholder="Description du template"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="baseTemplate">Template de base</Label>
                      <select
                        id="baseTemplate"
                        value={baseTemplateId}
                        onChange={(e) => setBaseTemplateId(e.target.value)}
                        className="w-full p-2 border rounded"
                      >
                        <option value="">Sélectionnez un template de base</option>
                        {templates.map((template) => (
                          <option key={template.id} value={template.id}>
                            {template.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <DialogFooter>
                    <DialogClose asChild>
                      <Button variant="outline">Annuler</Button>
                    </DialogClose>
                    <Button onClick={handleCreateTemplate}>Créer</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </CardFooter>
          </Card>
        </div>

        {/* Éditeur de template */}
        <div className="md:col-span-3">
          {activeTemplate && editedTemplate ? (
            <Card>
              <CardHeader>
                <CardTitle>
                  {editedTemplate.is_custom ? "Modifier le template" : "Détails du template"}
                </CardTitle>
                <CardDescription>
                  {editedTemplate.is_custom 
                    ? "Personnalisez le template selon vos besoins" 
                    : "Les templates par défaut ne peuvent pas être modifiés"}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label htmlFor="templateName" className="block text-sm font-medium mb-1">
                    Nom du template
                  </label>
                  <Input
                    id="templateName"
                    value={editedTemplate.name}
                    onChange={(e) => setEditedTemplate({...editedTemplate, name: e.target.value})}
                    placeholder="Nom du template"
                    disabled={!editedTemplate.is_custom}
                  />
                </div>
                <div>
                  <label htmlFor="templateDescription" className="block text-sm font-medium mb-1">
                    Description
                  </label>
                  <Textarea
                    id="templateDescription"
                    value={editedTemplate.description}
                    onChange={(e) => setEditedTemplate({...editedTemplate, description: e.target.value})}
                    placeholder="Description du template"
                    disabled={!editedTemplate.is_custom}
                  />
                </div>
                
                <Separator className="my-4" />
                
                <div>
                  <h3 className="text-lg font-semibold mb-2">Sections du template</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Chaque section peut avoir sa propre requête RAG et son propre prompt.
                  </p>
                  
                  <Accordion type="single" collapsible className="w-full">
                    {editedTemplate.sections.map((section, index) => (
                      <AccordionItem key={section.id} value={section.id}>
                        <div className="border-b">
                          <div className="flex">
                            <div 
                              className="flex flex-1 items-center justify-between py-4 font-medium transition-all hover:underline"
                              onClick={() => {
                                const accordionElement = document.getElementById(`accordion-${section.id}`);
                                if (accordionElement) accordionElement.click();
                              }}
                            >
                              <div className="flex items-center justify-between w-full">
                                <div className="flex items-center">
                                  <span>{section.name}</span>
                                  {section.required && (
                                    <span className="ml-2 text-xs bg-red-100 text-red-800 px-1 py-0.5 rounded">
                                      Obligatoire
                                    </span>
                                  )}
                                </div>
                                <div className="flex items-center">
                                  {editedTemplate.is_custom && !section.required && (
                                    <Button 
                                      variant="ghost" 
                                      size="sm" 
                                      className="text-red-500 hover:text-red-700 hover:bg-red-50 mr-2"
                                      onClick={(e) => {
                                        e.stopPropagation(); // Empêcher l'ouverture/fermeture de l'accordion
                                        deleteSection(index);
                                      }}
                                    >
                                      <Trash2 className="h-4 w-4" />
                                    </Button>
                                  )}
                                  <ChevronDown className="h-4 w-4 shrink-0 transition-transform duration-200" />
                                </div>
                              </div>
                            </div>
                            <button 
                              id={`accordion-${section.id}`}
                              className="hidden"
                              onClick={() => {
                                // Cette fonction sera appelée par le div ci-dessus
                              }}
                            />
                          </div>
                        </div>
                        <AccordionContent>
                          <div className="space-y-4 p-2">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <label className="block text-sm font-medium mb-1">
                                  Nom de la section
                                </label>
                                <Input
                                  value={section.name}
                                  onChange={(e) => handleSectionChange(index, 'name', e.target.value)}
                                  disabled={!editedTemplate.is_custom}
                                />
                              </div>
                              <div>
                                <label className="block text-sm font-medium mb-1">
                                  ID de la section
                                </label>
                                <Input
                                  value={section.id}
                                  disabled={true}
                                />
                              </div>
                            </div>
                            
                            <div>
                              <label className="block text-sm font-medium mb-1">
                                Description
                              </label>
                              <Input
                                value={section.description}
                                onChange={(e) => handleSectionChange(index, 'description', e.target.value)}
                                disabled={!editedTemplate.is_custom}
                              />
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                              <div className="flex items-center space-x-2">
                                <Switch
                                  id={`required-${section.id}`}
                                  checked={section.required}
                                  onCheckedChange={(checked) => handleSectionChange(index, 'required', checked)}
                                  disabled={!editedTemplate.is_custom}
                                />
                                <Label htmlFor={`required-${section.id}`}>Obligatoire</Label>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Switch
                                  id={`enabled-${section.id}`}
                                  checked={section.default_enabled}
                                  onCheckedChange={(checked) => handleSectionChange(index, 'default_enabled', checked)}
                                  disabled={!editedTemplate.is_custom}
                                />
                                <Label htmlFor={`enabled-${section.id}`}>Activé par défaut</Label>
                              </div>
                              <div>
                                <label className="block text-sm font-medium mb-1">
                                  Ordre
                                </label>
                                <Input
                                  type="number"
                                  value={section.order}
                                  onChange={(e) => handleSectionChange(index, 'order', parseInt(e.target.value))}
                                  disabled={!editedTemplate.is_custom}
                                />
                              </div>
                            </div>
                            
                            <div className="bg-blue-50 p-4 rounded-md border border-blue-200">
                              <h4 className="font-bold text-blue-800 mb-2">Requête RAG</h4>
                              <p className="text-sm text-blue-700 mb-2">
                                Cette requête est utilisée pour extraire les informations pertinentes des documents clients.
                                Vous pouvez utiliser les variables {"{product_name}"} et {"{product_category}"}.
                              </p>
                              <Textarea
                                value={section.rag_query_template}
                                onChange={(e) => handleSectionChange(index, 'rag_query_template', e.target.value)}
                                className="min-h-[100px] font-mono"
                                disabled={!editedTemplate.is_custom}
                              />
                            </div>
                            
                            <div className="bg-green-50 p-4 rounded-md border border-green-200">
                              <h4 className="font-bold text-green-800 mb-2">Prompt de génération</h4>
                              <p className="text-sm text-green-700 mb-2">
                                Ce prompt est utilisé pour générer le contenu de cette section.
                                Il reçoit les informations extraites par la requête RAG.
                              </p>
                              <Textarea
                                value={section.prompt_template}
                                onChange={(e) => handleSectionChange(index, 'prompt_template', e.target.value)}
                                className="min-h-[150px] font-mono"
                                disabled={!editedTemplate.is_custom}
                              />
                            </div>
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                  
                  {/* Bouton pour ajouter une nouvelle section */}
                  {editedTemplate.is_custom && (
                    <Button 
                      className="mt-4 w-full" 
                      variant="outline" 
                      onClick={addSection}
                    >
                      <Plus className="mr-2 h-4 w-4" />
                      Ajouter une nouvelle section
                    </Button>
                  )}
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                {editedTemplate.is_custom && (
                  <>
                    <Button 
                      variant="destructive" 
                      onClick={handleDelete}
                      disabled={isDeleting}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      {isDeleting ? "Suppression..." : "Supprimer"}
                    </Button>
                    <Button 
                      onClick={handleSave}
                      disabled={isSaving}
                    >
                      {isSaving ? "Sauvegarde en cours..." : "Sauvegarder"}
                    </Button>
                  </>
                )}
                {!editedTemplate.is_custom && (
                  <Button 
                    onClick={() => {
                      // Créer une copie du template par défaut
                      const copy = JSON.parse(JSON.stringify(editedTemplate));
                      copy.id = 'new_template';
                      copy.is_custom = true;
                      copy.name = `Copie de ${copy.name}`;
                      setActiveTemplate(copy);
                      setEditedTemplate(copy);
                    }}
                  >
                    <Copy className="mr-2 h-4 w-4" />
                    Dupliquer ce template
                  </Button>
                )}
              </CardFooter>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-10">
                <p className="text-center text-muted-foreground">
                  Sélectionnez un template à modifier ou créez-en un nouveau
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Guide d'utilisation des templates</h2>
        <Card>
          <CardContent className="py-6">
            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold mb-2">Qu'est-ce qu'un template de fiche produit ?</h3>
                <p className="mb-2">
                  Un template de fiche produit définit la structure et le contenu d'une fiche produit générée.
                  Il est composé de plusieurs sections, chacune avec sa propre requête RAG et son propre prompt.
                </p>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold mb-2">Optimisation des requêtes RAG</h3>
                <p className="mb-2">
                  Chaque section peut avoir sa propre requête RAG, qui est utilisée pour extraire les informations pertinentes
                  des documents clients. Voici quelques conseils pour optimiser vos requêtes RAG :
                </p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Utilisez des termes spécifiques liés à la section (ex: "dimensions", "matériaux", "avantages")</li>
                  <li>Incluez des synonymes pour couvrir différentes formulations</li>
                  <li>Utilisez les variables {"{product_name}"} et {"{product_category}"} pour contextualiser la requête</li>
                  <li>Pour les caractéristiques techniques, soyez précis sur les types d'informations recherchées</li>
                  <li>Pour les avantages, incluez des termes comme "bénéfices", "points forts", "avantages"</li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold mb-2">Variables disponibles dans les requêtes RAG</h3>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Variable</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Exemple</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell><code>{"{product_name}"}</code></TableCell>
                      <TableCell>Nom du produit</TableCell>
                      <TableCell>"Chaise ergonomique X200"</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell><code>{"{product_category}"}</code></TableCell>
                      <TableCell>Catégorie du produit</TableCell>
                      <TableCell>"Mobilier de bureau"</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
              
              <div className="bg-yellow-50 p-4 rounded-md border border-yellow-200">
                <h4 className="font-bold text-yellow-800 mb-2">Exemple de requête RAG optimisée</h4>
                <p className="text-sm text-yellow-700 mb-2">
                  Pour une section "Caractéristiques techniques" :
                </p>
                <pre className="bg-white p-3 rounded-md border border-gray-200 font-mono text-sm whitespace-pre-wrap">
                  spécifications techniques détaillées de {"{product_name}"} incluant dimensions, poids, matériaux, 
                  capacité, puissance, consommation, normes, certifications, compatibilité, 
                  exigences techniques, caractéristiques physiques
                </pre>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TemplateManager;
