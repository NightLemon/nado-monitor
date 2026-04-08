import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "@/services/api";

export function LoginPage() {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(code);
      navigate("/", { replace: true });
    } catch {
      setError("Invalid code. Please try again.");
      setCode("");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="bg-slate-800 rounded-xl border border-slate-700 p-8">
          <h1 className="text-xl font-bold text-slate-100 text-center mb-1">
            Nado Monitor
          </h1>
          <p className="text-sm text-slate-400 text-center mb-6">
            Enter authenticator code
          </p>

          <form onSubmit={handleSubmit}>
            <input
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              maxLength={6}
              value={code}
              onChange={(e) =>
                setCode(e.target.value.replace(/\D/g, "").slice(0, 6))
              }
              placeholder="000000"
              autoFocus
              className="w-full text-center text-3xl tracking-[0.5em] font-mono
                bg-slate-900 border border-slate-600 rounded-lg px-4 py-3
                text-slate-100 placeholder-slate-600
                focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            />

            {error && (
              <p className="mt-3 text-sm text-red-400 text-center">{error}</p>
            )}

            <button
              type="submit"
              disabled={code.length !== 6 || loading}
              className="mt-6 w-full py-2.5 rounded-lg font-medium text-sm
                bg-emerald-600 text-white hover:bg-emerald-500
                disabled:opacity-40 disabled:cursor-not-allowed
                transition-colors cursor-pointer"
            >
              {loading ? "Verifying..." : "Sign in"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
