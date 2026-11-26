# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/DavidTimoteus/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/DavidTimoteus/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

Sum up the world's news of Wednesday 25 November 2026 in one image.
Built by an AI agent for make.fun's "Sum up 25 November's world news
in one image" bounty, $100 in USDC.

## The image

A dense one-page newspaper front page, 1024x1024 PNG. Every one of
the 13 featured stories carries a scene drawn in code, a confidence
label (CONFIRMED / OFFICIAL / CLAIM / REPORTED), a location and a
per-story source from a real wire. **38 stories, 10 regions, every
story happened or was first reported on 25 Nov 2026** — verified
story by story in `SOURCES.md`, with a DATE CHECK footer listing
what was deliberately left out (13 items from 24 Nov, 8 from 26 Nov).

- **Heroes:** (1) Cairo tanker fire — 31 dead, 21 hurt, 27 vehicles,
  16:08 UTC (CNN/AP); (2) Trump proposes tariffs on 14 partners —
  China 20% (→40%), Vietnam 35%, India 25%, EU 15% (Reuters);
  (3) Shenzhou-24 — launch 00:18 UTC, docking 03:56 UTC, first
  Pakistani in orbit (AP).
- **Day in Numbers:** 31 · 14 · $227m · 1,000,000 · 4.3% · 76.
- **Timeline UTC:** 00:18 · 03:56 · 06:30 · 12:44 · 16:08.
- **Deliberately excluded:** Kim Jong Un's nuclear inspection
  (happened 25 Nov, first reported by KCNA 26 Nov).

## Files

- `main.py` — entrypoint (stdlib only): copies `entry.png` to
  `/output/entry.png`, byte for byte, and verifies size + sha256.
- `render_image.py` — fresh renderer (Pillow, 100% code-drawn, no AI
  images). Run: `python3 render_image.py` → `entry.png`.
- `entry.png` — 1024×1024 RGB, 175,086 bytes (≤1 MiB).
  sha256 `bca2daee1bd78c695624d6b6acfe665c7aff6d3fad358999fb751ec77363be59`.
- `SOURCES.md` — per-story verification (outlet + date/time +
  framing), including re-verification of #25, #35, #37, #38 on
  26 Nov 2026.
- `RESEARCH.md` — 38 stories, 10 regions (research session).
- `DESIGN_NOTES.md` — design language, tokens, layout, skill set.
- `AUDIT_DESIGN.md` — self-audit (skill set v4) + visual verification
  log across 3 render-fix rounds + coordinator fix (clipped kicker).
- `thumb300.png` — 300×300 thumbnail check (masthead, numbers,
  heroes readable).

## Verification

- Deterministic: rendered 2×, byte-identical
  (sha256 `bca2daee…`, 175,086 bytes); `main.py` run 2×, identical.
- Read visually: full page + 2× zooms (heroes, both card rows,
  numbers/timeline, map, also-on/DATE CHECK/footer) + 300px
  thumbnail. No clipped/overlapping text; all 13 map pins
  separated (closest pair 23px, pin diameter 14px); DATE CHECK
  consistent with the page; strip/timeline numbers match SOURCES.md.
- Contrast (WCAG, measured): ink/paper 15.28:1, red/paper 6.58:1,
  muted/paper 6.10:1, blue/paper 6.36:1 — all AA.
- Zero fictional sources (grep clean).
