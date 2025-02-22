"use client";

import { AuroraBackgroundDemo } from "@/components/AuroraBackgroundDemo";
import { FeaturesSectionDemo } from "@/components/ui/glowing-effect";
// import { LampDemo } from "@/components/ui/lamp";

export function HomePage() {
  return (
    <div className="dark min-h-screen">
      <AuroraBackgroundDemo />
      <FeaturesSectionDemo />
    </div>
  );
}