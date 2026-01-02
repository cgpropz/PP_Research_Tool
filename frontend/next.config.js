/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['cdn.nba.com'],
  },
  async rewrites() {
    // Use environment variable, or Railway production URL if in production
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://ppresearchtool-production.up.railway.app';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
