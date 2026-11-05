import { Link } from "react-router-dom";
import PageHeader from "../components/PageHeader";
import { project, team, technologies, workflow } from "../data/sampleData";

export default function AboutPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="About the project"
        title={project.name}
        text="PedSafe is the frontend for a student hackathon system that will later connect video analysis, conflict detection, and a risk score. The pages you can click today are a complete demonstration with sample data."
      />

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="rounded-2xl border border-line bg-white p-6 shadow-sm">
          <h2 className="font-display text-2xl font-bold text-navy">Problem</h2>
          <p className="mt-3 leading-7 text-slate-600">
            Urban crossings mix people and vehicles at schools, markets, hospitals, and transit stops. Teams need a clear way to see where pedestrian risk looks higher and where a possible conflict was flagged. A raw video is hard to compare across places.
          </p>
        </article>
        <article className="rounded-2xl border border-line bg-white p-6 shadow-sm">
          <h2 className="font-display text-2xl font-bold text-navy">Proposed solution</h2>
          <p className="mt-3 leading-7 text-slate-600">
            Accept a road video, detect and track pedestrians and vehicles, look for movements that could conflict, and show a Low, Medium, or High result with the reasons. This website is the screen for that result. It does not claim it can predict an accident with certainty.
          </p>
        </article>
      </section>

      <section className="rounded-2xl bg-navy p-6 text-white">
        <h2 className="font-display text-2xl font-bold">System workflow</h2>
        <ol className="mt-5 grid gap-4 md:grid-cols-5">
          {workflow.map((item) => (
            <li key={item.step}>
              <p className="text-sm font-bold text-sky-300">{item.step}</p>
              <h3 className="mt-1 font-display text-lg font-bold">{item.title}</h3>
              <p className="mt-2 text-sm leading-6 text-sky-100">{item.text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        {technologies.map((group) => (
          <article key={group.group} className="rounded-2xl border border-line bg-white p-6 shadow-sm">
            <h2 className="font-display text-2xl font-bold text-navy">{group.group}</h2>
            <ul className="mt-4 flex flex-wrap gap-2">
              {group.items.map((item) => (
                <li key={item} className="rounded-full bg-ice px-3 py-1.5 text-sm font-semibold text-navy">{item}</li>
              ))}
            </ul>
          </article>
        ))}
      </section>

      <section>
        <h2 className="font-display text-2xl font-bold text-navy">Project team</h2>
        <p className="mt-2 text-slate-600">Roles follow the shared project split. Add personal names before the presentation if the team wants them on screen.</p>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {team.map((member) => (
            <article key={member.role} className="rounded-2xl border border-line bg-white p-5 shadow-sm">
              <p className="text-sm font-bold uppercase tracking-wide text-accent">{member.role}</p>
              <h3 className="mt-2 font-display text-lg font-bold text-navy">{member.focus}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{member.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-sky-200 bg-sky-50 p-6">
        <h2 className="font-display text-xl font-bold text-navy">Data honesty</h2>
        <p className="mt-2 leading-7 text-slate-700">{project.note} When Member 2 shares API routes, the dashboard can read those JSON fields without renaming them.</p>
        <Link to="/dashboard" className="mt-4 inline-block text-sm font-bold text-accent">Return to the dashboard</Link>
      </section>
    </div>
  );
}
