import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { GAMES } from "../data/games";

export default function GameDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const game = GAMES.find((g) => g.id === id);
  const [details, setDetails] = useState(null);
  const [priceHistory, setPriceHistory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const detailsRes = await fetch(`http://localhost:8000/game/${id}`);
        const detailsData = await detailsRes.json();
        setDetails(detailsData);

        const priceRes = await fetch(`http://localhost:8000/game/${id}/price-history`);
        const priceData = await priceRes.json();
        setPriceHistory(priceData);
      } catch (err) {
        console.error("Failed to fetch game details:", err);
      } finally {
        setLoading(false);
      }
    };

    if (game) {
      fetchData();
    }
  }, [id, game]);

  if (!game) {
    return (
      <div className="max-w-[900px] mx-auto">
        <button onClick={() => navigate(-1)} className="mb-4">← Powrót</button>
        <div className="rounded-2xl border p-8" style={{ background: "var(--panel)", borderColor: "var(--border)" }}>
          Gra nie znaleziona.
        </div>
      </div>
    );
  }

  const finalPrice = game.discount > 0 ? (game.price * (1 - game.discount / 100)).toFixed(2) : game.price.toFixed(2);

  return (
    <div className="max-w-[1100px] mx-auto fade-up">
      <button onClick={() => navigate(-1)} className="mb-6">← Powrót</button>

      <div className="rounded-2xl overflow-hidden border" style={{ background: "var(--panel)", borderColor: "var(--border)" }}>
        <div className="relative w-full" style={{ aspectRatio: "3/1" }}>
          <img src={game.hero || game.cover} alt={game.title} className="w-full h-full object-cover" onError={(e)=>{e.target.src=game.cover}} />
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <div className="flex items-start gap-6">
              <img src={game.cover} alt={game.title} className="w-40 h-60 object-cover rounded-lg shadow" />
              <div>
                <h1 className="font-display font-black text-[34px] mb-2">{game.title}</h1>
                <div className="flex items-center gap-3 mb-3">
                  <div className="font-mono text-[13px]" style={{ color: "#FDE047" }}>★ {game.rating.toFixed(1)}</div>
                  <div className="text-[13px]" style={{ color: "var(--text-faint)" }}>{game.genre.join(", ")} • {game.studio}</div>
                </div>

                <div className="mb-4 text-[14px]" style={{ color: "var(--text-dim)" }}>
                  Czas gry: {game.hours}h • Ostatnio: {game.recent}
                </div>

                <div className="mb-4">
                  <div className="text-[13px] mb-2 font-mono" style={{ color: "var(--text-faint)" }}>Platformy</div>
                  <div className="flex gap-2 text-[13px]" style={{ color: "var(--text-dim)" }}>
                    {game.platforms.map((p) => (
                      <div key={p} className="px-3 py-1 rounded-full border" style={{ borderColor: "var(--border)" }}>{p}</div>
                    ))}
                  </div>
                </div>

                <div className="mb-6">
                  <div className="font-mono text-[12px]" style={{ color: "var(--text-faint)" }}>Opis</div>
                  <p className="mt-2 text-[14px]" style={{ color: "var(--text-dim)" }}>
                    {loading ? "Ładowanie..." : details?.about_the_game || "Brak dostępnego opisu gry."}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <aside className="md:col-span-1 p-4 border-l" style={{ borderColor: "var(--border)" }}>
            <div className="mb-4">
              {game.discount > 0 && (
                <div className="font-mono text-[12px] line-through" style={{ color: "var(--text-faint)" }}>{game.price.toFixed(2)} zł</div>
              )}
              <div className="font-display font-bold text-[24px]" style={{ color: "var(--purple-2)" }}>{finalPrice} zł</div>
              {game.discount > 0 && <div className="font-mono text-[12px]" style={{ color: "var(--teal)" }}>-{game.discount}%</div>}
            </div>

            <button className="w-full h-12 rounded-full font-bold" style={{ background: "var(--teal)", color: "#04111A" }}>Kup teraz</button>

            <div className="mt-6 text-[13px]" style={{ color: "var(--text-faint)" }}>
              <div>Tag: {game.tag}</div>
              <div className="mt-2">Studio: {game.studio}</div>
            </div>
          </aside>
        </div>
      </div>

      {priceHistory && priceHistory.dates.length > 0 && (
        <div className="mt-8 rounded-2xl overflow-hidden border p-6" style={{ background: "var(--panel)", borderColor: "var(--border)" }}>
          <h2 className="font-display font-bold text-[24px] mb-6">Historia cen</h2>
          <div className="w-full h-80 bg-gradient-to-b from-[rgba(139,92,246,0.1)] to-transparent rounded-lg p-4 flex items-end justify-start gap-1 overflow-x-auto">
            {priceHistory.prices.map((price, idx) => {
              const minPrice = Math.min(...priceHistory.prices);
              const maxPrice = Math.max(...priceHistory.prices);
              const range = maxPrice - minPrice || 1;
              const height = ((price - minPrice) / range) * 100;
              return (
                <div
                  key={idx}
                  className="flex-1 min-w-[3px] rounded-t-sm transition-all hover:bg-teal-500"
                  style={{
                    height: `${Math.max(height, 5)}%`,
                    background: "var(--teal)",
                    opacity: 0.7,
                  }}
                  title={`${priceHistory.dates[idx]}: ${price} zł`}
                />
              );
            })}
          </div>
          <div className="mt-4 flex items-center justify-between text-[12px]" style={{ color: "var(--text-faint)" }}>
            <span>{priceHistory.dates[0]}</span>
            <span>Min: {Math.min(...priceHistory.prices).toFixed(2)} zł • Max: {Math.max(...priceHistory.prices).toFixed(2)} zł</span>
            <span>{priceHistory.dates[priceHistory.dates.length - 1]}</span>
          </div>
        </div>
      )}
    </div>
  );
}
