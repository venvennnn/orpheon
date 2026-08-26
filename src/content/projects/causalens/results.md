---
project: CausaLens
generated_by: orpheon
generated_at: '2026-08-24'
source_repository: venvennnn/causalens
source_commit: e30c21f0e5181515c2fd5ece6414d9469c524856
---

Ingestion has two spines: GDELT candidates after concept match and relevance filtering, and Bright Data Scraper Studio collectors for configured domains. Generic HTML scraping is not a substitute for those collectors.

Causal extraction writes directed edges of types CAUSES, CONTRIBUTES_TO, TRIGGERS, RESPONDS_TO, and AFFECTS. The frontend is Next.js, React Flow, and dagre. The backend is FastAPI, SQLAlchemy/SQLite, and NetworkX, with an LLM provider abstraction and JSON repair.

The product is honest about what it does not know. Predicted effects cannot impersonate established fact. Merging events is hard and must not invent sameness. This journal does not invent precision, recall, or live source counts the repository does not publish.

