export default function Logo({ light = false }) {
  const title = light ? "text-white" : "text-navy";
  const sub = light ? "text-sky-200" : "text-slate-500";

  return (
    <span className="flex items-center gap-3">
      <svg width="36" height="36" viewBox="0 0 32 32" aria-hidden="true">
        <rect width="32" height="32" rx="8" fill={light ? "#38BDF8" : "#0B1F3A"} />
        <path d="M16 5.5 25 9.2v6.4c0 5-3.6 8.6-9 10.4-5.4-1.8-9-5.4-9-10.4V9.2L16 5.5Z" fill={light ? "#0B1F3A" : "#38BDF8"} />
        <circle cx="16" cy="13" r="1.7" fill={light ? "#E0F2FE" : "#0B1F3A"} />
        <path d="M16 15.2c-1.8 0-3.2 1-3.2 2.4V21h1.6v-2.6h1v4.2h1.2v-4.2h1V21h1.6v-3.4c0-1.4-1.4-2.4-3.2-2.4Z" fill={light ? "#E0F2FE" : "#0B1F3A"} />
      </svg>
      <span>
        <span className={`block font-display text-lg font-bold leading-none ${title}`}>PedSafe</span>
        <span className={`mt-1 block text-xs leading-none ${sub}`}>Demo safety monitor</span>
      </span>
    </span>
  );
}
