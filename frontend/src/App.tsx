import { BrowserRouter, Routes, Route } from "react-router";
import Navbar from "./components/Navbar";
import Landing from "./pages/Landing";
import SearchPage from "./pages/Search";
import GraphView from "./pages/GraphView";
import Patterns from "./pages/Patterns";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main style={{ flex: 1 }}>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/graph/:id" element={<GraphView />} />
          <Route path="/patterns" element={<Patterns />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
