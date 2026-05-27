import React, { useMemo, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { RotateCcw } from "lucide-react";
import { GAMES, PLATFORMS, GENRES } from "../data/games";
import { RecGameCard } from "../components/GameCard";

export default function Recommendations() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const basedOnStr = params.get("based") || "";
  const basedTitles = basedOnStr.split("||").filter(Boolean);
  const basedOn = basedTitles.join(", ") || "Wybierz gry, aby wygenerować rekomendacje";

  const [priceRange, setPriceRange] = useState(300);
  const [platforms, setPlatforms] = useState({ pc: true, ps5: false, xbox: false, steamdeck: false });
  const [genres, setGenres] = useState({ RPG: false, FPS: false, Horror: false, Indie: false, Action: false });

  const [recsData, setRecsData] = useState([]);
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (basedTitles.length === 0) return;
    
    const abortController = new AbortController();
    const { signal } = abortController;
    
    setLoading(true);
    
    // Construct query parameters for FastAPI Query list
    const queryParams = basedTitles.map(t => `movie_list=${encodeURIComponent(t)}`).join('&');
    
    fetch(`http://localhost:8000/recommender?${queryParams}`, { signal })
      .then(res => res.json())
      .then(data => {
        // data is a list of dicts: [ {"Game A": 0.95}, {"Game B": 0.92} ]
        const formatted = data.map(item => {
          const gameName = Object.keys(item)[0];
          const similarity = item[gameName];
          return { name: gameName, match: Math.round(similarity * 100) };
        });
        
        // Now fetch details for these games from backend
        const namesQuery = formatted.map(g => g.name).join("||");
        return fetch(`http://localhost:8000/games_by_name?names=${encodeURIComponent(namesQuery)}`, { signal })
          .then(res => res.json())
          .then(details => {
             // Merge details with match score
             const merged = formatted.map(rec => {
               // find corresponding game detail
               const detail = details.find(d => d.title === rec.name);
               return {
                  id: detail ? detail.id : rec.name,
                  title: rec.name,
                  match: rec.match,
                  cover: detail ? detail.cover : "", // fallback cover handled in card
                  tag: detail && detail.genre ? detail.genre[0] : "INNE",
                  price: 0, // Placeholder
                  discount: 0,
                  rating: 8.5,
                  platforms: ["pc"],
                  genre: detail ? detail.genre : []
               };
             });
             setRecsData(merged);
             setLoading(false);
          });
      })
      .catch(err => {
        if (err.name === 'AbortError') {
          console.log('Request aborted');
        } else {
          console.error(err);
          setLoading(false);
        }
      });
      
    // Cleanup function when the component unmounts or basedOnStr changes
    return () => {
      abortController.abort();
    };
  }, [basedOnStr]);

  const togglePlatform = (id) => setPlatforms((p) => ({ ...p, [id]: !p[id] }));
  const toggleGenre = (g) => setGenres((x) => ({ ...x, [g]: !x[g] }));

  const reset = () => {
    setPriceRange(300);
    setPlatforms({ pc: true, ps5: false, xbox: false, steamdeck: false });
    setGenres({ RPG: false, FPS: false, Horror: false, Indie: false, Action: false });
  };

  const recs = useMemo(() => {
    let list = [...recsData];

    // price filter 
    list = list.filter((g) => {
      const final = g.price * (1 - g.discount / 100);
      return final <= priceRange;
    });

    // platform filter 
    const activePlatforms = Object.keys(platforms).filter((k) => platforms[k]);
    if (activePlatforms.length > 0) {
      list = list.filter((g) => activePlatforms.some((p) => g.platforms.includes(p)));
    }

    // genre filter
    const activeGenres = Object.keys(genres).filter((k) => genres[k]);
    if (activeGenres.length > 0) {
      list = list.filter((g) =>
        activeGenres.some((gg) =>
          g.genre && g.genre.some((gn) => gn.toLowerCase().includes(gg.toLowerCase()))
        )
      );
    }

    return list;
  }, [priceRange, platforms, genres, recsData]);

  return (
    <div className="max-w-[1400px] mx-auto fade-up">
      <div className="flex items-start justify-between mb-10 flex-wrap gap-4">
        <div>
          <h1 className="font-display font-black text-[48px] leading-[1.05] mb-3">Rekomendacje dla Ciebie</h1>
          <p className="text-[14px]" style={{ color: "var(--text-dim)" }}>
            Wygenerowane na podstawie: <span style={{ color: "var(--teal)" }}>{basedOn}</span>
          </p>
        </div>
        <button
          data-testid="pick-other-games-btn"
          onClick={() => navigate("/recommender")}
          className="h-11 px-6 rounded-full font-display font-bold text-[13px] transition-all hover:scale-105"
          style={{ background: "var(--teal)", color: "#04111A" }}
        >
          Wybierz inne gry
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-8">
        {/* Filters */}
        <aside
          data-testid="filters-panel"
          className="rounded-2xl border p-6 h-fit sticky top-4"
          style={{ background: "var(--panel)", borderColor: "var(--border)" }}
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-display font-bold text-[20px]">Filtry</h3>
            <button
              data-testid="reset-filters-btn"
              onClick={reset}
              className="flex items-center gap-1 font-mono text-[10px] uppercase tracking-wider hover:underline"
              style={{ color: "var(--teal)" }}
            >
              <RotateCcw size={11} /> Reset
            </button>
          </div>

          {/* Price */}
          <div className="mb-7">
            <div className="font-mono text-[10px] uppercase tracking-[0.15em] mb-3"
                 style={{ color: "var(--text-faint)" }}>
              Cena (PLN)
            </div>
            <input
              data-testid="price-slider"
              type="range"
              min="0"
              max="500"
              step="10"
              value={priceRange}
              onChange={(e) => setPriceRange(+e.target.value)}
            />
            <div className="flex justify-between mt-2 font-mono text-[11px]" style={{ color: "var(--text-dim)" }}>
              <span>0 PLN</span>
              <span style={{ color: "var(--teal)" }}>{priceRange} PLN</span>
            </div>
          </div>

          {/* Platforms */}
          <div className="mb-7">
            <div className="font-mono text-[10px] uppercase tracking-[0.15em] mb-3"
                 style={{ color: "var(--text-faint)" }}>
              Platformy
            </div>
            <div className="flex flex-col gap-3">
              {PLATFORMS.map((p) => (
                <button
                  key={p.id}
                  data-testid={`platform-${p.id}`}
                  onClick={() => togglePlatform(p.id)}
                  className="flex items-center gap-3 text-left text-[13px] transition-colors"
                  style={{ color: platforms[p.id] ? "white" : "var(--text-dim)" }}
                >
                  <span className={`check-box ${platforms[p.id] ? "checked" : ""}`}>
                    {platforms[p.id] && (
                      <svg width="11" height="11" viewBox="0 0 12 12" fill="none">
                        <path d="M2 6L5 9L10 3" stroke="#04111A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    )}
                  </span>
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Genres */}
          <div>
            <div className="font-mono text-[10px] uppercase tracking-[0.15em] mb-3"
                 style={{ color: "var(--text-faint)" }}>
              Gatunki
            </div>
            <div className="flex flex-wrap gap-2">
              {["RPG", "FPS", "Horror", "Indie", "Action"].map((g) => (
                <button
                  key={g}
                  data-testid={`genre-${g.toLowerCase()}`}
                  onClick={() => toggleGenre(g)}
                  className="px-4 h-8 rounded-full font-display font-semibold text-[12px] transition-all"
                  style={{
                    background: genres[g] ? "var(--teal)" : "var(--panel-3)",
                    color: genres[g] ? "#04111A" : "var(--text-dim)",
                    border: `1px solid ${genres[g] ? "var(--teal)" : "var(--border)"}`,
                  }}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>
        </aside>

        {/* Results */}
        <div>
          {loading ? (
            <div className="rounded-2xl border p-12 text-center flex flex-col items-center justify-center gap-4 min-h-[300px]" style={{ background: "var(--panel)", borderColor: "var(--border)" }}>
              <div className="w-10 h-10 border-4 border-t-[color:var(--teal)] rounded-full animate-spin" style={{ borderColor: "var(--border)", borderTopColor: "var(--teal)" }}></div>
              <div className="font-display font-bold text-[18px]">Generowanie rekomendacji...</div>
              <p className="text-[14px] text-[color:var(--text-dim)]">Nasz model sztucznej inteligencji dopasowuje podobne pozycje do Twojej bazy...</p>
            </div>
          ) : recs.length === 0 ? (
            <div
              data-testid="empty-results"
              className="rounded-2xl border p-12 text-center"
              style={{ background: "var(--panel)", borderColor: "var(--border)" }}
            >
              <div className="font-display font-bold text-[20px] mb-2">Brak wyników</div>
              <p className="text-[14px]" style={{ color: "var(--text-dim)" }}>
                Spróbuj poluzować filtry lub zresetować je, aby zobaczyć rekomendacje.
              </p>
            </div>
          ) : (
            <div data-testid="recommendations-grid" className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
              {recs.map((g, i) => (
                <div key={g.id} className="fade-up" style={{ animationDelay: `${i * 60}ms` }}>
                  <RecGameCard game={g} match={g.match} onMore={() => navigate("/browse")} />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


