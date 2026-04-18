import { startTransition, useState } from "react";
import {
  ArrowUpRight,
  Bot,
  CheckCircle2,
  Layers3,
  LoaderCircle,
  Sparkles,
  Workflow,
  XCircle,
} from "lucide-react";

import { SplineSceneBasic } from "@/components/ui/demo";

type ExecutionStep = {
  tool: string;
  payload: Record<string, unknown>;
};

type ExecutionResult = {
  status: string;
  action?: string;
  system?: string;
  tool?: string;
  message?: string;
  error?: string;
  data?: Record<string, unknown>;
};

type OrchestrateResponse = {
  status: string;
  execution: {
    parsed_intent: {
      task: string;
      target_platform: string;
      data: Record<string, unknown>;
    };
    plan: ExecutionStep[];
    results: ExecutionResult[];
  };
};

type ErrorResponse = {
  detail?: string;
};

const statusCards = [
  {
    title: "Intent Parsing",
    description: "Map natural language into deterministic enterprise actions.",
    icon: Bot,
  },
  {
    title: "Connector Routing",
    description: "Coordinate workflows across CRM, messaging, and internal ops.",
    icon: Workflow,
  },
  {
    title: "Scalable UI Layer",
    description: "A shadcn-style component surface with motion-ready primitives.",
    icon: Layers3,
  },
];

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "https://lyncsync-mvp.vercel.app";

export default function App() {
  const [intent, setIntent] = useState("Onboard a new client named Acme Corp");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<OrchestrateResponse | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setIsSubmitting(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/orchestrate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_intent: intent }),
      });

      const data = (await res.json()) as OrchestrateResponse | ErrorResponse;

      if (!res.ok) {
        const message =
          "detail" in data && typeof data.detail === "string"
            ? data.detail
            : "The orchestration request failed.";
        throw new Error(message);
      }

      startTransition(() => {
        setResponse(data as OrchestrateResponse);
      });
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "Something went wrong while contacting the orchestration API.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-background text-foreground">
      <section className="mx-auto flex min-h-screen max-w-7xl flex-col gap-10 px-6 py-10 lg:px-8">
        <div className="space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-4 py-2 text-sm text-cyan-100">
            LyncSync UI integration
          </div>
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl space-y-3">
              <h1 className="text-4xl font-semibold tracking-tight md:text-6xl">
                Spline scene integrated into a shadcn-style React surface.
              </h1>
              <p className="text-lg text-muted-foreground">
                The frontend now supports TypeScript, Tailwind CSS, path aliases,
                and reusable UI primitives under <code>src/components/ui</code>.
              </p>
            </div>
            <a
              href="https://lyncsync-mvp.vercel.app/docs"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm font-medium text-white transition hover:bg-white/10"
            >
              Open backend docs
              <ArrowUpRight className="h-4 w-4" />
            </a>
          </div>
        </div>

        <SplineSceneBasic />

        <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <section className="rounded-3xl border border-white/10 bg-white/[0.04] p-6">
            <div className="mb-5 flex items-center gap-3">
              <div className="rounded-full border border-cyan-400/20 bg-cyan-400/10 p-2 text-cyan-200">
                <Sparkles className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">Intent to execution</h2>
                <p className="text-sm text-muted-foreground">
                  Submit a natural-language request to the live LyncSync API.
                </p>
              </div>
            </div>

            <form className="space-y-4" onSubmit={handleSubmit}>
              <label className="block space-y-2">
                <span className="text-sm font-medium text-neutral-200">
                  User intent
                </span>
                <textarea
                  value={intent}
                  onChange={(event) => setIntent(event.target.value)}
                  className="min-h-32 w-full rounded-2xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-white outline-none transition placeholder:text-neutral-500 focus:border-cyan-400/40"
                  placeholder="Onboard a new client named Acme Corp"
                />
              </label>

              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="submit"
                  disabled={isSubmitting || !intent.trim()}
                  className="inline-flex items-center gap-2 rounded-full bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isSubmitting ? (
                    <>
                      <LoaderCircle className="h-4 w-4 animate-spin" />
                      Running
                    </>
                  ) : (
                    <>
                      <Workflow className="h-4 w-4" />
                      Execute intent
                    </>
                  )}
                </button>
                <p className="text-xs text-muted-foreground">
                  API target: <code>{API_BASE_URL}</code>
                </p>
              </div>
            </form>
          </section>

          <section className="rounded-3xl border border-white/10 bg-white/[0.04] p-6">
            <h2 className="text-xl font-semibold">Execution telemetry</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Parsed schema, planned tools, and connector results from the API.
            </p>

            {error ? (
              <div className="mt-5 rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-100">
                <div className="flex items-center gap-2 font-medium">
                  <XCircle className="h-4 w-4" />
                  Request failed
                </div>
                <p className="mt-2 text-red-100/90">{error}</p>
              </div>
            ) : null}

            {response ? (
              <div className="mt-5 space-y-4 text-sm">
                <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-cyan-200/80">
                    Parsed intent
                  </div>
                  <div className="mt-3 grid gap-2">
                    <p>
                      <span className="text-muted-foreground">Task:</span>{" "}
                      {response.execution.parsed_intent.task}
                    </p>
                    <p>
                      <span className="text-muted-foreground">Platform:</span>{" "}
                      {response.execution.parsed_intent.target_platform}
                    </p>
                  </div>
                </div>

                <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-cyan-200/80">
                    Execution plan
                  </div>
                  <div className="mt-3 space-y-3">
                    {response.execution.plan.map((step, index) => (
                      <div
                        key={`${step.tool}-${index}`}
                        className="rounded-xl border border-white/10 bg-white/[0.03] p-3"
                      >
                        <p className="font-medium text-white">
                          {index + 1}. {step.tool}
                        </p>
                        <pre className="mt-2 overflow-x-auto text-xs text-neutral-300">
                          {JSON.stringify(step.payload, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-cyan-200/80">
                    Results
                  </div>
                  <div className="mt-3 space-y-3">
                    {response.execution.results.map((result, index) => (
                      <div
                        key={`${result.status}-${index}`}
                        className="rounded-xl border border-white/10 bg-white/[0.03] p-3"
                      >
                        <div className="flex items-center gap-2 font-medium">
                          {result.status === "success" ? (
                            <CheckCircle2 className="h-4 w-4 text-emerald-300" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-300" />
                          )}
                          {result.system || result.tool || result.status}
                        </div>
                        <pre className="mt-2 overflow-x-auto text-xs text-neutral-300">
                          {JSON.stringify(result, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-5 rounded-2xl border border-dashed border-white/10 bg-black/20 p-5 text-sm text-muted-foreground">
                Submit an intent to see the orchestration response rendered here.
              </div>
            )}
          </section>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {statusCards.map(({ title, description, icon: Icon }) => (
            <article
              key={title}
              className="rounded-3xl border border-white/10 bg-white/[0.03] p-6"
            >
              <Icon className="h-6 w-6 text-cyan-300" />
              <h2 className="mt-4 text-xl font-medium">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                {description}
              </p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
