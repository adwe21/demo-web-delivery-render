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

const INSTALL_COMMAND =
  "curl -fsSL https://example.com/demo-launch-site/install.sh | bash";

const AUDIENCE_COPY: Record<Audience, { label: string; title: string; body: string }> = {
  product: {
    label: "Product teams",
    title: "Ship the story before the full product is ready",
    body:
      "Present the narrative, value props, and CTA flow in a polished single page that can be validated with real traffic.",
  },
  ops: {
    label: "Ops & GTM",
    title: "Coordinate launch messaging from one surface",
    body:
      "Turn timelines, handoff notes, and launch milestones into one page your teams can review, share, and iterate on quickly.",
  },
  founders: {
    label: "Founders",
    title: "Move from concept to launch-ready presence in days",
    body:
      "Start with the core message, capture demand, and create a clear next action while engineering continues on the full product.",
  },
};

const FEATURE_BLOCKS = [
  {
    icon: Blocks,
    eyebrow: "HeroSection",
    title: "Clear positioning at first glance",
    body:
      "A sharp hero, concise proof points, and immediate CTA hierarchy make the launch message understandable in seconds.",
  },
  {
    icon: Workflow,
    eyebrow: "FeatureGrid",
    title: "Composable content blocks for rapid iteration",
    body:
      "Swap proof, feature, and rollout sections without rebuilding the whole page structure. Designed for fast messaging changes.",
  },
  {
    icon: Mail,
    eyebrow: "ContactForm",
    title: "Demand capture with a live interaction loop",
    body:
      "A working CTA form captures launch interest and gives immediate confirmation feedback, suitable for demos and stakeholder review.",
  },
] as const;

const DELIVERY_STEPS = [
  {
    title: "Design handoff aligned",
    body: "Direction: 清晰、结构化、低噪音。页面结构聚焦 Hero、Feature blocks、CTA form。",
  },
  {
    title: "Frontend implementation",
    body: "Single-page React + Vite delivery with reusable blocks, responsive layout, copy interaction, and CTA form state.",
  },
  {
    title: "Launch-ready validation",
    body: "Production build passes locally so the page can move into downstream QA / deploy phases with low friction.",
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
    await navigator.clipboard.writeText(INSTALL_COMMAND);
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
              frontend delivery · demo-web-delivery
            </div>

            <div className="space-y-5">
              <p className="font-display text-sm uppercase tracking-[0.2em] text-muted-foreground">
                Hero · Feature blocks · CTA form
              </p>
              <h1 className="max-w-3xl font-collapse text-5xl leading-none tracking-[0.05em] text-foreground sm:text-6xl md:text-7xl">
                Launch a credible product story before the full platform ships.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-foreground/78 sm:text-xl">
                This demo site packages positioning, proof, and conversion into one focused frontend surface.
                It is built for stakeholder review, early demand capture, and downstream launch validation.
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

            <div className="grid gap-4 sm:grid-cols-3">
              {[
                "Responsive one-page structure",
                "Interactive audience messaging switcher",
                "Working CTA confirmation flow",
              ].map((item) => (
                <div key={item} className="border border-border bg-card/65 px-4 py-4 text-sm leading-6 text-foreground/78">
                  <div className="mb-2 flex items-center gap-2 font-display uppercase tracking-[0.16em] text-muted-foreground">
                    <Check className="h-4 w-4 text-success" />
                    Ready
                  </div>
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div className="relative z-10 space-y-5 border border-border bg-card/75 p-5 shadow-[0_0_0_1px_rgba(255,230,203,0.02)]">
            <div className="flex items-center justify-between border-b border-border pb-4">
              <div>
                <p className="font-display text-xs uppercase tracking-[0.18em] text-muted-foreground">Quick launch starter</p>
                <h2 className="mt-2 font-collapse text-2xl uppercase tracking-[0.12em]">Install / handoff prompt</h2>
              </div>
              <Rocket className="h-6 w-6 text-warning" />
            </div>

            <div className="space-y-4">
              <div className="border border-border bg-background/65 p-4 font-courier text-sm leading-7 text-foreground/88">
                <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">
                  <span className="h-2 w-2 rounded-full bg-destructive" />
                  <span className="h-2 w-2 rounded-full bg-warning" />
                  <span className="h-2 w-2 rounded-full bg-success" />
                  terminal snippet
                </div>
                <code className="block overflow-x-auto whitespace-pre-wrap bg-transparent p-0">{INSTALL_COMMAND}</code>
              </div>

              <button
                type="button"
                onClick={() => {
                  void handleCopy();
                }}
                className="inline-flex w-full items-center justify-center gap-2 border border-border bg-secondary px-4 py-3 font-display text-sm uppercase tracking-[0.16em] text-foreground transition hover:border-foreground/35"
              >
                {copyState === "copied" ? <Check className="h-4 w-4 text-success" /> : <Clipboard className="h-4 w-4" />}
                {copyState === "copied" ? "Copied" : "Copy command"}
              </button>

              <div className="border border-border bg-background/40 p-4">
                <p className="font-display text-xs uppercase tracking-[0.18em] text-muted-foreground">Audience lens</p>
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

        <section id="features" className="mx-auto max-w-6xl px-6 py-6 md:py-12">
          <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="font-display text-sm uppercase tracking-[0.2em] text-muted-foreground">Feature blocks</p>
              <h2 className="mt-3 font-collapse text-4xl uppercase tracking-[0.1em] sm:text-5xl">Core frontend sections delivered</h2>
            </div>
            <p className="max-w-xl leading-7 text-foreground/74">
              The implementation follows the approved design direction: clear structure, low noise, and a focused path from value proposition to CTA.
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
              <h2 className="mt-3 font-collapse text-4xl uppercase tracking-[0.08em]">Built to clear frontend acceptance</h2>
              <p className="mt-4 leading-7 text-foreground/76">
                The page turns the design handoff into a runnable React implementation and keeps the scope tight around the current delivery lane.
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
              <p className="font-display text-sm uppercase tracking-[0.2em] text-muted-foreground">CTA form</p>
              <h2 className="font-collapse text-4xl uppercase tracking-[0.08em] sm:text-5xl">Capture launch interest with a working interaction</h2>
              <p className="leading-7 text-foreground/76">
                Submit the form to simulate a launch intake flow. The interaction confirms the handoff works and demonstrates the CTA state transition for review.
              </p>
              <div className="border border-border bg-card/70 p-5 text-sm leading-7 text-foreground/76">
                <div className="mb-3 flex items-center gap-2 font-display uppercase tracking-[0.16em] text-muted-foreground">
                  <Users className="h-4 w-4" />
                  Demo-ready outcomes
                </div>
                <ul className="space-y-2">
                  <li>• Collect contact and use-case context in one place.</li>
                  <li>• Submit the launch intake to the backend API and return immediate confirmation.</li>
                  <li>• Keep the CTA flow aligned with downstream QA and deploy validation.</li>
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
