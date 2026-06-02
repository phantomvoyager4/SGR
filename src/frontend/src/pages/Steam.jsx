import React, { useState } from "react";
import { CheckCircle2, RefreshCw, Download, Unlink } from "lucide-react";
import { USER } from "../data/games";

export default function Steam() {
  const [syncing, setSyncing] = useState(false);
  const [lastSync, setLastSync] = useState("przed chwilą");

  const handleSync = () => {
    setSyncing(true);
    setTimeout(() => {
      setSyncing(false);
      setLastSync("teraz");
    }, 1600);
  };

  return (
    <div className="max-w-[1000px] mx-auto fade-up">
      <h1 className="font-display font-black text-[44px] leading-none mb-3">
        Integracja Steam
      </h1>
      <p className="text-[15px] mb-10" style={{ color: "var(--text-dim)" }}>
        Połącz swoje konto Steam, aby importować bibliotekę i otrzymywać
        spersonalizowane rekomendacje.
      </p>

      <div
        data-testid="steam-status-card"
        className="rounded-2xl border p-8 mb-6 relative overflow-hidden"
        style={{
          background:
            "linear-gradient(135deg, rgba(13, 148, 136, 0.12), rgba(5, 8, 15, 0.5))",
          borderColor: "var(--teal-dim)",
        }}
      >
        <div className="flex items-start gap-5 mb-6">
          <div
            className="w-14 h-14 rounded-full grid place-items-center glow-teal"
            style={{
              background: "rgba(94, 234, 212, 0.15)",
              border: "1px solid var(--teal)",
            }}
          >
            <CheckCircle2 size={24} style={{ color: "var(--teal)" }} />
          </div>
          <div className="flex-1">
            <div className="font-display font-bold text-[24px] mb-1">
              Konto Steam połączone
            </div>
            <div className="text-[13px]" style={{ color: "var(--text-dim)" }}>
              Zalogowano jako{" "}
              <span style={{ color: "var(--teal)" }}>{USER.username}</span> ·
              Ostatnia synchronizacja: {lastSync}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          {[
            { label: "Gry w bibliotece", value: USER.libraryCount },
            {
              label: "Łączny czas gry",
              value: `${USER.totalHours.toLocaleString("pl-PL")}h`,
            },
            { label: "Osiągnięcia", value: 782 },
          ].map((s, i) => (
            <div
              key={i}
              className="p-4 rounded-xl border"
              style={{
                background: "rgba(5, 8, 15, 0.4)",
                borderColor: "var(--border)",
              }}
            >
              <div
                className="font-mono text-[10px] uppercase tracking-wider mb-1"
                style={{ color: "var(--text-faint)" }}
              >
                {s.label}
              </div>
              <div className="font-display font-black text-[22px]">
                {s.value}
              </div>
            </div>
          ))}
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            data-testid="sync-steam-btn"
            onClick={handleSync}
            disabled={syncing}
            className="flex items-center gap-2 h-11 px-6 rounded-full font-display font-bold text-[13px] transition-all hover:scale-105 disabled:opacity-60"
            style={{ background: "var(--teal)", color: "#04111A" }}
          >
            <RefreshCw size={14} className={syncing ? "animate-spin" : ""} />
            {syncing ? "Synchronizacja..." : "Synchronizuj teraz"}
          </button>
          <button
            data-testid="import-btn"
            className="flex items-center gap-2 h-11 px-6 rounded-full font-display font-bold text-[13px] border transition-colors hover:border-[color:var(--teal-dim)]"
            style={{ borderColor: "var(--border-hover)", color: "white" }}
          >
            <Download size={14} /> Importuj ponownie
          </button>
          <button
            data-testid="disconnect-btn"
            className="flex items-center gap-2 h-11 px-6 rounded-full font-display font-semibold text-[13px] border transition-colors"
            style={{ borderColor: "var(--border)", color: "var(--text-dim)" }}
          >
            <Unlink size={14} /> Rozłącz konto
          </button>
        </div>
      </div>

      <div
        className="rounded-2xl border p-6"
        style={{ background: "var(--panel)", borderColor: "var(--border)" }}
      >
        <h3 className="font-display font-bold text-[18px] mb-4">
          Ustawienia synchronizacji
        </h3>
        <div className="space-y-4">
          {[
            {
              label: "Automatyczna synchronizacja biblioteki",
              desc: "Co 24 godziny",
              on: true,
            },
            {
              label: "Importuj czas gry",
              desc: "Aktualizowany w czasie rzeczywistym",
              on: true,
            },
            {
              label: "Udostępniaj osiągnięcia",
              desc: "Publiczny profil dla rekomendacji",
              on: false,
            },
          ].map((opt, i) => {
            const [on, setOn] = [opt.on, () => {}];
            return <ToggleRow key={i} {...opt} testid={`toggle-${i}`} />;
          })}
        </div>
      </div>
    </div>
  );
}

function ToggleRow({ label, desc, on: initialOn, testid }) {
  const [on, setOn] = useState(initialOn);
  return (
    <div
      className="flex items-center justify-between py-3 border-b last:border-0"
      style={{ borderColor: "var(--border)" }}
    >
      <div>
        <div className="font-display font-semibold text-[14px]">{label}</div>
        <div className="text-[12px]" style={{ color: "var(--text-faint)" }}>
          {desc}
        </div>
      </div>
      <button
        data-testid={testid}
        onClick={() => setOn(!on)}
        className="w-11 h-6 rounded-full relative transition-colors"
        style={{ background: on ? "var(--teal)" : "var(--panel-3)" }}
      >
        <span
          className="absolute top-0.5 w-5 h-5 rounded-full transition-all"
          style={{
            left: on ? "22px" : "2px",
            background: on ? "#04111A" : "var(--text-dim)",
          }}
        />
      </button>
    </div>
  );
}
