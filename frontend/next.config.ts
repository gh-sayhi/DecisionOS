import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8001";
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`
      },
      {
        source: "/reports/:path*",
        destination: `${backendUrl}/reports/:path*`
      }
    ];
  }
};

export default nextConfig;
