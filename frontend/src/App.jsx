import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppShell from "./components/AppShell";
import AboutPage from "./pages/AboutPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import ConflictsPage from "./pages/ConflictsPage";
import DashboardPage from "./pages/DashboardPage";
import HomePage from "./pages/HomePage";
import RiskPage from "./pages/RiskPage";

function Inside({ children }) {
  return <AppShell>{children}</AppShell>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<Inside><DashboardPage /></Inside>} />
        <Route path="/risk" element={<Inside><RiskPage /></Inside>} />
        <Route path="/conflicts" element={<Inside><ConflictsPage /></Inside>} />
        <Route path="/analytics" element={<Inside><AnalyticsPage /></Inside>} />
        <Route path="/about" element={<Inside><AboutPage /></Inside>} />
      </Routes>
    </BrowserRouter>
  );
}
