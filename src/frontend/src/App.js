import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Browse from "./pages/Browse";
import Recommender from "./pages/Recommender";
import Recommendations from "./pages/Recommendations";
import Library from "./pages/Library";
import Steam from "./pages/Steam";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/browse" element={<Browse />} />
            <Route path="/recommender" element={<Recommender />} />
            <Route path="/recommendations" element={<Recommendations />} />
            <Route path="/library" element={<Library />} />
            <Route path="/steam" element={<Steam />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </div>
  );
}

export default App;


