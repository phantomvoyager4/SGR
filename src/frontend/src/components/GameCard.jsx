import React from "react";
import { Monitor, Gamepad2, Heart } from "lucide-react";

const tagColor = (tag) => {
  const m = {
    RPG: { bg: "rgba(139,92,246,0.18)", fg: "#C4B5FD" },
    FPS: { bg: "rgba(34,211,238,0.15)", fg: "#67E8F9" },
    INDIE: { bg: "rgba(244,114,182,0.15)", fg: "#F9A8D4" },
    AKCJA: { bg: "rgba(251,146,60,0.15)", fg: "#FDBA74" },
    CRPG: { bg: "rgba(168,85,247,0.18)", fg: "#D8B4FE" },
    SYMULATOR: { bg: "rgba(94,234,212,0.15)", fg: "#5EEAD4" },
  };
  return m[tag] || { bg: "rgba(255,255,255,0.08)", fg: "#CBD5E1" };
};

export function GameCard({ game, onClick }) {
  const t = tagColor(game.tag);
  const finalPrice = game.discount > 0 ? (game.price * (1 - game.discount / 100)).toFixed(2) : game.price.toFixed(2);

  return (
    <div
      data-testid={`game-card-${game.id}`}
      onClick={onClick}
      className="group cursor-pointer rounded-xl overflow-hidden border transition-all duration-300 hover:-translate-y-1"
      style={{ background: "var(--panel)", borderColor: "var(--border)" }}
      onMouseEnter={(e) => (e.currentTarget.style.borderColor = "var(--teal-dim)")}
      onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--border)")}
    >
      <div className="relative aspect-[2/3] overflow-hidden">
        <img
          src={game.cover}
          alt={game.title}
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
          onError={(e) => { e.target.src = `https://placehold.co/600x900/0F1624/5EEAD4?text=${encodeURIComponent(game.title)}`; }}
        />
        <div className="absolute top-2 right-2 px-2 py-1 rounded font-mono text-[10px] font-bold"
             style={{ background: "rgba(5, 8, 15, 0.85)", color: "var(--teal)", border: "1px solid var(--teal-dim)" }}>
          {game.rating.toFixed(1)}/10
        </div>
      </div>
      <div className="p-4">
        <div className="font-display font-bold text-[16px] leading-tight mb-1 truncate">{game.title}</div>
        <div className="text-[12px] mb-3" style={{ color: "var(--text-faint)" }}>
          {game.genre.join(", ")} • {game.studio}
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-baseline gap-2">
            {game.discount > 0 && (
              <span className="font-mono text-[10px] line-through" style={{ color: "var(--text-faint)" }}>
                {game.price.toFixed(2)} zł
              </span>
            )}
            <span className="font-display font-bold text-[15px]">{finalPrice} zł</span>
          </div>
          <div className="flex gap-1.5" style={{ color: "var(--text-dim)" }}>
            {game.platforms.includes("ps5") && <Gamepad2 size={14} />}
            {game.platforms.includes("pc") && <Monitor size={14} />}
          </div>
        </div>
      </div>
    </div>
  );
}

export function FavoriteCard({ game }) {
  const t = tagColor(game.tag);
  return (
    <div
      data-testid={`favorite-${game.id}`}
      className="rounded-xl overflow-hidden border transition-all duration-300 hover:-translate-y-1 cursor-pointer"
      style={{ background: "var(--panel)", borderColor: "var(--border)" }}
    >
      <div className="relative aspect-[4/3] overflow-hidden">
        <img
          src={game.cover}
          alt={game.title}
          className="w-full h-full object-cover"
          onError={(e) => { e.target.src = `https://placehold.co/600x400/0F1624/5EEAD4?text=${encodeURIComponent(game.title)}`; }}
        />
        <button className="absolute top-2 right-2 w-8 h-8 rounded-full grid place-items-center"
                style={{ background: "rgba(5, 8, 15, 0.7)", backdropFilter: "blur(8px)" }}>
          <Heart size={14} fill="var(--teal)" style={{ color: "var(--teal)" }} />
        </button>
      </div>
      <div className="p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2 py-0.5 rounded font-mono text-[9px] uppercase font-bold"
                style={{ background: t.bg, color: t.fg }}>
            {game.tag}
          </span>
          <span className="font-mono text-[11px]" style={{ color: "#FDE047" }}>★ {game.rating.toFixed(1)}</span>
        </div>
        <div className="font-display font-bold text-[17px] mb-2">{game.title}</div>
        <div className="text-[11px] space-y-0.5" style={{ color: "var(--text-faint)" }}>
          <div>Czas gry: {game.hours}h</div>
          <div>Ostatnio grane: {game.recent}</div>
        </div>
      </div>
    </div>
  );
}

export function RecGameCard({ game, match = 95, onMore }) {
  const finalPrice = game.discount > 0 ? (game.price * (1 - game.discount / 100)).toFixed(2) : game.price.toFixed(2);
  return (
    <div
      data-testid={`rec-game-${game.id}`}
      className="rounded-xl overflow-hidden border transition-all duration-300 hover:-translate-y-1 w-full"
      style={{ background: "var(--panel)", borderColor: "var(--border)" }}
    >
      <div className="relative overflow-hidden w-full" style={{ aspectRatio: "460/215" }}>
        <img
          src={game.cover}
          alt={game.title}
          className="w-full h-full object-cover"
          onError={(e) => { e.target.src = `https://placehold.co/460x215/0F1624/5EEAD4?text=${encodeURIComponent(game.title)}`; }}
        />
        <div className="absolute top-3 right-3 px-3 py-1 rounded-full font-mono text-[10px] font-bold uppercase tracking-wider"
             style={{ background: "rgba(5, 8, 15, 0.85)", border: "1px solid var(--teal)", color: "var(--teal)" }}>
          {match}% Match
        </div>
        <div className="absolute bottom-3 left-3 font-display font-black text-[20px] drop-shadow-lg" style={{ textShadow: "0 2px 4px rgba(0,0,0,0.8)" }}>
          {game.title}
        </div>
      </div>
      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div>
            <div className="font-mono text-[9px] uppercase tracking-wider" style={{ color: "var(--text-faint)" }}>
              Najbliższa promocja
            </div>
            <div className="text-[11px] mt-0.5" style={{ color: "var(--text-dim)" }}>30.06.2026</div>
          </div>
          <div className="text-right">
            <div className="font-display font-bold text-[18px]" style={{ color: "var(--purple-2)" }}>
              {finalPrice} PLN
            </div>
            {game.discount > 0 && (
              <div className="font-mono text-[10px]" style={{ color: "var(--teal)" }}>-{game.discount}%</div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1 mb-4 text-[11px]" style={{ color: "var(--text-faint)" }}>
          <span className="font-mono" style={{ color: "#FDE047" }}>★ {game.rating.toFixed(1)}</span>
          <span className="mx-1">·</span>
          <span>Cena regularna: {game.price.toFixed(2)} zł</span>
        </div>
        <button
          data-testid={`rec-more-${game.id}`}
          onClick={onMore}
          className="w-full h-10 rounded-full font-display font-bold text-[13px] tracking-wide transition-all hover:scale-[1.02]"
          style={{ background: "var(--teal)", color: "#04111A" }}
        >
          WIĘCEJ
        </button>
      </div>
    </div>
  );
}

export function SelectableLibraryCard({ game, selected, onToggle }) {
  return (
    <button
      data-testid={`lib-select-${game.id}`}
      onClick={() => onToggle(game.id)}
      className="text-left w-full rounded-xl overflow-hidden border-2 transition-all duration-300"
      style={{
        background: "var(--panel)",
        borderColor: selected ? "var(--teal)" : "var(--border)",
        boxShadow: selected ? "0 0 24px -4px rgba(94, 234, 212, 0.4)" : "none",
      }}
    >
      <div className="relative overflow-hidden w-full" style={{ aspectRatio: "460/215" }}>
        <img
          src={game.cover}
          alt={game.title}
          className="w-full h-full object-cover"
          onError={(e) => { e.target.src = `https://placehold.co/460x215/0F1624/5EEAD4?text=${encodeURIComponent(game.title)}`; }}
        />
        {selected && (
          <div className="absolute inset-0" style={{ background: "rgba(94, 234, 212, 0.1)" }} />
        )}
      </div>
      <div className="p-3">
        <div className="font-display font-bold text-[14px] truncate">{game.title}</div>
        <div className="text-[11px] mt-1" style={{ color: "var(--text-faint)" }}>
          Czas gry: {game.hours}h
        </div>
      </div>
    </button>
  );
}

