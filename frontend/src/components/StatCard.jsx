export default function StatCard({ label, value, hint }) {
  return (
    <article className="rounded-2xl border border-line bg-white p-5 shadow-sm">
      <p className="text-sm font-semibold text-slate-500">{label}</p>
      <p className="mt-2 font-display text-3xl font-bold tracking-tight text-navy">{value}</p>
      <p className="mt-2 text-sm leading-5 text-slate-500">{hint}</p>
    </article>
  );
}
