/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  basePath: '/rfp',
  assetPrefix: '/rfp',
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://rfp-backend:8050';
    
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/:path*`,
      },
      {
        source: '/:path(client-data|client-file|upload-client-file|generate-with-rag)/:rest*',
        destination: `${apiUrl}/:path/:rest*`,
      },
    ];
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://rfp-backend:8050',
  },
  trailingSlash: true, // ← AJOUT IMPORTANT
};

module.exports = nextConfig;
