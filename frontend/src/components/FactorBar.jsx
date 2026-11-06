export default function FactorBar({ label, value }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm">
        <span className="font-medium text-slate-600">{label}</span>
        <span className="font-semibold text-navy">{value}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-ice">
        <div className="h-full rounded-full bg-accent" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}
