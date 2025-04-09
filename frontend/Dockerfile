FROM node:18-alpine

WORKDIR /app

# Copier les fichiers de dépendances
COPY package.json package-lock.json* ./

# Installer les dépendances
RUN npm ci

# Copier le reste des fichiers du projet
COPY . .

# Construire l'application
RUN npm run build

# Exposer le port 3000 (Next.js utilise ce port par défaut)
EXPOSE 3000

# Démarrer l'application
CMD ["npm", "run", "start"]
