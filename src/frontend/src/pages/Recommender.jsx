import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Plus } from "lucide-react";
import { USER } from "../data/games";
import { SelectableLibraryCard } from "../components/GameCard";
import { HelpCircle } from "lucide-react";

export default function Recommender() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState(new Set());
  const [q, setQ] = useState("");
  const [library, setLibrary] = useState([]);
  const [selectedGames, setSelectedGames] = useState([]);
  const [ratings, setRatings] = useState({});

  const toggle = (id) => {
    const strId = String(id);
    const next = new Set(selected);
    if (next.has(strId)) {
      next.delete(strId);
      setRatings((prev) => {
        const updated = { ...prev };
        delete updated[strId];
        return updated;
      });
    } else {
      next.add(strId);
    }
    setSelected(next);
  };

  const ratedCount = Object.keys(ratings).length;
  const isRatingMode = ratedCount > 0;
  const allRated = ratedCount === selected.size;
  const canGenerate = selected.size >= 2 && (!isRatingMode || allRated);

  React.useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (q.trim()) {
        fetch(`http://localhost:8000/search?q=${encodeURIComponent(q)}`)
          .then((res) => res.json())
          .then((data) => setLibrary(data))
          .catch((err) => console.error(err));
      } else {
        fetch(`http://localhost:8000/search?q=&limit=20`)
          .then((res) => res.json())
          .then((data) => setLibrary(data))
          .catch((err) => console.error(err));
      }
    }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [q]);

  React.useEffect(() => {
    const ids = Array.from(selected).join(",");
    if (ids) {
      fetch(`http://localhost:8000/games?ids=${ids}`)
        .then((res) => res.json())
        .then((data) => {
          // Remove duplicates just in case
          const unique = [];
          const seen = new Set();
          for (const g of data) {
            if (!seen.has(String(g.id))) {
              seen.add(String(g.id));
              unique.push(g);
            }
          }
          setSelectedGames(unique);
        })
        .catch((err) => console.error(err));
    } else {
      setSelectedGames([]);
    }
  }, [selected]);

  const handleGenerate = () => {
    if (!canGenerate) return;
    const payload = selectedGames
      .map((g) => {
        const r = ratings[g.id] || 1;
        return `${g.title}::${r}`;
      })
      .join("||");
    navigate(`/recommendations?payload=${encodeURIComponent(payload)}`);
  };

  return (
    <div className="max-w-[1400px] mx-auto fade-up">
      <h1 className="font-display font-black text-[44px] leading-[1.05] mb-3">
        Wybierz swoje ulubione gry
      </h1>
      <p
        className="text-[15px] mb-8 max-w-[800px]"
        style={{ color: "var(--text-dim)" }}
      >
        Zaznacz co najmniej 2 gry ze swojej biblioteki Steam, abyśmy mogli
        wygenerować rekomendowane dla ciebie gry. Dodatkowo, mozesz dodać ocenę
        podanej gry, w celu lepszego dopasowania. Jeżeli zdecydujesz się na
        ocenę podanych gier, wypełnij wszystkie ratingi, aby zapewnić systemowi
        odpowiednie informacje.
      </p>

      {/* Stats banner */}
      <div
        data-testid="selection-banner"
        className="rounded-2xl border p-6 flex items-center justify-between flex-wrap gap-6 mb-8"
        style={{
          background: "var(--panel)",
          borderColor: "var(--border)",
        }}
      >
        <div className="flex items-center gap-10">
          <div>
            <div className="flex items-baseline gap-2">
              <span
                data-testid="selected-count"
                className="font-display font-black text-[32px]"
                style={{ color: selected.size >= 3 ? "var(--teal)" : "white" }}
              >
                {selected.size}
              </span>
              <span
                className="font-mono text-[11px] uppercase tracking-wider"
                style={{ color: "var(--text-dim)" }}
              >
                Wybrane
              </span>
            </div>
          </div>
          <div>
            <div className="flex items-baseline gap-2">
              <span
                className="font-display font-black text-[32px]"
                style={{ color: "var(--purple-2)" }}
              >
                {USER.libraryCount}
              </span>
              <span
                className="font-mono text-[11px] uppercase tracking-wider"
                style={{ color: "var(--text-dim)" }}
              >
                W Bibliotece
              </span>
            </div>
          </div>
        </div>
        <div className="flex flex-row gap-2 items-center">
          <div
            className={`group relative flex items-center justify-center p-2 ${canGenerate ? "invisible" : ""}`}
          >
            <HelpCircle className="font-display text-center text-red-400 max-w-[100px] text-sm cursor-pointer" />

            {/* Tooltip */}
            <div className="absolute bottom-full mb-2 hidden w-64 rounded bg-gray-900 p-2 text-xs text-white group-hover:block z-10 shadow-lg font-sans text-left">
              Zaznacz minimum 2 gry i do wszystkich dodaj oceny, aby wygenerować
              rekomendacje.
            </div>
          </div>
          <button
            data-testid="generate-recommendations-btn"
            disabled={!canGenerate}
            onClick={handleGenerate}
            className="h-12 px-8 rounded-full font-display font-bold text-[14px] tracking-wide transition-all"
            style={{
              background: canGenerate ? "var(--teal)" : "var(--panel-2)",
              color: canGenerate ? "#04111A" : "var(--text-faint)",
              cursor: canGenerate ? "pointer" : "not-allowed",
              boxShadow: canGenerate
                ? "0 0 32px -8px rgba(94, 234, 212, 0.6)"
                : "none",
            }}
          >
            Generuj rekomendacje
          </button>
        </div>
      </div>

      {/* Selected row */}
      {selectedGames.length > 0 && (
        <div className="mb-10">
          <div
            className="font-mono text-[10px] uppercase tracking-wider mb-4"
            style={{ color: "var(--text-faint)" }}
          >
            Wybrane tytuły
          </div>
          <div className="flex gap-4 flex-wrap">
            {selectedGames
              .filter((g) => selected.has(String(g.id)))
              .map((g) => (
                <div
                  key={g.id}
                  className="flex flex-col items-center bg-black w-[220px] h-[200px] rounded-2xl pt-4 gap-3"
                  style={{ background: "var(--panel)" }}
                >
                  <div
                    data-testid={`selected-${g.id}`}
                    onClick={() => toggle(g.id)}
                    className="w-[200px] aspect-[460/215] rounded-lg overflow-hidden border-2 cursor-pointer transition-all hover:-translate-y-1 bg-[#0A1018] shrink-0"
                    style={{
                      borderColor: "var(--teal)",
                      boxShadow: "0 0 20px -4px rgba(94, 234, 212, 0.5)",
                    }}
                  >
                    <img
                      src={g.cover}
                      alt={g.title}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.src = `https://placehold.co/460x215/0F1624/5EEAD4?text=${encodeURIComponent(g.title)}`;
                      }}
                    />
                  </div>
                  <div className="flex flex-col w-full px-4 gap-2">
                    <label
                      htmlFor={`rating-${g.id}`}
                      className="text-white text-sm mb-1"
                    >
                      Oceń grę w skali 1-10. <br />
                      <span>
                        Twoja ocena: {ratings[g.id] || <i>Nie zaznaczono</i>}
                      </span>
                    </label>
                    <input
                      id={`rating-${g.id}`}
                      type="range"
                      min="1"
                      max="10"
                      step="1"
                      value={ratings[g.id] || 1}
                      onChange={(e) =>
                        setRatings({
                          ...ratings,
                          [g.id]: parseInt(e.target.value),
                        })
                      }
                      className={`w-full cursor-pointer transition-opacity duration-300 ${ratings[g.id] ? "accent-teal-400 opacity-100" : "accent-gray-600 opacity-40 hover:opacity-80"}`}
                    />
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Search */}
      <div className="mb-6">
        <div
          className="flex items-center gap-3 h-12 px-5 rounded-full border max-w-[520px]"
          style={{ background: "var(--panel)", borderColor: "var(--border)" }}
        >
          <Search size={16} style={{ color: "var(--text-faint)" }} />
          <input
            data-testid="library-search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Wyszukaj gry w bibliotece..."
            className="flex-1 bg-transparent border-none outline-none text-[14px] placeholder:text-[color:var(--text-faint)]"
          />
        </div>
      </div>

      {/* Library grid */}
      <div
        data-testid="library-grid"
        className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-5"
      >
        {library.map((g, i) => (
          <div
            key={g.id}
            className="fade-up"
            style={{ animationDelay: `${i * 40}ms` }}
          >
            <SelectableLibraryCard
              game={g}
              selected={selected.has(String(g.id))}
              onToggle={toggle}
            />
          </div>
        ))}
        <button
          data-testid="load-more-btn"
          className="rounded-xl border-2 border-dashed flex flex-col items-center justify-center gap-2 transition-all hover:border-[color:var(--teal-dim)] w-full"
          style={{
            borderColor: "var(--border-hover)",
            background: "transparent",
            color: "var(--text-dim)",
            minHeight: "180px",
          }}
        >
          <Plus size={28} />
          <span className="font-mono text-[10px] uppercase tracking-wider">
            Wczytaj więcej
          </span>
        </button>
      </div>
    </div>
  );
}
