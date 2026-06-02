import React, { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Info, Plus, Zap, ChevronDown, ArrowRight } from "lucide-react";
import { GAMES } from "../data/games";
import { GameCard } from "../components/GameCard";

const CHIPS = ["RPG", "FPS", "Indie"];

export default function Home() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState("RPG");

  const hero = GAMES.find((g) => g.id === "cyberpunk");

  const recommended = useMemo(() => {
    const map = {
      RPG: ["elden-ring", "dark-souls-3", "baldurs-gate-3", "bloodborne"],
      FPS: ["doom-eternal", "call-of-juarez", "cyberpunk", "baldurs-gate-3"],
      Indie: ["hades", "hollow-knight", "lies-of-p", "elden-ring"],
    };
    const ids = map[filter] || map.RPG;
    return ids.map((id) => GAMES.find((g) => g.id === id)).filter(Boolean);
  }, [filter]);

  const activityBased = [
    GAMES.find((g) => g.id === "rdr"),
    GAMES.find((g) => g.id === "call-of-juarez"),
  ];

  return (
    <div className="max-w-[1400px] mx-auto fade-up">
      {/* Hero card */}
      <section
        data-testid="hero-section"
        className="relative rounded-2xl overflow-hidden border mb-12"
        style={{ borderColor: "var(--border)", minHeight: "380px" }}
      >
        <img
          src={hero.hero || hero.cover}
          alt={hero.title}
          className="absolute inset-0 w-full h-full object-cover"
          onError={(e) => {
            e.target.src = hero.cover;
          }}
        />
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(90deg, rgba(5,8,15,0.95) 0%, rgba(5,8,15,0.7) 45%, rgba(5,8,15,0.3) 100%)",
          }}
        />
        <div className="relative p-10 max-w-[60%]">
          <div className="flex items-center gap-3 mb-5">
            <span
              className="px-3 py-1 rounded-full font-mono text-[10px] uppercase tracking-wider font-bold"
              style={{ background: "var(--teal)", color: "#04111A" }}
            >
              Ultra Match
            </span>
            <span
              className="font-mono text-[11px] uppercase tracking-wider"
              style={{ color: "var(--text-dim)" }}
            >
              Gry jednoosobowe
            </span>
          </div>
          <h1 className="font-display font-black text-[56px] leading-[1] mb-5 tracking-tight">
            Cyberpunk 2077
          </h1>
          <p
            className="text-[15px] leading-relaxed mb-7 max-w-[520px]"
            style={{ color: "var(--text-dim)" }}
          >
            Biorąc pod uwagę Twoje 450 godzin spędzonych w Wiedźminie 3 i
            zamiłowanie do gier RPG z otwartym światem, ta przesiąknięta neonami
            dystopia będzie Twoją kolejną obsesją.
          </p>
          <div className="flex items-center gap-3">
            <button
              data-testid="hero-details-btn"
              onClick={() => navigate("/browse")}
              className="flex items-center gap-2 h-12 px-7 rounded-full font-display font-bold text-[14px] transition-all hover:scale-105"
              style={{ background: "var(--teal)", color: "#04111A" }}
            >
              <Info size={16} />
              Szczegóły
            </button>
            <button
              onClick={() => navigate("/recommender")}
              className="flex items-center gap-2 h-12 px-7 rounded-full font-display font-bold text-[14px] border transition-colors hover:border-[color:var(--teal-dim)] hover:scale-105"
              style={{
                borderColor: "var(--border-hover)",
                background: "transparent",
                color: "white",
              }}
            >
              Rekomender
            </button>
          </div>
        </div>
      </section>

      {/* Recommended */}
      <section data-testid="recommended-section" className="mb-16">
        <div className="flex items-end justify-between mb-8 flex-wrap gap-4">
          <div>
            <h2 className="font-display font-black text-[36px] leading-none mb-2">
              Rekomendowane dla Ciebie
            </h2>
            <p className="text-[14px]" style={{ color: "var(--text-dim)" }}>
              Na podstawie Twojego stylu gry…
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span
              className="font-mono text-[10px] uppercase tracking-wider mr-2"
              style={{ color: "var(--text-faint)" }}
            >
              Filtruj:
            </span>
            {CHIPS.map((c) => (
              <button
                key={c}
                data-testid={`chip-${c.toLowerCase()}`}
                onClick={() => setFilter(c)}
                className="px-4 h-9 rounded-full font-display font-semibold text-[12px] transition-all"
                style={{
                  background: filter === c ? "var(--teal)" : "var(--panel)",
                  color: filter === c ? "#04111A" : "var(--text-dim)",
                  border:
                    filter === c
                      ? "1px solid var(--teal)"
                      : "1px solid var(--border)",
                }}
              >
                {c}
              </button>
            ))}
            <button
              data-testid="chip-genre"
              className="flex items-center gap-1.5 px-4 h-9 rounded-full font-display font-semibold text-[12px] border transition-colors"
              style={{
                background: "var(--panel)",
                borderColor: "var(--border)",
                color: "var(--text-dim)",
              }}
            >
              Gatunek <ChevronDown size={14} />
            </button>
          </div>
          <button
            onClick={() => navigate("/recommender")}
            className="rounded-full font-display font-bold text-[14px] border transition-colors px-5 h-7"
            style={{
              background: "var(--teal)",
              borderColor: "var(--teal)",
              color: "#04111A",
            }}
          >
            Pokaż więcej
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
          {recommended.map((g, i) => (
            <div
              key={g.id}
              className="fade-up"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <GameCard game={g} onClick={() => navigate("/browse")} />
            </div>
          ))}
        </div>
      </section>

      {/* Activity-based */}
      <section data-testid="activity-section" className="mb-10">
        <div className="flex items-center gap-3 mb-6">
          <div
            className="w-10 h-10 rounded-full grid place-items-center"
            style={{
              background: "var(--panel-2)",
              border: "1px solid var(--border)",
            }}
          >
            <Zap size={16} style={{ color: "var(--teal)" }} />
          </div>
          <div>
            <div className="font-display font-bold text-[20px]">
              Na podstawie Twojej ostatniej aktywności…
            </div>
            <div className="text-[13px]" style={{ color: "var(--text-dim)" }}>
              Ponieważ niedawno grałeś w{" "}
              <span style={{ color: "var(--teal)" }}>
                Red Dead Redemption 2
              </span>
            </div>
          </div>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          {activityBased.map((g) => {
            if (!g) return null;
            return (
              <div
                key={g.id}
                data-testid={`activity-${g.id}`}
                onClick={() => navigate("/browse")}
                className="flex items-center gap-5 p-4 rounded-xl border cursor-pointer transition-all hover:border-[color:var(--teal-dim)]"
                style={{
                  background: "var(--panel)",
                  borderColor: "var(--border)",
                }}
              >
                <img
                  src={g.cover}
                  alt={g.title}
                  className="w-20 h-28 object-cover rounded-lg flex-shrink-0"
                  onError={(e) => {
                    e.target.src = `https://placehold.co/200x280/0F1624/5EEAD4?text=${encodeURIComponent(g.title)}`;
                  }}
                />
                <div className="flex-1 min-w-0">
                  <div className="font-display font-bold text-[17px] mb-1 truncate">
                    {g.title}
                  </div>
                  <div
                    className="text-[12px] mb-3 line-clamp-2"
                    style={{ color: "var(--text-dim)" }}
                  >
                    Przygodowa gra akcji z 2010 roku; wyprodukowana przez
                    Rockstar San Diego.
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-display font-bold text-[14px]">
                      {(g.price * (1 - g.discount / 100)).toFixed(2)} zł
                    </span>
                    {g.discount > 0 && (
                      <span
                        className="px-2 py-0.5 rounded font-mono text-[9px] uppercase font-bold"
                        style={{
                          background: "rgba(94,234,212,0.15)",
                          color: "var(--teal)",
                        }}
                      >
                        -{g.discount}%
                      </span>
                    )}
                  </div>
                </div>
                <ArrowRight size={18} style={{ color: "var(--text-dim)" }} />
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
