import { NavLink } from "react-router-dom";

const links = [
  { to: "/dashboard", label: "Dashboard", hint: "City overview" },
  { to: "/risk", label: "Risk Prediction", hint: "Zone map" },
  { to: "/conflicts", label: "Conflict Detection", hint: "Event log" },
  { to: "/analytics", label: "Analytics", hint: "Trends and reports" },
  { to: "/about", label: "About Project", hint: "Team and method" },
];

export default function Sidebar({ open, onNavigate }) {
  return (
    <aside
      className={`no-print fixed inset-y-0 left-0 z-30 w-72 transform border-r border-white/10 bg-navy text-white transition lg:static lg:translate-x-0 ${
        open ? "translate-x-0" : "-translate-x-full"
      }`}
    >
      <div className="border-b border-white/10 px-5 py-5">
        <p className="font-display text-lg font-bold">Monitor</p>
        <p className="mt-1 text-sm text-sky-200">Sample zone overlay</p>
      </div>
      <nav className="space-y-1 px-3 py-4">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            onClick={onNavigate}
            className={({ isActive }) =>
              `block rounded-xl px-3 py-3 ${isActive ? "bg-white text-navy" : "text-sky-100 hover:bg-white/10"}`
            }
          >
            <span className="block text-sm font-bold">{link.label}</span>
            <span className="block text-xs opacity-70">{link.hint}</span>
          </NavLink>
        ))}
      </nav>
      <div className="mx-3 rounded-2xl bg-white/10 p-4 text-sm leading-6 text-sky-100">
        Models are not connected. Every number in this panel is demonstration data.
      </div>
    </aside>
  );
}
