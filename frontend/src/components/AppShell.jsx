import { useState } from "react";
import { Link } from "react-router-dom";
import DemoBanner from "./DemoBanner";
import Logo from "./Logo";
import Sidebar from "./Sidebar";

export default function AppShell({ children }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-screen bg-paper">
      <DemoBanner />
      <div className="lg:flex">
        <Sidebar open={open} onNavigate={() => setOpen(false)} />
        {open ? (
          <button
            type="button"
            aria-label="Close menu"
            className="no-print fixed inset-0 z-20 bg-navy/40 lg:hidden"
            onClick={() => setOpen(false)}
          />
        ) : null}
        <div className="min-w-0 flex-1">
          <div className="no-print flex items-center justify-between gap-3 border-b border-line bg-white px-4 py-3 lg:px-8">
            <div className="flex items-center gap-3">
              <button
                type="button"
                className="rounded-lg border border-line px-3 py-2 text-sm font-semibold text-navy lg:hidden"
                onClick={() => setOpen(true)}
              >
                Menu
              </button>
              <Link to="/" className="hidden sm:block">
                <Logo />
              </Link>
            </div>
            <Link to="/" className="text-sm font-semibold text-accent">
              Back to home
            </Link>
          </div>
          <main className="px-4 py-6 lg:px-8 lg:py-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
