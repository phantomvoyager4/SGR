import React from "react";
import { useNavigate } from "react-router-dom";
import { Clock, Gamepad2, Sparkles, TrendingUp } from "lucide-react";
import { GAMES, USER } from "../data/games";
import { FavoriteCard } from "../components/GameCard";

const StatCard = ({ icon: Icon, label, value, suffix, delta, color = "var(--teal)", testid }) => (
  <div
    data-testid={testid}
    className="rounded-2xl border p-6 transition-all hover:-translate-y-1"
    style={{ background: "var(--panel)", borderColor: "var(--border)" }}
  >
    <div className="flex items-start justify-between mb-5">
      <div className="w-10 h-10 rounded-lg grid place-items-center"
           style={{ background: `${color.replace("var(--", "rgba(").replace(")", ", 0.15)")}`, border: `1px solid ${color}` }}>
        <Icon size={18} style={{ color }} />
      </div>
      {delta && (
        <span className="font-mono text-[10px] uppercase tracking-wider font-bold" style={{ color }}>
          {delta}
        </span>
      )}
    </div>
    <div className="font-mono text-[10px] uppercase tracking-[0.15em] mb-2" style={{ color: "var(--text-faint)" }}>
      {label}
    </div>
    <div className="flex items-baseline gap-2">
      <span className="font-display font-black text-[32px] leading-none">{value}</span>
      {suffix && <span className="text-[13px]" style={{ color: "var(--text-dim)" }}>{suffix}</span>}
    </div>
  </div>
);

export default function Library() {
  const navigate = useNavigate();
  const favorites = USER.favorites.map((id) => GAMES.find((g) => g.id === id)).filter(Boolean);

  const dotColor = (t) => ({ teal: "var(--teal)", purple: "var(--purple-2)", yellow: "#FDE047" })[t] || "var(--teal)";

  return (
    <div className="max-w-[1400px] mx-auto fade-up">
      {/* Profile card */}
      <section
        data-testid="profile-card"
        className="rounded-2xl border p-6 flex items-center gap-6 mb-8 relative overflow-hidden"
        style={{
          background: "linear-gradient(135deg, rgba(13, 148, 136, 0.08), rgba(139, 92, 246, 0.06))",
          borderColor: "var(--teal-dim)",
        }}
      >
        <div className="w-[120px] h-[120px] rounded-xl overflow-hidden border-2 flex-shrink-0"
             style={{ borderColor: "var(--teal)" }}>
          <img src={USER.avatar} alt="avatar" className="w-full h-full object-cover" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <span className="px-3 py-0.5 rounded-full font-mono text-[10px] uppercase tracking-wider font-bold"
                  style={{ background: "rgba(94,234,212,0.15)", color: "var(--teal)", border: "1px solid var(--teal-dim)" }}>
              Połączony
            </span>
            <span className="font-mono text-[11px] uppercase tracking-wider" style={{ color: "var(--text-dim)" }}>
              Konto Steam
            </span>
          </div>
          <h1 className="font-display font-black text-[40px] leading-none mb-2">{USER.username}</h1>
          <div className="flex items-center gap-2 text-[13px]" style={{ color: "var(--text-dim)" }}>
            <span className="w-2 h-2 rounded-full pulse-dot" style={{ background: "var(--teal)" }} />
            Ostatnio aktywny: {USER.lastActive}
          </div>
        </div>
        <button
          data-testid="library-games-btn"
          onClick={() => navigate("/browse")}
          className="h-12 px-7 rounded-full font-display font-bold text-[14px] transition-all hover:scale-105"
          style={{ background: "var(--teal)", color: "#04111A" }}
        >
          Biblioteka gier
        </button>
      </section>

      {/* Stats */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
        <StatCard icon={Clock} testid="stat-hours" label="Czas gry" value={USER.totalHours.toLocaleString("pl-PL")}
                  suffix="h" delta={`+${USER.weekHours}h w tym tygodniu`} color="var(--teal)" />
        <StatCard icon={Gamepad2} testid="stat-genre" label="Ulubiony Gatunek" value={USER.favoriteGenre}
                  delta={`${USER.weekGenreHours}h w tym tygodniu`} color="var(--purple-2)" />
        <StatCard icon={Sparkles} testid="stat-recs" label="Rekomendacje" value={USER.recommendationsCount}
                  suffix="wygenerowanych sesji" delta={`+${USER.newRecommendations} nowych`} color="#FDE047" />
      </section>

      {/* Favorites + Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-8">
        <section data-testid="favorites-section">
          <div className="flex items-end justify-between mb-6">
            <div>
              <h2 className="font-display font-black text-[32px] leading-none mb-1">Ulubione</h2>
              <p className="text-[13px]" style={{ color: "var(--text-dim)" }}>
                Szybki dostęp do Twoich ulubionych gier
              </p>
            </div>
            <button
              data-testid="see-all-favorites"
              onClick={() => navigate("/browse")}
              className="text-[13px] font-medium hover:underline"
              style={{ color: "var(--teal)" }}
            >
              Zobacz wszystkie →
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {favorites.map((g, i) => (
              <div key={g.id} className="fade-up" style={{ animationDelay: `${i * 80}ms` }}>
                <FavoriteCard game={g} />
              </div>
            ))}
          </div>
        </section>

        <aside
          data-testid="activity-panel"
          className="rounded-2xl border p-6"
          style={{ background: "var(--panel)", borderColor: "var(--border)" }}
        >
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp size={16} style={{ color: "var(--teal)" }} />
            <h3 className="font-display font-bold text-[15px] uppercase tracking-wider">
              Ostatnia Aktywność
            </h3>
          </div>
          <div className="flex flex-col gap-5 mb-6">
            {USER.activity.map((a) => (
              <div key={a.id} className="flex gap-3">
                <div className="w-1.5 rounded-full flex-shrink-0 mt-1"
                     style={{ background: dotColor(a.type) }} />
                <div className="flex-1">
                  <div className="text-[13px] leading-snug mb-1">{a.text}</div>
                  <div className="font-mono text-[10px]" style={{ color: "var(--text-faint)" }}>
                    {a.time}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <button
            data-testid="history-btn"
            className="w-full h-10 rounded-full font-display font-semibold text-[12px] border transition-colors hover:border-[color:var(--teal-dim)]"
            style={{ borderColor: "var(--border-hover)", color: "white", background: "transparent" }}
          >
            Historia
          </button>
        </aside>
      </div>
    </div>
  );
}


