import { NavLink } from "react-router-dom";
import Logo from "./Logo";

const links = [
  { to: "/", label: "Home" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/risk", label: "Risk Prediction" },
  { to: "/conflicts", label: "Conflict Detection" },
  { to: "/analytics", label: "Analytics" },
  { to: "/about", label: "About" },
];

export default function Navbar() {
  return (
    <header className="no-print sticky top-0 z-40 border-b border-white/10 bg-navy text-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <NavLink to="/" className="shrink-0">
          <Logo light />
        </NavLink>
        <nav className="hidden items-center gap-1 lg:flex">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className={({ isActive }) =>
                `rounded-full px-3 py-2 text-sm font-semibold ${isActive ? "bg-white text-navy" : "text-sky-100 hover:bg-white/10"}`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
        <NavLink to="/dashboard" className="rounded-full bg-accent px-4 py-2 text-sm font-bold text-white hover:bg-sky-500">
          Get Started
        </NavLink>
      </div>
      <nav className="flex gap-2 overflow-x-auto px-4 pb-3 lg:hidden">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === "/"}
            className={({ isActive }) =>
              `shrink-0 rounded-full px-3 py-1.5 text-sm font-semibold ${isActive ? "bg-white text-navy" : "bg-white/10 text-sky-100"}`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
