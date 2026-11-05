import { Link } from "react-router-dom";
import DemoBanner from "../components/DemoBanner";
import Navbar from "../components/Navbar";
import { benefits, features, project, summary, workflow } from "../data/sampleData";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      <DemoBanner />
      <Navbar />
      <section className="relative overflow-hidden bg-navy text-white">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(56,189,248,0.35),transparent_36%),radial-gradient(circle_at_90%_0%,rgba(28,154,214,0.25),transparent_32%)]" />
        <div className="relative mx-auto grid max-w-6xl gap-10 px-4 py-16 lg:grid-cols-[1.1fr_0.9fr] lg:py-24">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-sky-300">Hackathon demonstration</p>
            <h1 className="mt-4 font-display text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl">
              {project.name}
            </h1>
            <p className="mt-5 max-w-xl text-lg leading-8 text-sky-100">
              A monitoring website for urban pedestrian safety. It is designed to highlight crossings that need attention and to show potential pedestrian–vehicle conflicts. This build uses sample data so the team can demonstrate the interface before the models are connected.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/dashboard" className="rounded-full bg-white px-5 py-3 text-sm font-bold text-navy">
                Open the dashboard
              </Link>
              <Link to="/about" className="rounded-full border border-white/30 px-5 py-3 text-sm font-bold text-white">
                Read the approach
              </Link>
            </div>
          </div>
          <div className="rounded-3xl border border-white/15 bg-white/10 p-5 shadow-2xl backdrop-blur">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-sky-100">Sample snapshot</p>
              <span className="rounded-full bg-emerald-400/20 px-3 py-1 text-xs font-bold text-emerald-200">Standby</span>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3">
              {[
                [summary.pedestrianCount.toLocaleString(), "Pedestrians"],
                [String(summary.conflicts), "Potential conflicts"],
                [String(summary.highRiskZones), "High-risk zones"],
                [String(summary.safetyScore), "Sample safety score"],
              ].map(([value, label]) => (
                <div key={label} className="rounded-2xl bg-navy/70 p-4">
                  <p className="font-display text-3xl font-bold">{value}</p>
                  <p className="text-sm text-sky-200">{label}</p>
                </div>
              ))}
            </div>
            <p className="mt-4 text-sm leading-6 text-sky-100">{project.note}</p>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-accent">Problem</p>
        <h2 className="mt-2 font-display text-3xl font-bold text-navy">Busy streets hide the crossings that need attention</h2>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {[
            ["Mixed movement", "People and vehicles share space at schools, markets, hospitals, and transit stops."],
            ["Hard to compare", "A video clip alone does not show which place is riskier across a day."],
            ["Careful claims", "A useful tool should flag potential conflict. It should not pretend it can foresee an accident."],
          ].map(([title, text]) => (
            <article key={title} className="rounded-2xl border border-line bg-paper p-5">
              <h3 className="font-display text-xl font-bold text-navy">{title}</h3>
              <p className="mt-2 leading-7 text-slate-600">{text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="bg-paper">
        <div className="mx-auto max-w-6xl px-4 py-16">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-accent">Features</p>
          <h2 className="mt-2 font-display text-3xl font-bold text-navy">What the demonstration shows</h2>
          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {features.map((feature) => (
              <article key={feature.title} className="rounded-2xl border border-line bg-white p-5 shadow-sm">
                <div className="mb-4 h-1.5 w-12 rounded-full bg-accent" />
                <h3 className="font-display text-xl font-bold text-navy">{feature.title}</h3>
                <p className="mt-2 leading-7 text-slate-600">{feature.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-accent">How it works</p>
        <h2 className="mt-2 font-display text-3xl font-bold text-navy">From a street observation to a clear screen</h2>
        <ol className="mt-8 grid gap-4 md:grid-cols-5">
          {workflow.map((item) => (
            <li key={item.step} className="rounded-2xl bg-navy p-4 text-white">
              <p className="text-sm font-bold text-sky-300">{item.step}</p>
              <h3 className="mt-2 font-display text-lg font-bold">{item.title}</h3>
              <p className="mt-2 text-sm leading-6 text-sky-100">{item.text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="bg-ice">
        <div className="mx-auto grid max-w-6xl gap-8 px-4 py-16 lg:grid-cols-[0.8fr_1.2fr]">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-accent">Benefits</p>
            <h2 className="mt-2 font-display text-3xl font-bold text-navy">Why a city team would use it</h2>
          </div>
          <ul className="space-y-3">
            {benefits.map((benefit) => (
              <li key={benefit} className="rounded-2xl bg-white px-5 py-4 leading-7 text-slate-700 shadow-sm">
                {benefit}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="bg-navy">
        <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-6 px-4 py-14 sm:flex-row sm:items-center">
          <div>
            <h2 className="font-display text-3xl font-bold text-white">Walk through the sample city</h2>
            <p className="mt-2 max-w-xl text-sky-100">Start with the dashboard, then open the map, the conflict log, and the charts.</p>
          </div>
          <Link to="/dashboard" className="rounded-full bg-accent px-5 py-3 text-sm font-bold text-white">
            Get Started
          </Link>
        </div>
      </section>
    </div>
  );
}
