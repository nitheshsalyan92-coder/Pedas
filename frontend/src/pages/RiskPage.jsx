import { useMemo, useState } from "react";
import FactorBar from "../components/FactorBar";
import PageHeader from "../components/PageHeader";
import RiskBadge from "../components/RiskBadge";
import RiskMap from "../components/RiskMap";
import { zones } from "../data/sampleData";

const filters = ["All", "High", "Medium", "Low"];

const factorLabels = {
  trafficDensity: "Traffic density",
  pedestrianDensity: "Pedestrian density",
  roadConditions: "Road condition concern",
  lighting: "Lighting concern",
};

export default function RiskPage() {
  const [filter, setFilter] = useState("All");
  const [selectedId, setSelectedId] = useState(zones[0].id);

  const visible = useMemo(
    () => zones.filter((zone) => filter === "All" || zone.level === filter),
    [filter],
  );
  const selected = visible.find((zone) => zone.id === selectedId) ?? visible[0];

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Risk prediction"
        title="Where the sample risk is higher"
        text="Colors show the demo label for each place. A higher percentage means the sample record marked that zone as more concerning. It is not a forecast that a crash will occur."
      >
        {filters.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setFilter(item)}
            className={`rounded-full px-4 py-2 text-sm font-bold ${filter === item ? "bg-navy text-white" : "bg-white text-navy ring-1 ring-line"}`}
          >
            {item}
          </button>
        ))}
      </PageHeader>

      <div className="grid gap-4 xl:grid-cols-[1.4fr_0.8fr]">
        <section className="overflow-hidden rounded-2xl border border-line bg-white p-3 shadow-sm">
          <RiskMap zones={visible} selectedId={selected?.id} onSelect={setSelectedId} />
          <div className="flex flex-wrap gap-4 px-2 py-3 text-sm text-slate-600">
            <span className="flex items-center gap-2"><i className="h-3 w-3 rounded-full bg-rose-600" /> High</span>
            <span className="flex items-center gap-2"><i className="h-3 w-3 rounded-full bg-amber-600" /> Medium</span>
            <span className="flex items-center gap-2"><i className="h-3 w-3 rounded-full bg-emerald-600" /> Low</span>
            <span>Map imagery © OpenStreetMap. Pins are demo locations.</span>
          </div>
        </section>

        <aside className="space-y-4">
          {selected ? (
            <article className="rounded-2xl border border-line bg-white p-5 shadow-sm">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="font-display text-2xl font-bold text-navy">{selected.name}</h2>
                  <p className="text-sm text-slate-500">{selected.area}</p>
                </div>
                <RiskBadge level={selected.level} />
              </div>
              <p className="mt-4 font-display text-4xl font-bold text-navy">{selected.riskPercent}%</p>
              <p className="text-sm text-slate-500">Sample predicted risk for this location.</p>
              <p className="mt-3 text-sm leading-6 text-slate-600">{selected.note}</p>
              <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-xl bg-paper p-3">
                  <p className="text-slate-500">Pedestrians</p>
                  <p className="font-display text-xl font-bold text-navy">{selected.pedestrians}</p>
                </div>
                <div className="rounded-xl bg-paper p-3">
                  <p className="text-slate-500">Vehicles</p>
                  <p className="font-display text-xl font-bold text-navy">{selected.vehicles}</p>
                </div>
              </div>
              <div className="mt-5 space-y-3">
                {Object.entries(selected.factors).map(([key, value]) => (
                  <FactorBar key={key} label={factorLabels[key]} value={value} />
                ))}
              </div>
              <p className="mt-3 text-xs text-slate-500">Higher bars mean a stronger concern in the sample record.</p>
            </article>
          ) : (
            <article className="rounded-2xl border border-line bg-white p-5 text-slate-600">No zones match this filter.</article>
          )}

          <ul className="max-h-80 space-y-2 overflow-auto">
            {visible.map((zone) => (
              <li key={zone.id}>
                <button
                  type="button"
                  onClick={() => setSelectedId(zone.id)}
                  className={`flex w-full items-center justify-between rounded-2xl border px-4 py-3 text-left ${
                    selected?.id === zone.id ? "border-accent bg-ice" : "border-line bg-white"
                  }`}
                >
                  <span>
                    <span className="block font-semibold text-navy">{zone.name}</span>
                    <span className="text-sm text-slate-500">{zone.riskPercent}% sample risk</span>
                  </span>
                  <RiskBadge level={zone.level} />
                </button>
              </li>
            ))}
          </ul>
        </aside>
      </div>
    </div>
  );
}
