# Agent Framework — explainer site

A small, self-contained static site that tells a GitHub visitor honestly what this
project is and what it is not. No build step, no dependencies, no external network
calls — plain HTML + CSS (+ inline SVG). Works on GitHub Pages or any static host.

## Pages

| File | Purpose |
|------|---------|
| `index.html` | What it is, what you get, how to use it, what it achieves, BYOK/security |
| `what-its-not.html` | The honest limitations page — the 58/100 audit, the blunt "NOT" list, roadmap |
| `assets/styles.css` | All styling (light + dark, responsive). Linked locally — no CDN |
| `screenshots/` | Reference screenshots (if generated) |

## Preview locally

From inside the `site/` directory:

```bash
python -m http.server 8000
# then open http://localhost:8000
```

Or open `index.html` directly in a browser — it works with no server because the
CSS is a local relative file and there are no external resources.

## Publish on GitHub Pages

Two common options:

1. **Serve `/site` from a branch.** In the repo, go to
   *Settings → Pages*, set the source to your branch and the `/site` folder
   (Pages can serve from `/` or `/docs`; if it must be `/docs`, rename or copy
   `site/` to `docs/`).
2. **GitHub Actions.** Add a Pages workflow that uploads the `site/` directory as
   the Pages artifact. No build is needed — upload the folder as-is.

Because everything is self-contained and uses relative paths, the site works
identically at a project-pages sub-path (e.g. `user.github.io/agent-framework/`)
and at a root domain.

## Self-contained guarantee

- No `<script src>`, no external `<link>` to CDNs, no web fonts, no remote images.
- The only asset reference is the local `assets/styles.css`.
- Fully functional offline.

## Honesty note

This site is public-facing and its whole ethos is honesty. Every substantive claim
traces to a source in the repo or the close-out pack:

- `constitutional/framework-architecture-v1.2.2.md` — what the framework is
- `instance-riverside-bookings/close-out/ASA-verdict-v1.0.0.md` — the 58/100 audit
- `instance-riverside-bookings/close-out/pilot-test-report-v1.0.0.md` — 6 PASS / 2 PARTIAL / 0 FAIL
- `roadmap/framework-scaling-and-domains-v0.1.0.md` — SME T0–T2 scope
- `roadmap/console-brief-v0.1.0.md` — the BYOK requirement

If you change a claim on the site, re-check it against these sources first.
