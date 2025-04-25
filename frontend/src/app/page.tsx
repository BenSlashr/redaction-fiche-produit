import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <header className="mb-16 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900 dark:text-white">
            Générateur de Fiches Produit IA
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Créez des fiches produit optimisées et professionnelles en quelques clics grâce à l'intelligence artificielle
          </p>
          <div className="flex justify-center mt-4 space-x-4">
            <Link 
              href="/generate"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
            >
              Générer une fiche produit
            </Link>
            <Link 
              href="/prompts"
              className="inline-block bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition duration-200"
            >
              Gérer les prompts
            </Link>
          </div>
        </header>

        <main className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md">
                <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
                  Fonctionnalités principales
                </h2>
                <ul className="space-y-3">
                  <li className="flex items-start">
                    <span className="text-emerald-500 mr-2">✓</span>
                    <span className="text-gray-700 dark:text-gray-300">Génération de descriptions produit optimisées pour le SEO</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-emerald-500 mr-2">✓</span>
                    <span className="text-gray-700 dark:text-gray-300">Personnalisation du ton éditorial selon votre marque</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-emerald-500 mr-2">✓</span>
                    <span className="text-gray-700 dark:text-gray-300">Analyse des concurrents pour un contenu compétitif</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-emerald-500 mr-2">✓</span>
                    <span className="text-gray-700 dark:text-gray-300">Intégration des données techniques dans un format attrayant</span>
                  </li>
                </ul>
              </div>
              
              <Link 
                href="/generate"
                className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition duration-200 text-center w-full"
              >
                Commencer à générer
              </Link>
            </div>
            
            <div className="relative h-[400px] rounded-xl overflow-hidden shadow-lg">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-purple-500/20 z-10"></div>
              <div className="absolute inset-0 flex items-center justify-center z-20">
                <div className="bg-white/90 dark:bg-gray-800/90 p-6 rounded-xl max-w-md">
                  <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">
                    Exemple de fiche produit
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 text-sm">
                    "Le Smartphone XYZ Pro offre une expérience utilisateur exceptionnelle grâce à son écran AMOLED 
                    de 6,5 pouces et son processeur octa-core ultrarapide. Sa batterie longue durée de 5000mAh 
                    vous accompagne toute la journée, tandis que son appareil photo 108MP capture chaque détail 
                    avec une précision remarquable..."
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-20 bg-gray-100 dark:bg-gray-800/50 p-8 rounded-xl">
            <h2 className="text-2xl font-semibold mb-6 text-center text-gray-800 dark:text-white">
              Comment ça fonctionne
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="bg-blue-100 dark:bg-blue-900/30 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">1</span>
                </div>
                <h3 className="font-medium mb-2 text-gray-800 dark:text-white">Entrez vos données</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Renseignez les informations techniques et commerciales de votre produit
                </p>
              </div>
              <div className="text-center">
                <div className="bg-blue-100 dark:bg-blue-900/30 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">2</span>
                </div>
                <h3 className="font-medium mb-2 text-gray-800 dark:text-white">Personnalisez</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Choisissez le ton éditorial et les options d'optimisation SEO
                </p>
              </div>
              <div className="text-center">
                <div className="bg-blue-100 dark:bg-blue-900/30 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">3</span>
                </div>
                <h3 className="font-medium mb-2 text-gray-800 dark:text-white">Générez</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Notre IA crée une fiche produit optimisée et prête à l'emploi
                </p>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            <Link href="/generate" className="group">
              <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6 hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
                <h2 className="text-2xl font-semibold mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                  Générer une description
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Créez une description de produit optimisée pour le SEO et adaptée à votre marque.
                </p>
              </div>
            </Link>
            
            <Link href="/batch" className="group">
              <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6 hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
                <h2 className="text-2xl font-semibold mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                  Génération par lot
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Importez un fichier CSV pour générer plusieurs descriptions de produits en une seule fois.
                </p>
              </div>
            </Link>
            
            <Link href="/prompts" className="group">
              <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6 hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
                <h2 className="text-2xl font-semibold mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                  Gérer les prompts
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Personnalisez les prompts utilisés pour la génération de contenu.
                </p>
              </div>
            </Link>
            
            <Link href="/templates" className="group">
              <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-6 hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
                <h2 className="text-2xl font-semibold mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                  Templates de fiches produit
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Personnalisez les templates et les requêtes RAG pour chaque section de vos fiches produit.
                </p>
              </div>
            </Link>
          </div>
        </main>
      </div>
    </div>
  );
}
