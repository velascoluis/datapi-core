/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    distDir: "build",
    images: {
        unoptimized: true,
    },
};

module.exports = nextConfig

