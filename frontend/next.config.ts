import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produces .next/standalone/ with a minimal node_modules tree.
  // Lets the Dockerfile runner stage be tiny (only runtime deps).
  output: "standalone",
};

export default nextConfig;
