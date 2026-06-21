import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

export default function GameDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [details, setDetails] = useState(null);
  const [priceHistory, setPriceHistory] = useState(null);
  const [predictions, setPredictions] = useState(null); 
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const detailsRes = await fetch(`http://localhost:8000/game/${id}`);
        const detailsData = await detailsRes.json();
        setDetails(Object.keys(detailsData).length > 0 ? detailsData : null);

        const priceRes = await fetch(`http://localhost:8000/game/${id}/price-history`);
        const priceData = await priceRes.json();
        setPriceHistory(priceData);

        const predictionsRes = await fetch(`http://localhost:8000/game/${id}/price-predictions?days=30`);
        if (predictionsRes.ok) {
          const predictionsData = await predictionsRes.json();
          setPredictions(Object.keys(predictionsData).length > 0 ? predictionsData : null);
        }
      } catch (err) {
        console.error("Błąd pobierania danych:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-[1100px] mx-auto text-center p-12 text-[color:var(--text-dim)]">
        Ładowanie szczegółów gry...
      </div>
    );
  }

  if (!details) {
    return (
      <div className="max-w-[900px] mx-auto">
        <button onClick={() => navigate(-1)} className="mb-4">← Powrót</button>
        <div className="rounded-2xl border p-8 text-center" style={{ background: "var(--panel)", borderColor: "var(--border)" }}>
          Gra nie znaleziona na serwerze.
        </div>
      </div>
    );
  }

  const isFree = details.is_free;
  const priceOverview = details.price_overview;
  const discount = priceOverview?.discount_percent || 0;
  const currentPrice = isFree ? 0 : (priceOverview ? priceOverview.final / 100 : null);
  const initialPrice = priceOverview ? priceOverview.initial / 100 : null;

  const genres = details.genres ? details.genres.map((g) => g.description).join(", ") : "Brak danych";
  const studio = details.developers ? details.developers.join(", ") : "Nieznany";
  const categories = details.categories ? details.categories.map((c) => c.description) : [];

  return (
    <div className="max-w-[1100px] mx-auto fade-up">
      <button onClick={() => navigate(-1)} className="mb-6">← Powrót</button>

      <div className="rounded-2xl overflow-hidden border" style={{ background: "var(--panel)", borderColor: "var(--border)" }}>
        <div className="relative w-full flex justify-center items-center overflow-hidden" style={{ aspectRatio: "3/1" }}>
          <img src={details.header_image} alt={details.name} className="w-full h-full object-cover blur-sm opacity-50 absolute top-0 left-0" />
          <img src={details.header_image} alt={details.name} className="h-full w-auto relative z-10 object-contain mx-auto" />
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 flex flex-col justify-center">
            <div className="flex items-start gap-6 w-full">
              <div className="w-full text-center md:text-left">
                <h1 className="font-display font-black text-[34px] mb-2">{details.name}</h1>
                <div className="flex items-center justify-center md:justify-start gap-3 mb-4">
                  <div className="text-[13px]" style={{ color: "var(--text-faint)" }}>
                    {genres} • {studio}
                  </div>
                </div>

                <div>
                  <div className="text-[13px] mb-2 font-mono uppercase tracking-wider" style={{ color: "var(--text-faint)" }}>Cechy / Kategorie</div>
                  <div className="flex gap-2 text-[12px] flex-wrap justify-center md:justify-start" style={{ color: "var(--text-dim)" }}>
                    {categories.map((c) => (
                      <div key={c} className="px-3 py-1 rounded-full border" style={{ borderColor: "var(--border)" }}>{c}</div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <aside className="md:col-span-1 p-4 border-t md:border-t-0 md:border-l flex flex-col justify-center text-center md:text-left" style={{ borderColor: "var(--border)" }}>
            <div className="mb-4">
              {discount > 0 && (
                <div className="font-mono text-[12px] line-through" style={{ color: "var(--text-faint)" }}>
                  {initialPrice?.toFixed(2)} zł
                </div>
              )}
              <div className="font-display font-bold text-[24px]" style={{ color: "var(--purple-2)" }}>
                {isFree ? "Za darmo" : currentPrice !== null ? `${currentPrice.toFixed(2)} zł` : "Brak ceny"}
              </div>
              {discount > 0 && <div className="font-mono text-[12px]" style={{ color: "var(--teal)" }}>-{discount}%</div>}
            </div>

            <button className="w-full h-12 rounded-full font-bold transition-transform hover:scale-[1.02]" style={{ background: "var(--teal)", color: "#04111A" }}>
              Zagraj / Kup
            </button>

            <div className="mt-4 text-[13px]" style={{ color: "var(--text-faint)" }}>
              <div>Wydawca: {details.publishers ? details.publishers.join(", ") : "Nieznany"}</div>
            </div>
          </aside>
        </div>
      </div>

      <div className="mt-8 rounded-2xl overflow-hidden border p-8 text-center" style={{ background: "var(--panel)", borderColor: "var(--border)" }}>
        <div className="mb-6">
          <h2 className="font-display font-black text-[28px] mt-3" style={{ color: "var(--text-bright)" }}>
            Opis gry
          </h2>
          <div className="w-12 h-[2px] mx-auto mt-2 rounded-full" style={{ background: "var(--teal)" }}></div>
        </div>

        <div 
          className="mt-2 text-[15px] leading-relaxed max-w-[800px] mx-auto flex flex-col items-center justify-center [&_img]:mx-auto [&_img]:my-4 [&_img]:rounded-lg" 
          style={{ color: "var(--text-dim)" }}
          dangerouslySetInnerHTML={{ __html: details.about_the_game }}
        />
      </div>

      <div className="mt-8 rounded-2xl overflow-hidden border p-8" style={{ background: "var(--panel)", borderColor: "var(--border)" }}>
        <div className="mb-6 text-center">
          <h2 className="font-display font-black text-[28px] mt-3" style={{ color: "var(--text-bright)" }}>
            Nasze przewidywania ceny
          </h2>
          <div className="w-12 h-[2px] mx-auto mt-2 rounded-full" style={{ background: "var(--teal)" }}></div>
        </div>

        <div className="max-w-[800px] mx-auto mt-6 text-[15px]" style={{ color: "var(--text-dim)" }}>
          {predictions ? (
            <div>
              <div className="mb-4 text-center text-[14px]" style={{ color: "var(--text-faint)" }}>
                Sugerowana cena bazowa wykryta przez model: <span className="font-bold" style={{ color: "var(--text-bright)" }}>{predictions.current_price.toFixed(2)} zł</span>
              </div>
              
              <div className="overflow-x-auto rounded-xl border" style={{ borderColor: "var(--border)" }}>
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr style={{ background: "rgba(255,255,255,0.03)" }}>
                      <th className="p-3 font-mono text-[13px] uppercase tracking-wider" style={{ color: "var(--text-faint)" }}>Data</th>
                      <th className="p-3 font-mono text-[13px] uppercase tracking-wider" style={{ color: "var(--text-faint)" }}>Przewidywana Cena</th>
                      <th className="p-3 font-mono text-[13px] uppercase tracking-wider text-right" style={{ color: "var(--text-faint)" }}>Spodziewana obniżka</th>
                    </tr>
                  </thead>
                  <tbody>
                    {predictions.dates.map((date, index) => {
                      const price = predictions.prices[index];
                      const discountPercent = predictions.discounts[index];
                      
                      return (
                        <tr key={date} className="border-t transition-colors hover:bg-[rgba(255,255,255,0.01)]" style={{ borderColor: "var(--border)" }}>
                          <td className="p-3 font-mono text-[14px]">{date}</td>
                          <td className="p-3 font-bold" style={{ color: discountPercent > 0 ? "var(--purple-2)" : "var(--text-bright)" }}>
                            {price.toFixed(2)} zł
                          </td>
                          <td className="p-3 text-right font-mono font-bold" style={{ color: discountPercent > 0 ? "var(--teal)" : "var(--text-faint)" }}>
                            {discountPercent > 0 ? `-${discountPercent}%` : "Brak obniżki"}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="text-center p-6 text-[color:var(--text-faint)]">
              Niestety nasz model nie posiada wystarczającej ilości danych, aby wygenerować prognozę ceny dla tej gry.
            </div>
          )}
        </div>
      </div>
      
    </div>
  );
}