import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import PageHeader from "../components/PageHeader";
import { conflicts, dailyActivity, hourlyMovement, weeklyActivity, zones } from "../data/sampleData";
import { downloadCsv } from "../utils/downloadReport";

export default function AnalyticsPage() {
  const [period, setPeriod] = useState("daily");
  const trend = period === "daily" ? dailyActivity : weeklyActivity;
  const zoneComparison = zones.map((zone) => ({
    name: zone.name.split(" ")[0],
    fullName: zone.name,
    risk: zone.riskPercent,
    traffic: zone.factors.trafficDensity,
  }));

  function downloadReport() {
    downloadCsv("pedsafe-demo-zone-report.csv", zones.map((zone) => ({
      source: "DEMO DATA",
      zone: zone.name,
      area: zone.area,
      level: zone.level,
      riskPercent: zone.riskPercent,
      pedestrians: zone.pedestrians,
      vehicles: zone.vehicles,
      trafficDensity: zone.factors.trafficDensity,
      pedestrianDensity: zone.factors.pedestrianDensity,
      roadConditions: zone.factors.roadConditions,
      lighting: zone.factors.lighting,
    })));
  }

  function downloadConflicts() {
    downloadCsv("pedsafe-demo-conflicts.csv", conflicts.map((item) => ({
      source: "DEMO DATA",
      ...item,
    })));
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Analytics and reports"
        title="Sample trends for the demonstration"
        text="Switch between a sample week and four sample weeks. Downloads are CSV files of this same demonstration data. Use Print / Save PDF if you want a paper copy of the page."
      >
        <button type="button" onClick={() => setPeriod("daily")} className={`rounded-full px-4 py-2 text-sm font-bold ${period === "daily" ? "bg-navy text-white" : "bg-white text-navy ring-1 ring-line"}`}>Daily</button>
        <button type="button" onClick={() => setPeriod("weekly")} className={`rounded-full px-4 py-2 text-sm font-bold ${period === "weekly" ? "bg-navy text-white" : "bg-white text-navy ring-1 ring-line"}`}>Weekly</button>
        <button type="button" onClick={downloadReport} className="rounded-full bg-accent px-4 py-2 text-sm font-bold text-white">Download CSV</button>
        <button type="button" onClick={downloadConflicts} className="rounded-full bg-white px-4 py-2 text-sm font-bold text-navy ring-1 ring-line">Conflict CSV</button>
        <button type="button" onClick={() => window.print()} className="no-print rounded-full bg-white px-4 py-2 text-sm font-bold text-navy ring-1 ring-line">Print / Save PDF</button>
      </PageHeader>

      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-2xl bg-navy p-5 text-white">
          <p className="text-sm text-sky-200">Peak sample hour</p>
          <p className="mt-2 font-display text-3xl font-bold">18:00</p>
          <p className="mt-1 text-sm text-sky-100">Highest pedestrian bar in the sample day.</p>
        </article>
        <article className="rounded-2xl border border-line bg-white p-5">
          <p className="text-sm text-slate-500">Busiest sample zone</p>
          <p className="mt-2 font-display text-2xl font-bold text-navy">Central Market</p>
          <p className="mt-1 text-sm text-slate-500">312 sample pedestrians.</p>
        </article>
        <article className="rounded-2xl border border-line bg-white p-5">
          <p className="text-sm text-slate-500">Zones above 70% risk</p>
          <p className="mt-2 font-display text-3xl font-bold text-navy">{zones.filter((zone) => zone.riskPercent >= 70).length}</p>
          <p className="mt-1 text-sm text-slate-500">From the sample zone list.</p>
        </article>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <article className="rounded-2xl border border-line bg-white p-5 shadow-sm">
          <h2 className="font-display text-xl font-bold text-navy">Pedestrian movement</h2>
          <p className="text-sm text-slate-500">{period === "daily" ? "One sample week." : "Four sample weeks."}</p>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trend}>
                <CartesianGrid stroke="#e7f3fb" />
                <XAxis dataKey="day" tick={{ fill: "#64748b", fontSize: 12 }} />
                <YAxis tick={{ fill: "#64748b", fontSize: 12 }} />
                <Tooltip />
                <Line type="monotone" dataKey="pedestrians" stroke="#0b1f3a" strokeWidth={3} />
                <Line type="monotone" dataKey="conflicts" stroke="#e11d48" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </article>
        <article className="rounded-2xl border border-line bg-white p-5 shadow-sm">
          <h2 className="font-display text-xl font-bold text-navy">Traffic density by zone</h2>
          <p className="text-sm text-slate-500">Sample concern scores, not live detector output.</p>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={zoneComparison}>
                <CartesianGrid stroke="#e7f3fb" />
                <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 11 }} />
                <YAxis tick={{ fill: "#64748b", fontSize: 12 }} />
                <Tooltip labelFormatter={(_, payload) => payload?.[0]?.payload?.fullName || ""} />
                <Legend />
                <Bar dataKey="traffic" name="Traffic density" fill="#1c9ad6" radius={[6, 6, 0, 0]} />
                <Bar dataKey="risk" name="Risk %" fill="#0b1f3a" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>
      </section>

      <article className="rounded-2xl border border-line bg-white p-5 shadow-sm">
        <h2 className="font-display text-xl font-bold text-navy">Hourly pedestrian trend</h2>
        <div className="mt-4 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={hourlyMovement}>
              <XAxis dataKey="hour" tick={{ fill: "#64748b", fontSize: 12 }} />
              <YAxis tick={{ fill: "#64748b", fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="people" name="People" fill="#38bdf8" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </article>
    </div>
  );
}
