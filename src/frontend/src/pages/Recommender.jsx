import React, { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Plus } from "lucide-react";
import { GAMES, USER } from "../data/games";
import { SelectableLibraryCard } from "../components/GameCard";

export default function Recommender() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState(new Set(["bloodborne", "elden-ring", "witcher-3"]));
  const [q, setQ] = useState("");

  const toggle = (id) => {
    const next = new Set(selected);
    next.has(id) ? next.delete(id) : next.add(id);
    setSelected(next);
  };

  const library = useMemo(
    () => GAMES.filter((g) => g.title.toLowerCase().includes(q.toLowerCase())),
    [q]
  );

  const selectedGames = [...selected].map((id) => GAMES.find((g) => g.id === id)).filter(Boolean);

  const handleGenerate = () => {
    if (selected.size < 3) return;
    const titles = selectedGames.map((g) => g.title).join(",");
    navigate(`/recommendations?based=${encodeURIComponent(titles)}`);
  };

  const canGenerate = selected.size >= 3;

  return (
    <div className="max-w-[1400px] mx-auto fade-up">
      <h1 className="font-display font-black text-[44px] leading-[1.05] mb-3">Wybierz swoje ulubione</h1>
      <p className="text-[15px] mb-8 max-w-[620px]" style={{ color: "var(--text-dim)" }}>
        Zaznacz co najmniej 3 gry ze swojej biblioteki Steam, abyśmy mogli wygenerować dla Ciebie idealne rekomendacje.
      </p>

      {/* Stats banner */}
      <div
        data-testid="selection-banner"
        className="rounded-2xl border p-6 flex items-center justify-between flex-wrap gap-6 mb-8"
        style={{ background: "var(--panel)", borderColor: selected.size >= 3 ? "var(--teal-dim)" : "var(--border)" }}
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
              <span className="font-mono text-[11px] uppercase tracking-wider" style={{ color: "var(--text-dim)" }}>
                Wybrane
              </span>
            </div>
          </div>
          <div>
            <div className="flex items-baseline gap-2">
              <span className="font-display font-black text-[32px]" style={{ color: "var(--purple-2)" }}>
                {USER.libraryCount}
              </span>
              <span className="font-mono text-[11px] uppercase tracking-wider" style={{ color: "var(--text-dim)" }}>
                W Bibliotece
              </span>
            </div>
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
            boxShadow: canGenerate ? "0 0 32px -8px rgba(94, 234, 212, 0.6)" : "none",
          }}
        >
          Generuj rekomendacje
        </button>
      </div>

      {/* Selected row */}
      {selectedGames.length > 0 && (
        <div className="mb-10">
          <div className="font-mono text-[10px] uppercase tracking-wider mb-4" style={{ color: "var(--text-faint)" }}>
            Wybrane tytuły
          </div>
          <div className="flex gap-4 flex-wrap">
            {selectedGames.map((g) => (
              <div
                key={g.id}
                data-testid={`selected-${g.id}`}
                onClick={() => toggle(g.id)}
                className="w-[120px] aspect-[2/3] rounded-lg overflow-hidden border-2 cursor-pointer transition-all hover:-translate-y-1"
                style={{ borderColor: "var(--teal)", boxShadow: "0 0 20px -4px rgba(94, 234, 212, 0.5)" }}
              >
                <img
                  src={g.cover}
                  alt={g.title}
                  className="w-full h-full object-cover"
                  onError={(e) => { e.target.src = `https://placehold.co/240x360/0F1624/5EEAD4?text=${encodeURIComponent(g.title)}`; }}
                />
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
      <div data-testid="library-grid" className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-5">
        {library.map((g, i) => (
          <div key={g.id} className="fade-up" style={{ animationDelay: `${i * 40}ms` }}>
            <SelectableLibraryCard game={g} selected={selected.has(g.id)} onToggle={toggle} />
          </div>
        ))}
        <button
          data-testid="load-more-btn"
          className="rounded-xl border-2 border-dashed flex flex-col items-center justify-center gap-2 aspect-[2/3] transition-all hover:border-[color:var(--teal-dim)]"
          style={{ borderColor: "var(--border-hover)", background: "transparent", color: "var(--text-dim)" }}
        >
          <Plus size={28} />
          <span className="font-mono text-[10px] uppercase tracking-wider">Wczytaj więcej</span>
        </button>
      </div>
    </div>
  );
}


