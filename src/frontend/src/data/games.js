// Mock game data. Cover images use Steam CDN (publicly accessible library covers).
const cover = (id) => `https://cdn.cloudflare.steamstatic.com/steam/apps/${id}/library_600x900_2x.jpg`;
const header = (id) => `https://cdn.cloudflare.steamstatic.com/steam/apps/${id}/library_hero.jpg`;

export const GAMES = [
  { id: "1245620", title: "Elden Ring", genre: ["Action RPG"], studio: "FromSoftware", rating: 9.5, price: 299.9, discount: 0, platforms: ["pc", "ps5", "xbox"], cover: cover(1245620), hero: header(1245620), hours: 82, recent: "2 dni temu", tag: "RPG" },
  { id: "3611400", title: "Bloodborne", genre: ["Action RPG"], studio: "FromSoftware", rating: 9.2, price: 159.9, discount: 20, platforms: ["ps5"], cover: "https://image.api.playstation.com/cdn/UP9000/CUSA00207_00/0T6yOF9Nr29vRrFJjmc8h7OyKS0j2R0u.png", hours: 45, recent: "1 tydzień temu", tag: "RPG" },
  { id: "292030", title: "Wiedźmin 3", genre: ["RPG"], studio: "CD Projekt Red", rating: 8.9, price: 89.9, discount: 50, platforms: ["pc", "ps5", "xbox", "steamdeck"], cover: cover(292030), hero: header(292030), hours: 150, recent: "wczoraj", tag: "RPG" },
  { id: "1091500", title: "Cyberpunk 2077", genre: ["Action RPG"], studio: "CD Projekt Red", rating: 8.4, price: 199.9, discount: 40, platforms: ["pc", "ps5", "xbox"], cover: cover(1091500), hero: header(1091500), hours: 92, recent: "dziś", tag: "AKCJA" },
  { id: "374320", title: "Dark Souls III", genre: ["Action RPG"], studio: "FromSoftware", rating: 9.2, price: 169.5, discount: 30, platforms: ["pc", "ps5", "xbox"], cover: cover(374320), hero: header(374320), hours: 68, recent: "tydzień temu", tag: "RPG" },
  { id: "1086940", title: "Baldur's Gate 3", genre: ["CRPG"], studio: "Larian Studios", rating: 9.7, price: 249.5, discount: 10, platforms: ["pc", "ps5"], cover: cover(1086940), hero: header(1086940), hours: 120, recent: "3 dni temu", tag: "CRPG" },
  { id: "1174180", title: "Red Dead Redemption 2", genre: ["Akcja", "Przygoda"], studio: "Rockstar", rating: 9.3, price: 219.0, discount: 60, platforms: ["pc", "ps5", "xbox"], cover: cover(1174180), hero: header(1174180), hours: 362, recent: "wczoraj", tag: "AKCJA" },
  { id: "782330", title: "Doom Eternal", genre: ["FPS", "Akcja"], studio: "id Software", rating: 9.0, price: 99.9, discount: 70, platforms: ["pc", "ps5", "xbox"], cover: cover(782330), hero: header(782330), hours: 40, recent: "miesiąc temu", tag: "FPS" },
  { id: "1145360", title: "Hades", genre: ["Roguelike", "RPG"], studio: "Supergiant", rating: 9.1, price: 89.0, discount: 45, platforms: ["pc", "ps5", "xbox", "steamdeck"], cover: cover(1145360), hero: header(1145360), hours: 48, recent: "2 dni temu", tag: "INDIE" },
  { id: "1222670", title: "The Sims 4", genre: ["Symulator"], studio: "Maxis", rating: 7.5, price: 149.0, discount: 50, platforms: ["pc"], cover: cover(1222670), hero: header(1222670), hours: 1240, recent: "2 tygodnie temu", tag: "SYMULATOR" },
  { id: "2668510", title: "Red Dead Redemption", genre: ["Akcja", "Przygoda"], studio: "Rockstar", rating: 8.8, price: 69.0, discount: 30, platforms: ["pc", "ps5"], cover: cover(2668510), hero: header(2668510), hours: 50, recent: "niedawno", tag: "AKCJA" },
  { id: "3020", title: "Call of Juarez: Gunslinger", genre: ["FPS"], studio: "Techland", rating: 8.0, price: 8.99, discount: 80, platforms: ["pc"], cover: cover(204450), hero: header(204450), hours: 12, recent: "miesiąc temu", tag: "FPS" },
  { id: "3489700", title: "Stellar Blade", genre: ["Akcja"], studio: "Shift Up", rating: 8.7, price: 279.0, discount: 0, platforms: ["pc", "ps5"], cover: cover(3489700), hours: 0, recent: "—", tag: "AKCJA" },
  { id: "367520", title: "Hollow Knight", genre: ["Metroidvania", "Indie"], studio: "Team Cherry", rating: 9.4, price: 45.0, discount: 55, platforms: ["pc", "ps5", "xbox", "steamdeck"], cover: cover(367520), hero: header(367520), hours: 55, recent: "miesiąc temu", tag: "INDIE" },
  { id: "1627720", title: "Lies of P", genre: ["Action RPG"], studio: "Neowiz", rating: 8.8, price: 229.0, discount: 25, platforms: ["pc", "ps5", "xbox"], cover: cover(1627720), hero: header(1627720), hours: 0, recent: "—", tag: "RPG" },
];

export const GENRES = ["RPG", "FPS", "Indie", "Akcja", "Symulator", "Roguelike"];

export const PLATFORMS = [
  { id: "pc", label: "Windows PC" },
  { id: "ps5", label: "PlayStation 5" },
  { id: "xbox", label: "Xbox Series X" },
  { id: "steamdeck", label: "Steam Deck" },
];

export const USER = {
  username: "zzzosia",
  avatar: "https://static.wikia.nocookie.net/clair-obscur/images/9/91/COE33_char_icon_Lune.png/revision/latest?cb=20250506001951",
  steamConnected: true,
  lastActive: "2 godziny temu",
  totalHours: 12420,
  favoriteGenre: "Action RPG",
  recommendationsCount: 154,
  libraryCount: 124,
  weekHours: 23,
  weekGenreHours: 12,
  newRecommendations: 8,
  favorites: ["rdr2", "sims-4", "witcher-3"],
  activity: [
    { id: 1, type: "teal", text: "Zaimportowano dane z konta Steam", time: "teraz" },
    { id: 2, type: "purple", text: "Dodano Kingdom Come: Deliverance 2 do ulubionych", time: "3 godziny temu" },
    { id: 3, type: "yellow", text: "Zdobyto osiągnięcie: Nowy użytkownik", time: "wczoraj" },
  ],
};


