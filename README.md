# RFP - Générateur de Fiches Produit

## Guide de démarrage rapide

### Prérequis
- Python 3.10+ (`python --version` pour vérifier)
- Node.js 18+ (`node --version` pour vérifier)
- npm 9+ (`npm --version` pour vérifier)
- Clés API :
  - [OpenAI API](https://platform.openai.com/api-keys) (obligatoire)
  - [THOT SEO API](https://thot-seo.fr/) (obligatoire pour les fonctionnalités SEO)
  - [ValueSERP API](https://www.valueserp.com/) (optionnelle, pour l'analyse concurrentielle)

### Installation en 5 minutes

#### 1. Cloner le dépôt
```bash
git clone <URL_DU_REPO> rfp
cd rfp
```

#### 2. Configurer le backend
```bash
cd backend

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier .env
echo "OPENAI_API_KEY=votre_clé_openai" > .env
echo "THOT_API_KEY=votre_clé_thot" >> .env
echo "VALUESERP_API_KEY=votre_clé_valueserp" >> .env

# Lancer le serveur backend
/Users/benoit/rfp/backend/venv/bin/python -m uvicorn main:app --reload --port 8050
```
Le backend sera disponible sur http://localhost:8050

#### 3. Configurer le frontend (dans un nouveau terminal)
```bash
cd frontend

# Installer les dépendances
npm install

# Créer le fichier .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Lancer le serveur frontend
npm run dev
```
Le frontend sera disponible sur http://localhost:3000

#### 4. Vérifier l'installation
- Ouvrir http://localhost:3000 dans votre navigateur
- Tester la génération d'une description de produit simple
- Vérifier que toutes les fonctionnalités sont opérationnelles

## Structure du projet

```
rfp/
├── backend/                 # API FastAPI
│   ├── services/            # Services métier
│   │   ├── langchain_service.py       # Générateur de descriptions
│   │   ├── self_improving_chain.py    # Chaîne d'auto-amélioration
│   │   ├── thot_seo_service.py        # Service SEO
│   │   ├── competitor_analyzer.py     # Analyse concurrentielle
│   │   ├── specs_extractor.py         # Extraction de spécifications
│   │   ├── batch_processor.py         # Traitement par lot
│   │   └── prompt_manager.py          # Gestion des prompts
│   ├── prompts/             # Templates de prompts
│   ├── main.py              # Point d'entrée de l'API
│   ├── requirements.txt     # Dépendances Python
│   └── .env                 # Variables d'environnement
│
├── frontend/                # Application Next.js
│   ├── src/
│   │   ├── app/             # Pages de l'application
│   │   │   ├── page.tsx     # Page principale (génération individuelle)
│   │   │   └── batch/       # Page de génération par lot
│   │   ├── components/      # Composants réutilisables
│   │   │   ├── ui/          # Composants UI de base
│   │   │   └── specs-extractor/ # Extracteur de spécifications
│   │   └── lib/             # Utilitaires et services
│   ├── package.json         # Dépendances JavaScript
│   └── .env.local           # Variables d'environnement
│
└── README.md                # Documentation principale
```

## Présentation du projet

RFP (Rédacteur de Fiches Produit) est une application web complète qui permet de générer automatiquement des descriptions de produits de haute qualité, optimisées pour le SEO et adaptées à différents publics cibles. L'application utilise des modèles d'IA avancés pour produire des descriptions professionnelles à partir d'informations de base sur les produits.

## Fonctionnalités principales

### 1. Génération de descriptions de produits
- Génération de descriptions détaillées et persuasives
- Intégration des spécifications techniques
- Personnalisation du ton et du style
- Optimisation SEO automatique
- Suggestions d'amélioration SEO
- Utilisation de templates de produits personnalisables

### 2. Ciblage de persona
- Adaptation du contenu à différents publics cibles
- Personas prédéfinis (professionnel, débutant, expert, entreprise, particulier)
- Personnalisation des personas

### 3. Analyse concurrentielle
- Analyse automatique des produits concurrents
- Extraction des arguments de vente uniques
- Identification des caractéristiques clés à mettre en avant
- Analyse des mots-clés utilisés par la concurrence

### 4. Guide SEO
- Recommandations SEO spécifiques au produit
- Suggestions de mots-clés et d'expressions à inclure
- Analyse des questions fréquentes à aborder
- Recommandations sur la longueur du contenu

### 5. Extraction automatique de spécifications
- Extraction de spécifications techniques à partir de texte brut
- Support de différents formats (tableaux, listes, etc.)
- Prévisualisation des spécifications extraites

### 6. Traitement par lot
- Génération simultanée de multiples descriptions
- Import de données produits via CSV
- Suivi de progression en temps réel
- Conservation de toutes les options de personnalisation

## Architecture technique

### Backend (Python/FastAPI)
- **FastAPI** : Framework API rapide et moderne
- **LangChain** : Orchestration des modèles d'IA et des chaînes de traitement
- **OpenAI API** : Modèles de langage avancés (GPT-4o)
- **THOT SEO API** : Analyse et recommandations SEO
- **ValueSERP API** : Analyse des résultats de recherche et de la concurrence

#### Services principaux
- `ProductDescriptionGenerator` : Génération de descriptions de produits
- `SelfImprovingChain` : Amélioration automatique des descriptions
- `ThotSeoService` : Intégration avec l'API THOT SEO
- `CompetitorAnalyzer` : Analyse des produits concurrents
- `SpecsExtractor` : Extraction de spécifications techniques
- `BatchProcessor` : Traitement par lot des descriptions
- `TemplateService` : Gestion des templates de fiches produit

### Frontend (Next.js/React)
- **Next.js** : Framework React avec rendu côté serveur
- **Tailwind CSS** : Styling moderne et responsive
- **shadcn/ui** : Composants UI réutilisables
- **React Hook Form** : Gestion des formulaires
- **Axios** : Communication avec l'API backend

#### Pages principales
- `/` : Génération individuelle de descriptions
- `/batch` : Génération par lot via CSV
- `/history` : Historique des descriptions générées
- `/settings` : Configuration de l'application

## Guide d'utilisation

### Génération individuelle
1. Accéder à la page d'accueil
2. Remplir les informations du produit :
   - Nom du produit
   - Description brève
   - Catégorie
   - Mots-clés
   - Spécifications techniques
3. Personnaliser les options :
   - Ton et style
   - Persona cible
   - Optimisation SEO
   - Analyse concurrentielle
   - Guide SEO
   - Utilisation de templates (optionnel)
4. Si l'option template est activée :
   - Sélectionner un template de fiche produit
   - Choisir les sections à inclure
5. Cliquer sur "Générer la description"

### Extraction de spécifications
1. Dans le formulaire de génération, cliquer sur "Extraire les spécifications"
2. Coller le texte brut contenant les spécifications
3. Cliquer sur "Extraire"
4. Vérifier et ajuster les spécifications extraites
5. Cliquer sur "Utiliser ces spécifications"

### Génération par lot
1. Accéder à la page "Génération par lot"
2. Préparer un fichier CSV avec les colonnes suivantes :
   - name (obligatoire)
   - description
   - category
   - keywords (séparés par des virgules)
   - technical_specs (format JSON ou texte brut)
3. Télécharger le fichier CSV
4. Personnaliser les options globales
5. Cliquer sur "Générer les descriptions"
6. Suivre la progression en temps réel
7. Télécharger les résultats une fois terminé

## Format du fichier CSV pour la génération par lot

Voici un exemple de fichier CSV correctement formaté pour la génération par lot :

```csv
name,description,category,keywords,technical_specs
Batterie externe 10000mAh,Batterie portable de haute capacité,Accessoires,batterie portable charge rapide usb-c,{"Capacité":"10000mAh","Ports":"USB-C + USB-A","Poids":"180g"}
Clavier mécanique RGB,Clavier gaming avec switches mécaniques,Périphériques,clavier mécanique gaming rgb,{"Switches":"Blue","Rétroéclairage":"RGB","Disposition":"AZERTY"}
```

## Personnalisation avancée

### Prompts personnalisés
Le système utilise un gestionnaire de prompts qui peut être personnalisé pour adapter les instructions données aux modèles d'IA. Les prompts sont stockés dans le dossier `prompts` du backend.

### Modèles de langage
Par défaut, l'application utilise GPT-4o, mais elle peut être configurée pour utiliser d'autres modèles OpenAI ou même d'autres fournisseurs de LLM compatibles avec LangChain.

### Styles et tons
L'application propose plusieurs styles et tons prédéfinis, mais vous pouvez créer vos propres combinaisons en modifiant les options dans le formulaire.

## Dépannage

### Problèmes courants
- **Erreur 401** : Vérifiez que vos clés API sont correctement configurées dans les fichiers `.env`
- **Erreur lors de l'extraction des spécifications** : Assurez-vous que le format du texte est compatible
- **Génération par lot échoue** : Vérifiez le format de votre fichier CSV
- **Le serveur backend ne démarre pas** : Vérifiez que toutes les dépendances sont installées avec `pip install -r requirements.txt`
- **Le serveur frontend ne démarre pas** : Vérifiez que toutes les dépendances sont installées avec `npm install`

### Logs
Les logs détaillés sont disponibles dans la console du backend et peuvent être configurés pour être plus ou moins verbeux en modifiant le niveau de log dans `main.py`.

Pour activer les logs de débogage, ajoutez cette ligne à votre fichier `.env` du backend :
```
LOG_LEVEL=DEBUG
```

## Configuration des ports et adresses IP

### Ports utilisés

- **Backend (FastAPI)** : Port 8050
  - En local : `http://127.0.0.1:8050` ou `http://localhost:8050`
  - En production : Configuré sur votre VPS avec le même port (8050)

- **Frontend (Next.js)** : Port 3000 (par défaut)
  - En local : `http://localhost:3000`
  - En production : Selon votre configuration

### Fichiers de configuration à vérifier lors de la mise en production

1. **Backend** : Commande de démarrage avec le port 8050
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8050
   ```

2. **Frontend** : Fichier `.env.local`
   ```
   NEXT_PUBLIC_API_URL=http://[ADRESSE_IP_OU_DOMAINE_DU_BACKEND]:8050
   ```

3. **Frontend** : Fichier `next.config.js`
   - Vérifier que les URLs dans les sections `rewrites()` et `env` pointent vers le backend
   - Utiliser l'adresse IP ou le nom de domaine du backend en production

4. **Frontend** : Fichiers proxy dans `src/app/api/`
   - `proxy-generate/route.ts`
   - `proxy-rag/route.ts`
   - `proxy-template/route.ts`
   - Tous ces fichiers doivent utiliser la même URL de backend

5. **Frontend** : Fichier `package.json`
   - Le script `dev` contient l'option `NODE_OPTIONS='--dns-result-order=ipv4first'` pour privilégier IPv4
   - En production, cette option peut être nécessaire si vous rencontrez des problèmes de connexion IPv6

### Notes importantes pour la mise en production

- Si vous utilisez Docker, assurez-vous que les ports sont correctement exposés dans les fichiers `docker-compose.yml`
- Pour éviter les problèmes de connexion IPv6, utilisez toujours des adresses IPv4 explicites (`127.0.0.1` au lieu de `localhost`)
- Si vous utilisez un proxy inverse (Nginx, etc.), configurez-le pour rediriger vers le port 8050 du backend

## Développement futur

### Fonctionnalités planifiées
- Support multilingue
- Intégration avec d'autres plateformes e-commerce
- Amélioration de l'analyse concurrentielle
- Interface d'administration
- Historique des modifications

## Licence
Ce projet est sous licence propriétaire. Tous droits réservés.

---
