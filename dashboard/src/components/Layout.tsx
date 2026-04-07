import { Link, Outlet } from "react-router-dom";
import { Activity } from "lucide-react";

export function Layout() {
  return (
    <div className="min-h-screen bg-slate-900">
      <nav className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2 text-white no-underline">
            <Activity className="w-6 h-6 text-emerald-400" />
            <span className="text-lg font-semibold">Nado Monitor</span>
          </Link>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
