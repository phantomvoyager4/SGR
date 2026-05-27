import React, { useState } from "react";
import { NavLink, useNavigate, useLocation } from "react-router-dom";
import {
  LayoutGrid, Compass, Sparkles, BookMarked, Repeat2,
  LifeBuoy, LogOut, Search, Bell, Settings, ChevronRight
} from "lucide-react";
import { USER } from "../data/games";

const NAV = [
  { to: "/", label: "Strona główna", icon: LayoutGrid, testid: "nav-home" },
  { to: "/browse", label: "Przeglądaj gry", icon: Compass, testid: "nav-browse" },
  { to: "/recommender", label: "System rekomendacji", icon: Sparkles, testid: "nav-recommender" },
  { to: "/library", label: "Moja biblioteka", icon: BookMarked, testid: "nav-library" },
  { to: "/steam", label: "Integracja Steam", icon: Repeat2, testid: "nav-steam" },
];

export default function Layout({ children }) {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  const onSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/browse?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <div className="flex min-h-screen" style={{ background: "var(--bg)" }}>
      {/* Sidebar */}
      <aside
        data-testid="sidebar"
        className="w-[260px] flex-shrink-0 flex flex-col justify-between py-6 px-5 border-r"
        style={{ background: "var(--bg-2)", borderColor: "var(--border)" }}
      >
        <div>
          {/* Logo */}
          <div className="mb-10 px-1" data-testid="app-logo" onClick={() => navigate("/")}>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-md grid place-items-center font-display font-black text-[14px] cursor-pointer"
                   style={{ background: "var(--teal)", color: "#04111A" }}>
                SGR
              </div>
              <div>
                <div className="font-display font-bold text-[17px] leading-none">Steam Game Recommender</div>
              </div>
            </div>
          </div>

          {/* Nav */}
          <nav className="flex flex-col gap-1">
            {NAV.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  data-testid={item.testid}
                  className={({ isActive }) =>
                    `group flex items-center gap-3 px-3 py-2.5 rounded-lg text-[14px] transition-all duration-200 ${
                      isActive
                        ? "text-white font-medium"
                        : "text-[color:var(--text-dim)] hover:text-white hover:bg-[color:var(--panel)]"
                    }`
                  }
                  style={({ isActive }) =>
                    isActive
                      ? {
                          background: "linear-gradient(90deg, rgba(139,92,246,0.25), rgba(139,92,246,0.05))",
                          borderLeft: "2px solid var(--purple-2)",
                          paddingLeft: "10px",
                        }
                      : {}
                  }
                >
                  <Icon size={17} strokeWidth={1.8} />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        <div className="flex flex-col gap-1">
          <button
            data-testid="nav-support"
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-[14px] text-[color:var(--text-dim)] hover:text-white hover:bg-[color:var(--panel)] transition-all"
          >
            <LifeBuoy size={17} strokeWidth={1.8} />
            Support
          </button>
          <button
            data-testid="nav-logout"
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-[14px] text-[color:var(--text-dim)] hover:text-white hover:bg-[color:var(--panel)] transition-all"
          >
            <LogOut size={17} strokeWidth={1.8} />
            Wyloguj
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Topbar */}
        <header
          data-testid="topbar"
          className="h-20 flex items-center justify-between gap-6 px-8 border-b flex-shrink-0"
          style={{ background: "var(--bg)", borderColor: "var(--border)" }}
        >
          <form onSubmit={onSearch} className="flex-1 max-w-[640px]">
            <div className="flex items-center gap-3 h-11 px-5 rounded-full border transition-colors"
                 style={{ background: "var(--panel)", borderColor: "var(--border)" }}>
              <Search size={16} style={{ color: "var(--text-faint)" }} />
              <input
                data-testid="search-input"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                type="text"
                placeholder="Wyszukaj gry..."
                className="bg-transparent border-none outline-none flex-1 text-[14px] placeholder:text-[color:var(--text-faint)]"
              />
            </div>
          </form>

          <div className="flex items-center gap-3">
            <div
              data-testid="steam-status"
              className="flex items-center gap-2 px-4 h-10 rounded-full border font-mono text-[11px] uppercase tracking-wider"
              style={{ background: "rgba(94, 234, 212, 0.06)", borderColor: "var(--teal-dim)", color: "var(--teal)" }}
            >
              <span className="w-2 h-2 rounded-full pulse-dot" style={{ background: "var(--teal)" }} />
              Steam Połączony
            </div>
            <button
              data-testid="notifications-btn"
              className="w-10 h-10 rounded-full grid place-items-center border hover:border-[color:var(--border-hover)] transition-colors"
              style={{ background: "var(--panel)", borderColor: "var(--border)" }}
            >
              <Bell size={16} style={{ color: "var(--text-dim)" }} />
            </button>
            <button
              data-testid="settings-btn"
              className="w-10 h-10 rounded-full grid place-items-center border hover:border-[color:var(--border-hover)] transition-colors"
              style={{ background: "var(--panel)", borderColor: "var(--border)" }}
            >
              <Settings size={16} style={{ color: "var(--text-dim)" }} />
            </button>
            <button data-testid="avatar-btn" className="w-10 h-10 rounded-full overflow-hidden border-2"
                    style={{ borderColor: "var(--teal)" }}>
              <img src={USER.avatar} alt="avatar" className="w-full h-full object-cover" />
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto px-8 py-8">{children}</main>
      </div>
    </div>
  );
}

export { ChevronRight };


