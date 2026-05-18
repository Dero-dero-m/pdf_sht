import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@scaffold/shared-types"],
};

export default nextConfig;
