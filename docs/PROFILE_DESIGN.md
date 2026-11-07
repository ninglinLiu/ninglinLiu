# Profile design and maintenance

Original visual direction: ink, warm ivory, jade and copper. Editorial typography, an orbital systems diagram, product footage, a dense upstream contribution atlas and animated workflow diagrams.

## Rebuild

`python scripts/build_profile.py` generates self-contained animated SVGs and `docs/OPEN_SOURCE.md` from `data/contributions.json`. It also refreshes the README's accessible count descriptions. Only Python's standard library is needed.

`python scripts/refresh_contributions.py` fetches merged upstream PRs from GitHub. It rejects incomplete search results. The scheduled workflow refreshes this evidence daily. The omniAI registration milestone is maintained separately and is not inferred from GitHub metrics.

## Data and asset provenance

- The 1,000+ omniAI registered-user milestone was supplied by the project owner on 2026-11-07.
- Contribution counts include merged features, fixes, tests, refactors and documentation. PRs in ninglinLiu-owned repositories are excluded. Each record links to its upstream PR.
- `assets/omniai-product.jpg`: screenshot of the owner's omniAI 3D workspace.
- `assets/omniai-live.gif`: silent capture of the public omniAI landing page.
- `assets/video-showcase.gif`: optimized preview of the owner's published [Script to Video showcase](https://github.com/ninglinLiu/script-to-video-skill/blob/main/docs/media/hero-binance.gif). The source project retains its own sources and credits.
- SVG artwork is authored for this profile; no third-party profile design or personal portrait is copied.

## Presentation

Desktop and mobile SVGs are selected with the README's `picture` elements. CSS animations in SVGs honor `prefers-reduced-motion`; GIFs contain no audio. Main facts and links are also available as native README text. Contact prioritizes the visible email address, followed by the owner's supplied LinkedIn and X profiles.

## Activity, skills and topic icons

`python scripts/refresh_activity.py` reads the public GitHub contribution calendar without authentication and public, owned, non-fork repository language bytes through GitHub GraphQL. `GITHUB_TOKEN` is supplied only through the environment. The rolling calendar includes GitHub contributions, not only commits; height uses a logarithmic scale. Language percentages measure repository bytes, not proficiency or authored lines. Archived public repositories are included.

`python scripts/build_activity.py` builds the isometric calendar, language distribution and curated topic icon panels. Icon sources are recorded in `data/topics.json`; the topics are a curated interest gallery. Core languages are maintained separately as Python, Java, TypeScript and Solidity.

The top Contact link scrolls to the native Contact heading. The complete email remains visible and a Gmail compose link provides a browser-based alternative to `mailto:`. No message is sent by either link.

The existing GitHub Pages portfolio under `docs/index.html` is preserved. Profile publishing modifies the README and supporting assets, not the omniAI application.
