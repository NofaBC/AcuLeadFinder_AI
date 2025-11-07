/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Ignore critical dependency warnings from Firebase
    config.ignoreWarnings = [
      { module: /node_modules\/@firebase\/auth/ },
      { module: /node_modules\/@firebase\/firestore/ },
      { module: /node_modules\/@firebase\/storage/ },
      { module: /node_modules\/undici/ },
    ];

    // Handle undici module
    config.module = {
      ...config.module,
      exprContextCritical: false,
    };

    return config;
  },
}

module.exports = nextConfig
