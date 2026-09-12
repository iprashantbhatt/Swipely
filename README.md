# 📰 Swipely — Swipe News

<div align="center">

**A Tinder-style, swipeable news reader with a glassmorphic UI.**

[![Made with HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![Made with CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![Made with JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

---

## ✨ Overview

**Swipely** turns your daily news feed into a swipeable card stack — swipe **left** to skip a story, swipe **right** to save it for later. No frameworks, no build step: a single self-contained `index.html` powers the entire experience, backed by a lightweight news API.

Built with an Apple-inspired **Liquid Glass** aesthetic — frosted blurs, soft gradients, and five switchable themes — Swipely feels less like a news app and more like flipping through a deck of cards.

---

## 🎬 Preview

> _Add a screenshot or screen recording here — e.g. `docs/preview.gif`_

```
┌──────────────────────────┐
│  📰 Swipely      🔴 LIVE  │
├──────────────────────────┤
│  🔴 BREAKING: ticker...   │
├──────────────────────────┤
│  All 🌍 🇮🇳 💻 📈 🔬 ⚽ 🎬 🏥 │
├──────────────────────────┤
│                          │
│      ╭──────────────╮    │
│      │   [image]    │    │
│      │  headline    │    │
│      │  description │    │
│      ╰──────────────╯    │
│                          │
├──────────────────────────┤
│  ✨ For You  🔥  🔖  🔍   │
└──────────────────────────┘
```

---

## 🚀 Features

- **Swipeable card stack** — natural touch/mouse drag physics, with rotation and directional hints (👎 skip / ❤️ save)
- **Keyboard support** — navigate the stack with ← / → arrow keys
- **Live ticker** — scrolling breaking-news headlines pulled from the API
- **Category filters** — World, India, Tech, Business, Science, Sports, Culture, Health
- **Four views** — ✨ For You (swipe feed), 🔥 Trending, 🔖 Saved, 🔍 Search
- **5 glassmorphic themes** — Aurora, Dusk Rose, Arctic, Ember, Obsidian — switchable on the fly
- **Graceful offline fallback** — shows a placeholder card if the backend is unreachable
- **Zero dependencies** — pure HTML/CSS/JS, no build tooling required
- **Auto-refresh** — feed and ticker refresh hourly in the background

---

## 🛠️ Tech Stack

| Layer      | Tech                                            |
|------------|--------------------------------------------------|
| Frontend   | Vanilla HTML5, CSS3 (custom properties, backdrop-filter), JavaScript (ES6+) |
| Backend    | REST API — `/api/news`, `/api/breaking` _(adjust to match your actual backend)_ |
| Styling    | CSS custom properties for theming, `backdrop-filter` glassmorphism |
| Hosting    | Self-hosted / static hosting + reverse proxy (Nginx) |

---

## 📁 Project Structure

```
Swipely/
├── frontend/
│   └── index.html      # Entire app: markup, styles, and logic
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites
- A running backend that exposes:
  - `GET /api/news?category=<cat>&limit=<n>` → `{ articles: [...] }`
  - `GET /api/breaking` → `{ items: [...] }`
- Any static file server (or just open the file directly for local testing)

### Run locally

```bash
git clone https://github.com/iprashantbhatt/Swipely.git
cd Swipely/frontend

# Option A: open directly
open index.html

# Option B: serve it (recommended, avoids CORS/file:// issues)
npx serve .
```

By default, the frontend calls its API on the **same origin** (`const API = ""`). If your backend runs elsewhere, update the `API` constant at the top of the `<script>` block in `index.html`, or serve both behind the same reverse proxy.

### Article shape expected by the frontend

```json
{
  "id": 1,
  "source": "Reuters",
  "category": "Tech",
  "headline": "...",
  "desc": "...",
  "img": "https://...",
  "url": "https://...",
  "time": "2h ago",
  "time_ts": 1737000000,
  "color": "#6366f1",
  "score": 42
}
```

---

## 🎨 Theming

Themes are driven entirely by CSS custom properties, toggled via `data-theme` on `<html>`:

| Theme      | Vibe                        |
|------------|-----------------------------|
| Aurora     | Indigo/purple (default)     |
| Dusk Rose  | Rose & pink dusk tones      |
| Arctic     | Light, airy, cool blues     |
| Ember      | Warm amber & orange         |
| Obsidian   | Monochrome, near-black      |

Pick a theme via the 🎨 button in the top nav — it's saved instantly, no reload needed.

---

## 🗺️ Roadmap

- [ ] Persist saved articles (localStorage / account sync)
- [ ] PWA support for installable, offline-first use
- [ ] Push notifications for breaking news
- [ ] Personalized ranking based on swipe history

---

## 👤 Developer

**Prashant Bhatt**
Banker · Vibe Coder · Digital Explorer — building AI-powered apps, autonomous agents, and developer tools.

- 🌐 Website: [prashantbhatt.net](https://prashantbhatt.net)
- 💻 GitHub: [@iprashantbhatt](https://github.com/iprashantbhatt)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

Built with ❤️ by <a href="https://prashantbhatt.net">Prashant Bhatt</a>

</div>
