import { Link } from "react-router-dom";
import { Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import PageHeader from "../components/PageHeader";
import RiskBadge from "../components/RiskBadge";
import StatCard from "../components/StatCard";
import { conflicts, dailyActivity, riskCounts, summary } from "../data/sampleData";

const pieColors = { High: "#e11d48", Medium: "#d97706", Low: "#059669" };

export default function DashboardPage() {
  const distribution = riskCounts();

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Dashboard"
        title="Sample safety overview"
        text="A single view of the sample day: how many people were counted, where risk is higher, and whether the demo monitor is only standing by."
      >
        <span className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-800">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          {summary.status}
        </span>
      </PageHeader>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Pedestrian count" value={summary.pedestrianCount.toLocaleString()} hint="Sum of people in the eight sample zones." />
        <StatCard label="Detected conflicts" value={summary.conflicts} hint="Potential conflicts in the sample log, not confirmed crashes." />
        <StatCard label="High-risk zones" value={summary.highRiskZones} hint="Zones marked High in the demo map." />
        <StatCard label="Safety score" value={summary.safetyScore} hint="A sample score out of 100 for the presentation." />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.4fr_0.8fr]">
        <article className="rounded-2xl border border-line bg-white p-5 shadow-sm">
          <h2 className="font-display text-xl font-bold text-navy">Daily pedestrian activity</h2>
          <p className="text-sm text-slate-500">Sample counts for one demonstration week.</p>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dailyActivity}>
                <XAxis dataKey="day" tick={{ fill: "#64748b", fontSize: 12 }} />
                <YAxis tick={{ fill: "#64748b", fontSize: 12 }} />
                <Tooltip />
                <Line type="monotone" dataKey="pedestrians" stroke="#1c9ad6" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </article>
        <article className="rounded-2xl border border-line bg-white p-5 shadow-sm">
          <h2 className="font-display text-xl font-bold text-navy">Risk distribution</h2>
          <p className="text-sm text-slate-500">How the eight sample zones are labeled.</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={distribution} dataKey="count" nameKey="level" innerRadius={52} outerRadius={80} paddingAngle={3}>
                  {distribution.map((entry) => (
                    <Cell key={entry.level} fill={pieColors[entry.level]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <ul className="space-y-2">
            {distribution.map((entry) => (
              <li key={entry.level} className="flex items-center justify-between text-sm">
                <RiskBadge level={entry.level} />
                <span className="font-semibold text-navy">{entry.count} zones</span>
              </li>
            ))}
          </ul>
        </article>
      </section>

      <section className="rounded-2xl border border-line bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <h2 className="font-display text-xl font-bold text-navy">Latest sample conflicts</h2>
          <Link to="/conflicts" className="text-sm font-bold text-accent">View all</Link>
        </div>
        <ul className="mt-4 divide-y divide-line">
          {conflicts.slice(0, 4).map((item) => (
            <li key={item.id} className="flex flex-col gap-2 py-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-semibold text-navy">{item.location}</p>
                <p className="text-sm text-slate-500">{item.date} · {item.time} · {item.type}</p>
              </div>
              <RiskBadge level={item.severity} />
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
