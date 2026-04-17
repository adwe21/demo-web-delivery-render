import { useMemo, useState } from "react";
import { api } from "./lib/api";
import {
  ArrowRight,
  Blocks,
  Check,
  ChevronRight,
  Clipboard,
  Mail,
  Rocket,
  Send,
  Sparkles,
  Users,
  Workflow,
} from "lucide-react";

type Audience = "product" | "ops" | "founders";

const SITE_NAME = "Demo Launch Site";

type FormState = {
  name: string;
  email: string;
  company: string;
  useCase: string;
};

const PUBLIC_SITE_URL = "https://demo-web-delivery.zeabur.app/";
const LIVE_SMOKE_DOCS_URL = "https://github.com/adwe21/demo-web-delivery-render#smoke-checks";

const AUDIENCE_COPY: Record<Audience, { label: string; title: string; body: string }> = {
  product: {
    label: "Product teams",
    title: "Align the launch story before roadmap depth catches up",
    body:
      "Package the category narrative, proof stack, and conversion path into one surface that stakeholders can review and prospects can understand fast.",
  },
  ops: {
    label: "Ops & GTM",
    title: "Give every launch handoff one source of truth",
    body:
      "Turn campaign timing, sales context, and launch readiness into one destination your team can circulate without losing the message.",
  },
  founders: {
    label: "Founders",
    title: "Look launch-ready before the full product tour exists",
    body:
      "Lead with the sharpest proof, capture intent, and keep the next step clear while the deeper product roadmap continues shipping.",
  },
};

const FEATURE_BLOCKS = [
  {
    icon: Blocks,
    eyebrow: "Narrative system",
    title: "Clear positioning at first glance",
    body:
      "A sharp hero, concise proof points, and immediate CTA hierarchy make the launch message understandable in seconds.",
  },
  {
    icon: Workflow,
    eyebrow: "Proof modules",
    title: "Composable content blocks for rapid iteration",
    body:
      "Swap proof, feature, and rollout sections without rebuilding the whole page structure. Designed for fast messaging changes.",
  },
  {
    icon: Mail,
    eyebrow: "Live conversion",
    title: "Demand capture with a working interaction loop",
    body:
      "A working CTA form captures launch interest and gives immediate confirmation feedback, suitable for demos and stakeholder review.",
  },
] as const;

const PROOF_POINTS = [
  {
    value: "<60s",
    label: "Message clarity",
    body: "A new viewer can understand the offer, proof, and next step inside the first scroll.",
  },
  {
    value: "Live API intake",
    label: "Conversion path",
    body: "Launch interest is captured through the real backend flow, not a dead-end prototype button.",
  },
  {
    value: "Smoke-guarded deploys",
    label: "Release discipline",
    body: "Homepage, health, submission, and metadata contracts are checked before the public deploy is trusted.",
  },
  {
    value: "Share-ready metadata",
    label: "Distribution surface",
    body: "Large-image cards, alt text, and social previews are aligned before the link gets shared externally.",
  },
] as const;

const STATUS_BADGES = [
  { label: "Smoke status", value: "pass · root / health / intake" },
  { label: "Latest deploy", value: "main → Actions → Zeabur" },
  { label: "Share surface", value: "large card · png · alt text" },
  { label: "Public URL", value: "demo-web-delivery.zeabur.app" },
] as const;

const DELIVERY_STEPS = [
  {
    title: "Narrative direction locked",
    body: "The launch page is framed around a concise hero, modular proof blocks, and one clear conversion action.",
  },
  {
    title: "Production-ready launch surface",
    body: "A single-page React + Vite experience turns positioning, proof, and contact capture into something teams can review live.",
  },
  {
    title: "Proof-backed release gate",
    body: "Build, smoke, metadata, and share-surface checks stay green before the page is treated as ready for traffic.",
  },
] as const;

const INITIAL_FORM: FormState = {
  name: "",
  email: "",
  company: "",
  useCase: "",
};

export default function App() {
  const [audience, setAudience] = useState<Audience>("product");
  const [copyState, setCopyState] = useState<"idle" | "copied">("idle");
  const [form, setForm] = useState<FormState>(INITIAL_FORM);
  const [submitState, setSubmitState] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [submitMessage, setSubmitMessage] = useState("");

  const activeAudience = useMemo(() => AUDIENCE_COPY[audience], [audience]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(PUBLIC_SITE_URL);
    setCopyState("copied");
    window.setTimeout(() => setCopyState("idle"), 1800);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitState("submitting");
    setSubmitMessage("");
    try {
      const response = await api.submitContactIntake({
        name: form.name,
        email: form.email,
        company: form.company,
        use_case: form.useCase,
        source: "launch-page",
      });
      setSubmitState("success");
      setSubmitMessage(response.message);
      setForm(INITIAL_FORM);
    } catch (error) {
      setSubmitState("error");
      setSubmitMessage(error instanceof Error ? error.message : "Submission failed. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="noise-overlay" />
      <div className="warm-glow" />

      <header className="sticky top-0 z-40 border-b border-border bg-background/85 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <a href="#top" className="font-collapse text-xl uppercase tracking-[0.18em] text-foreground">
            {SITE_NAME}
          </a>
          <nav className="hidden items-center gap-6 font-display text-sm uppercase tracking-[0.16em] text-muted-foreground md:flex">
            <a href="#features" className="transition hover:text-foreground">
              Features
            </a>
            <a href="#delivery" className="transition hover:text-foreground">
              Delivery
            </a>
            <a href="#contact" className="transition hover:text-foreground">
              Contact
            </a>
          </nav>
          <a
            href="#contact"
            className="inline-flex items-center gap-2 border border-border bg-foreground px-4 py-2 font-display text-xs uppercase tracking-[0.16em] text-background transition hover:opacity-90"
          >
            Book demo
            <ArrowRight className="h-4 w-4" />
          </a>
        </div>
      </header>

      <main id="top">
        <section className="mx-auto grid max-w-6xl gap-10 px-6 py-18 md:grid-cols-[1.15fr_0.85fr] md:py-24">
          <div className="relative z-10 space-y-8">
            <div className="inline-flex items-center gap-2 border border-border bg-card/70 px-3 py-2 text-xs uppercase tracking-[0.18em] text-muted-foreground">
              <Sparkles className="h-4 w-4 text-warning" />
              trusted launch proof · demo launch site
            </div>

            <div className="space-y-5">
              <p className="font-display text-sm uppercase tracking-[0.2em] text-muted-foreground">
                Launch narrative system · proof blocks · live conversion
              </p>
              <h1 className="max-w-3xl font-collapse text-5xl leading-none tracking-[0.05em] text-foreground sm:text-6xl md:text-7xl">
                Launch a credible product story before the full platform ships.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-foreground/78 sm:text-xl">
                Demo Launch Site turns positioning, proof, and conversion into one production-ready launch surface.
                It is built for stakeholder confidence, early demand capture, and public sharing without placeholder polish.
              </p>
            </div>

            <div className="flex flex-col gap-4 sm:flex-row">
              <a
                href="#contact"
                className="inline-flex items-center justify-center gap-2 border border-foreground bg-foreground px-5 py-3 font-display text-sm uppercase tracking-[0.16em] text-background transition hover:opacity-90"
              >
                Start launch intake
                <ChevronRight className="h-4 w-4" />
              </a>
              <a
                href="#features"
                className="inline-flex items-center justify-center gap-2 border border-border bg-card/70 px-5 py-3 font-display text-sm uppercase tracking-[0.16em] text-foreground transition hover:border-foreground/35"
              >
                Explore sections
                <ArrowRight className="h-4 w-4" />
              </a>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {STATUS_BADGES.map((item) => (
                <div key={item.label} className="border border-border bg-card/65 px-4 py-4 text-sm leading-6 text-foreground/78">
                  <div className="mb-2 flex items-center gap-2 font-display uppercase tracking-[0.16em] text-muted-foreground">
                    <Check className="h-4 w-4 text-success" />
                    {item.label}
                  </div>
                  <div className="font-display text-sm uppercase tracking-[0.12em] text-foreground">{item.value}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative z-10 space-y-5 border border-border bg-card/75 p-5 shadow-[0_0_0_1px_rgba(255,230,203,0.02)]">
            <div className="flex items-center justify-between border-b border-border pb-4">
              <div>
                <p className="font-display text-xs uppercase tracking-[0.18em] text-muted-foreground">Launch proof pack</p>
                <h2 className="mt-2 font-collapse text-2xl uppercase tracking-[0.12em]">Open the proof deck</h2>
              </div>
              <Rocket className="h-6 w-6 text-warning" />
            </div>

            <div className="space-y-4">
              <div className="rounded-[20px] border border-border bg-background/65 p-4">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <p className="font-display text-xs uppercase tracking-[0.16em] text-muted-foreground">All systems ready for launch review</p>
                    <p className="mt-2 font-collapse text-2xl uppercase tracking-[0.08em] text-foreground">Proof pack status</p>
                  </div>
                  <div className="inline-flex items-center gap-2 border border-success/40 bg-success/10 px-3 py-2 font-display text-xs uppercase tracking-[0.16em] text-success">
                    <Check className="h-4 w-4" />
                    launch ready
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  {STATUS_BADGES.map((item) => (
                    <div key={item.label} className="border border-border bg-card/70 px-4 py-4">
                      <p className="font-display text-[11px] uppercase tracking-[0.18em] text-muted-foreground">{item.label}</p>
                      <p className="mt-2 font-display text-sm uppercase tracking-[0.12em] text-foreground">{item.value}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="border border-border bg-background/65 p-4 font-courier text-sm leading-7 text-foreground/88">
                <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  <span className="h-2 w-2 rounded-full bg-destructive" />
                  <span className="h-2 w-2 rounded-full bg-warning" />
                  <span className="h-2 w-2 rounded-full bg-success" />
                  public launch url
                </div>
                <code className="block overflow-x-auto whitespace-pre-wrap bg-transparent p-0">{PUBLIC_SITE_URL}</code>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <button
                  type="button"
                  onClick={() => {
                    void handleCopy();
                  }}
                  className="inline-flex w-full items-center justify-center gap-2 border border-border bg-secondary px-4 py-3 font-display text-sm uppercase tracking-[0.16em] text-foreground transition hover:border-foreground/35"
                >
                  {copyState === "copied" ? <Check className="h-4 w-4 text-success" /> : <Clipboard className="h-4 w-4" />}
                  {copyState === "copied" ? "Copied" : "COPY PUBLIC URL"}
                </button>
                <a
                  href={LIVE_SMOKE_DOCS_URL}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex w-full items-center justify-center gap-2 border border-foreground bg-foreground px-4 py-3 font-display text-sm uppercase tracking-[0.16em] text-background transition hover:opacity-90"
                >
                  RUN LIVE SMOKE
                  <ArrowRight className="h-4 w-4" />
                </a>
              </div>

              <div className="border border-border bg-background/40 p-4">
                <p className="font-display text-xs uppercase tracking-[0.18em] text-muted-foreground">Audience messaging</p>
                <div className="mt-3 grid gap-2 sm:grid-cols-3">
                  {(Object.keys(AUDIENCE_COPY) as Audience[]).map((key) => (
                    <button
                      key={key}
                      type="button"
                      onClick={() => setAudience(key)}
                      className={`border px-3 py-2 text-left font-display text-xs uppercase tracking-[0.16em] transition ${
                        audience === key
                          ? "border-foreground bg-foreground text-background"
                          : "border-border bg-card/70 text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      {AUDIENCE_COPY[key].label}
                    </button>
                  ))}
                </div>
                <div className="mt-4 space-y-2 border-t border-border pt-4">
                  <p className="font-collapse text-2xl uppercase tracking-[0.08em]">{activeAudience.title}</p>
                  <p className="leading-7 text-foreground/78">{activeAudience.body}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="proof" className="mx-auto max-w-6xl px-6 py-6 md:py-12">
          <div className="grid gap-8 border border-border bg-card/60 p-6 md:grid-cols-[0.85fr_1.15fr] md:p-8">
            <div>
              <p className="font-display text-sm uppercase tracking-[0.2em] text-muted-foreground">Trusted launch proof</p>
              <h2 className="mt-3 font-collapse text-4xl uppercase tracking-[0.08em] sm:text-5xl">Evidence, not placeholder polish.</h2>
              <p className="mt-4 max-w-xl leading-7 text-foreground/76">
                Launch signals teams can trust before they publish, share, or spend traffic.
              </p>
              <a
                href="#delivery"
                className="mt-6 inline-flex items-center gap-2 border border-border bg-background/45 px-4 py-3 font-display text-sm uppercase tracking-[0.16em] text-foreground transition hover:border-foreground/35"
              >
                Review the proof
                <ArrowRight className="h-4 w-4" />
              </a>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              {PROOF_POINTS.map((item) => (
                <article key={item.label} className="border border-border bg-background/45 p-5">
                  <p className="font-collapse text-2xl uppercase tracking-[0.08em] text-foreground">{item.value}</p>
                  <p className="mt-2 font-display text-xs uppercase tracking-[0.18em] text-muted-foreground">{item.label}</p>
                  <p className="mt-3 leading-7 text-foreground/76">{item.body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="features" className="mx-auto max-w-6xl px-6 py-6 md:py-12">
          <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="font-display text-sm uppercase tracking-[0.2em] text-muted-foreground">Feature blocks</p>
              <h2 className="mt-3 font-collapse text-4xl uppercase tracking-[0.1em] sm:text-5xl">Core launch sections in one system</h2>
            </div>
            <p className="max-w-xl leading-7 text-foreground/74">
              The page is structured to move from narrative to proof to conversion without asking the visitor to infer what matters.
            </p>
          </div>

          <div className="grid gap-5 md:grid-cols-3">
            {FEATURE_BLOCKS.map(({ icon: Icon, eyebrow, title, body }) => (
              <article key={title} className="group border border-border bg-card/75 p-6 transition hover:border-foreground/35">
                <div className="mb-5 inline-flex items-center gap-3 border border-border bg-background/50 px-3 py-2 text-xs uppercase tracking-[0.18em] text-muted-foreground">
                  <Icon className="h-4 w-4 text-warning" />
                  {eyebrow}
                </div>
                <h3 className="font-collapse text-2xl uppercase tracking-[0.08em] text-foreground">{title}</h3>
                <p className="mt-4 leading-7 text-foreground/76">{body}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="delivery" className="mx-auto max-w-6xl px-6 py-10 md:py-16">
          <div className="grid gap-8 border border-border bg-card/60 p-6 md:grid-cols-[0.8fr_1.2fr] md:p-8">
            <div>
              <p className="font-display text-sm uppercase tracking-[0.2em] text-muted-foreground">Delivery path</p>
              <h2 className="mt-3 font-collapse text-4xl uppercase tracking-[0.08em]">Built to hold up in public</h2>
              <p className="mt-4 leading-7 text-foreground/76">
                The launch surface stays useful because the narrative, proof stack, and release gate are all wired to the same delivery path.
              </p>
            </div>

            <div className="space-y-4">
              {DELIVERY_STEPS.map((step, index) => (
                <div key={step.title} className="flex gap-4 border border-border bg-background/45 p-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center border border-border font-display text-sm uppercase tracking-[0.16em] text-muted-foreground">
                    0{index + 1}
                  </div>
                  <div>
                    <h3 className="font-display text-sm uppercase tracking-[0.16em] text-foreground">{step.title}</h3>
                    <p className="mt-2 leading-7 text-foreground/74">{step.body}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="contact" className="mx-auto max-w-6xl px-6 py-8 pb-20 md:py-14 md:pb-24">
          <div className="grid gap-8 md:grid-cols-[0.85fr_1.15fr]">
            <div className="space-y-5">
              <p className="font-display text-sm uppercase tracking-[0.2em] text-muted-foreground">Launch intake</p>
              <h2 className="font-collapse text-4xl uppercase tracking-[0.08em] sm:text-5xl">Capture serious launch interest with a live handoff</h2>
              <p className="leading-7 text-foreground/76">
                Submit the form to show the launch surface can move from attention to qualified intent without breaking the story.
              </p>
              <div className="border border-border bg-card/70 p-5 text-sm leading-7 text-foreground/76">
                <div className="mb-3 flex items-center gap-2 font-display uppercase tracking-[0.16em] text-muted-foreground">
                  <Users className="h-4 w-4" />
                  What this proves
                </div>
                <ul className="space-y-2">
                  <li>• Collect contact and use-case context in one reviewable launch flow.</li>
                  <li>• Route launch interest through the backend API and return immediate confirmation.</li>
                  <li>• Keep the conversion surface aligned with smoke, deploy, and sharing checks.</li>
                </ul>
              </div>
            </div>

            <div className="border border-border bg-card/75 p-6">
              <form className="space-y-4" onSubmit={handleSubmit}>
                <div className="grid gap-4 sm:grid-cols-2">
                  <label className="space-y-2 text-sm text-foreground/82">
                    <span className="font-display uppercase tracking-[0.16em] text-muted-foreground">Name</span>
                    <input
                      required
                      value={form.name}
                      onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                      className="w-full border border-border bg-background/55 px-4 py-3 text-base text-foreground outline-none transition focus:border-foreground/40"
                      placeholder="Alex Chen"
                    />
                  </label>
                  <label className="space-y-2 text-sm text-foreground/82">
                    <span className="font-display uppercase tracking-[0.16em] text-muted-foreground">Work email</span>
                    <input
                      required
                      type="email"
                      value={form.email}
                      onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                      className="w-full border border-border bg-background/55 px-4 py-3 text-base text-foreground outline-none transition focus:border-foreground/40"
                      placeholder="alex@company.com"
                    />
                  </label>
                </div>

                <label className="block space-y-2 text-sm text-foreground/82">
                  <span className="font-display uppercase tracking-[0.16em] text-muted-foreground">Company</span>
                  <input
                    required
                    value={form.company}
                    onChange={(event) => setForm((current) => ({ ...current, company: event.target.value }))}
                    className="w-full border border-border bg-background/55 px-4 py-3 text-base text-foreground outline-none transition focus:border-foreground/40"
                    placeholder="Northstar Labs"
                  />
                </label>

                <label className="block space-y-2 text-sm text-foreground/82">
                  <span className="font-display uppercase tracking-[0.16em] text-muted-foreground">Launch use case</span>
                  <textarea
                    required
                    rows={5}
                    value={form.useCase}
                    onChange={(event) => setForm((current) => ({ ...current, useCase: event.target.value }))}
                    className="w-full resize-y border border-border bg-background/55 px-4 py-3 text-base text-foreground outline-none transition focus:border-foreground/40"
                    placeholder="We need a launch page for partner demos, waitlist capture, and investor meetings next month."
                  />
                </label>

                <button
                  type="submit"
                  disabled={submitState === "submitting"}
                  className="inline-flex w-full items-center justify-center gap-2 border border-foreground bg-foreground px-4 py-3 font-display text-sm uppercase tracking-[0.16em] text-background transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-70"
                >
                  <Send className="h-4 w-4" />
                  {submitState === "submitting" ? "Submitting…" : "Submit launch intake"}
                </button>
              </form>

              {submitState === "success" && (
                <div className="mt-4 border border-success/50 bg-success/10 p-4 text-sm leading-7 text-foreground">
                  <div className="flex items-center gap-2 font-display uppercase tracking-[0.16em] text-success">
                    <Check className="h-4 w-4" />
                    Submission received
                  </div>
                  <p className="mt-2 text-foreground/82">
                    {submitMessage || "Launch intake captured and handed to the backend workflow."}
                  </p>
                </div>
              )}

              {submitState === "error" && (
                <div className="mt-4 border border-warning/50 bg-warning/10 p-4 text-sm leading-7 text-foreground">
                  <div className="font-display uppercase tracking-[0.16em] text-warning">Submission failed</div>
                  <p className="mt-2 text-foreground/82">{submitMessage}</p>
                </div>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
