import { Routes, Route } from "react-router-dom";
import { Layout } from "@/components/Layout";
import { OverviewPage } from "@/pages/OverviewPage";
import { MachineDetailPage } from "@/pages/MachineDetailPage";

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/machines/:id" element={<MachineDetailPage />} />
      </Route>
    </Routes>
  );
}

export default App;
