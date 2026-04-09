import { useState, useEffect } from "react";
import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { OverviewPage } from "@/pages/OverviewPage";
import { MachineDetailPage } from "@/pages/MachineDetailPage";
import { LoginPage } from "@/pages/LoginPage";
import { isAuthenticated } from "@/services/api";

function ProtectedRoute() {
  const [authState, setAuthState] = useState<"loading" | "yes" | "no">(
    "loading",
  );

  useEffect(() => {
    isAuthenticated().then((ok) => setAuthState(ok ? "yes" : "no"));
  }, []);

  if (authState === "loading") return null;
  if (authState === "no") return <Navigate to="/login" replace />;
  return <Outlet />;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/machines/:id" element={<MachineDetailPage />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
