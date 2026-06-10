import React, { useMemo, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { GAMES, GENRES } from "../data/games";
import { GameCard } from "../components/GameCard";

export default function Browse() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const initialQ = params.get("q") || "";
  const [q, setQ] = useState(initialQ);
  const [active, setActive] = useState("Wszystko");

  const filtered = useMemo(() => {
    let list = GAMES.filter((g) =>
      g.title.toLowerCase().includes(q.toLowerCase()),
    );
    if (active !== "Wszystko") {
      list = list.filter(
        (g) =>
          g.genre.some((gn) =>
            gn.toLowerCase().includes(active.toLowerCase()),
          ) || g.tag.toLowerCase() === active.toLowerCase(),
      );
    }
    return list;
  }, [q, active]);

  const chips = ["Wszystko", ...GENRES];

  return (
    <div className="max-w-[1400px] mx-auto fade-up">
      <h1 className="font-display font-black text-[44px] leading-none mb-3">
        Przeglądaj gry
      </h1>
      <p className="text-[15px] mb-8" style={{ color: "var(--text-dim)" }}>
        Odkryj tytuły dopasowane do Twoich gustów — od klasyków po najnowsze
        premiery.
      </p>

      <div className="mb-8 flex flex-wrap gap-6 items-center justify-between">
        <input
          data-testid="browse-search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Wyszukaj gry..."
          className="h-12 px-5 rounded-full border bg-[color:var(--panel)] outline-none text-[14px] flex-1 min-w-[260px] max-w-[480px] placeholder:text-[color:var(--text-faint)]"
          style={{ borderColor: "var(--border)" }}
        />
        <div className="flex flex-wrap gap-2">
          {chips.map((c) => (
            <button
              key={c}
              data-testid={`browse-chip-${c.toLowerCase()}`}
              onClick={() => setActive(c)}
              className="px-4 h-9 rounded-full font-display font-semibold text-[12px] transition-all"
              style={{
                background: active === c ? "var(--teal)" : "var(--panel)",
                color: active === c ? "#04111A" : "var(--text-dim)",
                border: `1px solid ${active === c ? "var(--teal)" : "var(--border)"}`,
              }}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <div
        className="mb-4 font-mono text-[11px] uppercase tracking-wider"
        style={{ color: "var(--text-faint)" }}
      >
        Znaleziono:{" "}
        <span style={{ color: "var(--teal)" }}>{filtered.length}</span> tytułów
      </div>

      {filtered.length === 0 ? (
        <div
          data-testid="browse-empty"
          className="rounded-2xl border p-12 text-center"
          style={{ background: "var(--panel)", borderColor: "var(--border)" }}
        >
          <div className="font-display font-bold text-[20px] mb-2">
            Brak gier pasujących do zapytania
          </div>
          <p className="text-[14px]" style={{ color: "var(--text-dim)" }}>
            Spróbuj innego słowa kluczowego lub wyczyść filtry.
          </p>
        </div>
      ) : (
        <div
          data-testid="browse-grid"
          className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-5"
        >
          {filtered.map((g, i) => (
            <div
              key={g.id}
              className="fade-up"
              style={{ animationDelay: `${i * 40}ms` }}
            >
              <GameCard game={g} onClick={() => navigate("/recommender")} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
