# Guide d'optimisation des requêtes RAG pour les templates de fiches produit

Ce guide vous aidera à optimiser les requêtes RAG (Retrieval Augmented Generation) dans vos templates de fiches produit pour obtenir des résultats plus pertinents et exhaustifs.

## Qu'est-ce que le RAG ?

Le RAG (Retrieval Augmented Generation) est une technique qui combine la recherche d'informations et la génération de texte. Dans notre système :

1. Une **requête RAG** est utilisée pour rechercher des informations pertinentes dans vos documents clients
2. Les informations récupérées sont injectées dans un **prompt** qui est envoyé à l'IA
3. L'IA génère du contenu en se basant sur ces informations

## Structure d'un template de fiche produit

Un template de fiche produit est composé de plusieurs sections, chacune avec :

- Un **identifiant unique** (id)
- Un **nom** et une **description**
- Une **requête RAG** spécifique (`rag_query_template`)
- Un **prompt de génération** (`prompt_template`)

## Optimisation des requêtes RAG

### Principes généraux

1. **Soyez spécifique** : Plus votre requête est précise, plus les résultats seront pertinents
2. **Utilisez des synonymes** : Incluez différentes formulations pour couvrir toutes les possibilités
3. **Contextualisez** : Utilisez les variables `{product_name}` et `{product_category}` pour adapter la requête au produit
4. **Pensez aux termes techniques** : Incluez des termes spécifiques à votre domaine

### Variables disponibles

| Variable | Description | Exemple |
|----------|-------------|---------|
| `{product_name}` | Nom du produit | "Chaise ergonomique X200" |
| `{product_category}` | Catégorie du produit | "Mobilier de bureau" |

### Exemples de requêtes optimisées par type de section

#### Section "Introduction"

```
présentation générale et contexte d'utilisation de {product_name} dans la catégorie {product_category}, 
positionnement sur le marché, public cible, gamme de produits, marque
```

#### Section "Caractéristiques techniques"

```
spécifications techniques détaillées de {product_name} incluant dimensions, poids, matériaux, 
capacité, puissance, consommation, normes, certifications, compatibilité, 
exigences techniques, caractéristiques physiques, composants, technologie utilisée
```

#### Section "Avantages et bénéfices"

```
avantages, bénéfices, points forts et atouts de {product_name} par rapport à la concurrence,
valeur ajoutée, caractéristiques distinctives, innovations, solutions apportées,
problèmes résolus, améliorations par rapport aux modèles précédents
```

#### Section "Installation et mise en service"

```
instructions d'installation et de mise en service de {product_name}, prérequis, étapes,
outils nécessaires, temps d'installation, précautions, conseils de montage,
branchements, configuration initiale, démarrage
```

#### Section "Entretien et maintenance"

```
conseils d'entretien et de maintenance pour {product_name}, fréquence, méthodes,
produits recommandés, nettoyage, remplacement des pièces, durabilité,
procédures de maintenance préventive, prolongation de la durée de vie
```

## Stratégies avancées d'optimisation

### 1. Segmentation par aspects

Divisez votre requête en différents aspects du produit pour une couverture complète :

```
caractéristiques techniques de {product_name} concernant : 
1. dimensions et poids 
2. matériaux et composition 
3. performance et capacité 
4. normes et certifications
```

### 2. Requêtes ciblées par type de document

Adaptez vos requêtes selon les types de documents que vous avez importés :

```
spécifications techniques de {product_name} dans les fiches techniques, 
manuels d'utilisation et catalogues produits
```

### 3. Utilisation de termes techniques spécifiques

Incluez des termes techniques spécifiques à votre industrie :

```
// Pour des produits électroniques
spécifications de {product_name} incluant résolution, fréquence de rafraîchissement, 
connectique, consommation énergétique, compatibilité HDMI/DisplayPort
```

## Évaluation et amélioration continue

Pour évaluer l'efficacité de vos requêtes RAG :

1. **Testez différentes formulations** et comparez les résultats
2. **Analysez les informations manquantes** dans les fiches générées
3. **Enrichissez progressivement** vos requêtes avec des termes plus précis
4. **Documentez les requêtes efficaces** pour chaque type de produit

## Exemples de templates complets

### Template pour produits techniques

```
{
  "id": "technical_product",
  "name": "Produit technique",
  "description": "Template optimisé pour les produits techniques avec spécifications détaillées",
  "sections": [
    {
      "id": "introduction",
      "name": "Introduction",
      "rag_query_template": "présentation générale et contexte d'utilisation de {product_name}, positionnement, public cible"
    },
    {
      "id": "technical_specs",
      "name": "Caractéristiques techniques",
      "rag_query_template": "spécifications techniques détaillées de {product_name} incluant dimensions, poids, matériaux, capacité, puissance, consommation, normes, certifications, compatibilité"
    },
    {
      "id": "benefits",
      "name": "Avantages",
      "rag_query_template": "avantages, bénéfices et points forts de {product_name}, innovations, solutions apportées"
    }
  ]
}
```

## Conclusion

L'optimisation des requêtes RAG est un processus itératif qui s'améliore avec le temps et l'expérience. En suivant ces conseils et en expérimentant différentes approches, vous pourrez obtenir des fiches produit plus précises, plus complètes et mieux adaptées à vos besoins spécifiques.

N'hésitez pas à personnaliser vos templates et à créer des requêtes RAG spécifiques pour chaque type de produit dans votre catalogue.
