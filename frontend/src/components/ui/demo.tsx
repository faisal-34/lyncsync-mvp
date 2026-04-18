"use client";

import { Orbit, Sparkles } from "lucide-react";

import { Card } from "@/components/ui/card";
import { Spotlight } from "@/components/ui/spotlight";
import { SplineScene } from "@/components/ui/splite";

export function SplineSceneBasic() {
  return (
    <Card className="relative h-[560px] w-full overflow-hidden border-white/10 bg-black/[0.96]">
      <Spotlight className="-top-40 left-0 md:left-60 md:-top-20" fill="white" />

      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.12),transparent_35%),radial-gradient(circle_at_bottom_right,rgba(251,146,60,0.16),transparent_38%)]" />

      <div className="relative z-10 flex h-full flex-col lg:flex-row">
        <div className="flex flex-1 flex-col justify-center p-8 lg:p-12">
          <div className="mb-5 inline-flex w-fit items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-100">
            <Sparkles className="h-4 w-4" />
            Immersive orchestration
          </div>

          <h1 className="max-w-xl bg-gradient-to-b from-neutral-50 to-neutral-400 bg-clip-text text-4xl font-bold text-transparent md:text-5xl">
            Interactive 3D control surfaces for AI operations.
          </h1>

          <p className="mt-4 max-w-lg text-neutral-300">
            Bring your UI to life with beautiful 3D scenes. Create immersive
            experiences that capture attention and make orchestration workflows
            feel alive.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-neutral-200">
              <span className="font-medium text-white">Scene:</span> Spline
            </div>
            <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-neutral-200">
              <span className="font-medium text-white">Motion:</span> Framer
            </div>
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-neutral-200">
              <Orbit className="h-4 w-4 text-cyan-300" />
              Live interaction
            </div>
          </div>
        </div>

        <div className="relative flex-1">
          <div className="absolute inset-0 bg-gradient-to-r from-black/40 via-transparent to-transparent lg:hidden" />
          <SplineScene
            scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
            className="h-full w-full"
          />
        </div>
      </div>
    </Card>
  );
}
