---
project: CausaLens
generated_by: orpheon
generated_at: 2026-08-24
source_repository: venvennnn/causalens
source_commit: e30c21f0e5181515c2fd5ece6414d9469c524856
---

## Used / Influenced This Project

Named in the CausaLens README, architecture notes, or dependency surface:

- **GDELT** — dataset / live source. Web NGrams and snapshot TOC used to propose article candidates.
- **Bright Data Scraper Studio** — platform. Curated live-source spine for configured news domains. The README forbids replacing it with ad-hoc HTML scraping.
- **FastAPI** — framework. Backend API and service layer.
- **NetworkX** — library. Directed event graph.
- **React Flow** and **dagre** — libraries. Interactive graph layout in the Next.js UI.
- **SQLAlchemy / SQLite** — storage. Persistence for articles, events, and edges as documented.
- **LLM provider abstraction (OpenAI / Anthropic / Gemini)** — implementation detail in the README, including JSON repair.

No academic paper is cited in the repository as an original influence, so none is listed here as such. Edge types (`CAUSES`, `CONTRIBUTES_TO`, `TRIGGERS`, `RESPONDS_TO`, `AFFECTS`) are repository vocabulary, not a claim that they implement a named ontology from a paper. Pydantic, httpx, and tenacity are named on the backend stack; they support validation, HTTP, and retries around extraction, not a published evaluation.

How to read this section: collector names and libraries in the README are used/influenced. A well-known paper on causal discovery is not, unless the repo says so.

## Related Reading Discovered by Orpheon

Labelled as discoveries, not as the author's sources. They sit beside the graph; they are not the graph's bibliography.

- **GDELT project** — dataset. [https://www.gdeltproject.org/](https://www.gdeltproject.org/). Relates to candidate generation before Bright Data fetches. Official project pages are the right pointer; this journal does not invent coverage statistics.
- **Causal graphs** — concept. [https://en.wikipedia.org/wiki/Causal_graph](https://en.wikipedia.org/wiki/Causal_graph). Relates to directed event edges and the WHY / WHAT NEXT walks. CausaLens uses a directed event graph with evidence on edges; that is not the same as claiming a particular identification strategy from econometrics.
- **FastAPI documentation** — technical documentation. [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/). Relates to the backend service.
- **React Flow documentation** — technical documentation. [https://reactflow.dev/](https://reactflow.dev/). Relates to the interactive graph.
- **NetworkX documentation** — technical documentation. [https://networkx.org/documentation/stable/](https://networkx.org/documentation/stable/). Relates to in-memory graph operations on events and edges.
- **SQLAlchemy documentation** — technical documentation. [https://docs.sqlalchemy.org/](https://docs.sqlalchemy.org/). Relates to SQLite persistence as documented.
- **Bright Data** — technical documentation. [https://docs.brightdata.com/](https://docs.brightdata.com/). Relates to Scraper Studio collectors. The README's rule still stands: do not replace those collectors with ad-hoc HTML scraping.

Predicted edges in the product UI are dotted and labelled as not established fact. Treat this related-reading list with the same humility: it is Orpheon's reading list, not the author's footnotes. When `.orpheon.yml` later names a paper, that paper graduates. Until then, GDELT and Bright Data remain the only live sources this journal is willing to call original. NetworkX, React Flow, FastAPI, and SQLAlchemy are stack facts; they are not a literature review. A causal-discovery paper stays in related reading unless the repository cites it by name. The same rule applies to GDELT methodology papers and to Bright Data marketing pages: unless the repo cites them, they do not graduate. This page is long enough to be useful and short enough not to impersonate a bibliography the author never kept.