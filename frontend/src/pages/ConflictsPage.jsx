import { useMemo, useState } from "react";
import PageHeader from "../components/PageHeader";
import RiskBadge from "../components/RiskBadge";
import { conflicts } from "../data/sampleData";

const filters = ["All", "High", "Medium", "Low"];

export default function ConflictsPage() {
  const [severity, setSeverity] = useState("All");
  const [query, setQuery] = useState("");

  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return conflicts.filter((item) => {
      const matchesSeverity = severity === "All" || item.severity === severity;
      const matchesQuery = !needle || `${item.location} ${item.type} ${item.id}`.toLowerCase().includes(needle);
      return matchesSeverity && matchesQuery;
    });
  }, [query, severity]);

  const counts = filters.slice(1).map((level) => ({
    level,
    count: conflicts.filter((item) => item.severity === level).length,
  }));

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Conflict detection"
        title="Potential pedestrian–vehicle conflicts"
        text="Each row is a sample event for the demo. Severity describes the sample label, not a confirmed injury or crash."
      />

      <section className="grid gap-4 sm:grid-cols-3">
        {counts.map((item) => (
          <article key={item.level} className="rounded-2xl border border-line bg-white p-5 shadow-sm">
            <RiskBadge level={item.level} />
            <p className="mt-3 font-display text-3xl font-bold text-navy">{item.count}</p>
            <p className="text-sm text-slate-500">Sample events at this severity</p>
          </article>
        ))}
      </section>

      <section className="rounded-2xl border border-line bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search location, type, or ID"
            className="w-full rounded-xl border border-line px-4 py-3 text-sm outline-none ring-accent focus:ring-2 lg:max-w-sm"
          />
          <div className="flex flex-wrap gap-2">
            {filters.map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setSeverity(item)}
                className={`rounded-full px-4 py-2 text-sm font-bold ${severity === item ? "bg-navy text-white" : "bg-paper text-navy"}`}
              >
                {item}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-5 overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-line text-slate-500">
              <tr>
                <th className="px-3 py-3 font-semibold">ID</th>
                <th className="px-3 py-3 font-semibold">Date</th>
                <th className="px-3 py-3 font-semibold">Time</th>
                <th className="px-3 py-3 font-semibold">Location</th>
                <th className="px-3 py-3 font-semibold">Type</th>
                <th className="px-3 py-3 font-semibold">Severity</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((item) => (
                <tr key={item.id} className="border-b border-line/80">
                  <td className="px-3 py-3 font-semibold text-navy">{item.id}</td>
                  <td className="px-3 py-3">{item.date}</td>
                  <td className="px-3 py-3">{item.time}</td>
                  <td className="px-3 py-3">
                    <span className="block font-medium text-navy">{item.location}</span>
                    <span className="text-slate-500">{item.area}</span>
                  </td>
                  <td className="px-3 py-3">{item.type}</td>
                  <td className="px-3 py-3"><RiskBadge level={item.severity} /></td>
                </tr>
              ))}
            </tbody>
          </table>
          {visible.length === 0 ? <p className="py-8 text-center text-slate-500">No sample conflicts match that filter.</p> : null}
        </div>
      </section>

      <section>
        <h2 className="font-display text-2xl font-bold text-navy">Conflict history</h2>
        <div className="mt-4 grid gap-3">
          {visible.slice(0, 5).map((item) => (
            <article key={item.id} className="rounded-2xl border border-line bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="font-semibold text-navy">{item.location} · {item.time}</p>
                <RiskBadge level={item.severity} />
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.summary}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
