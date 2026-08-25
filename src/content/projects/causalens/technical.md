---
project: CausaLens
generated_by: orpheon
generated_at: 2026-08-24
source_repository: venvennnn/causalens
source_commit: e30c21f0e5181515c2fd5ece6414d9469c524856
---

## Problem

Headlines in Southeast Asia arrive as fragments. Regional markets actually move as chains: power, compute, factories, policy, and capital crossing borders. CausaLens SEA is a causal-intelligence system for that theatre. It answers why an event happened, what sits downstream, and which markets could be affected.

## Architecture

Ingestion has two spines. GDELT Web NGrams plus a snapshot table of contents produce high-quality article candidates after concept match, aggregation, relevance filtering, and deduplication. Bright Data Scraper Studio collectors then fetch configured domains (CNA, Edge, VIR, and others above a relevance floor). The README is explicit: generic `requests` / BeautifulSoup scraping is not a substitute for those collectors.

Normalized articles are deduplicated into real-world events. Causal extraction writes evidence-backed edges of types `CAUSES`, `CONTRIBUTES_TO`, `TRIGGERS`, `RESPONDS_TO`, and `AFFECTS`. The graph is directed. Observed edges are solid, inferred edges dashed, predicted effects dotted and labelled as not established fact.

The frontend is Next.js, TypeScript, Tailwind, React Flow, and dagre. The backend is FastAPI, Pydantic, SQLAlchemy/SQLite, NetworkX, httpx, and tenacity. An LLM provider abstraction covers OpenAI, Anthropic, and Gemini with JSON repair.

## Product motions

- **WHY?** — walk upstream causes.
- **WHAT NEXT?** — walk downstream consequences.
- **REGIONAL RIPPLE** — highlight cross-border effects.

Every edge is supposed to be auditable: supporting articles attach to the relationship.

## Design decisions

Events, not articles, are the unit of analysis. That is a modelling choice with a cost: merging is hard and must not invent sameness. Evidence on the edge is a second choice: a score without sources would be easier and less honest. Predicted edges are visually demoted so the interface cannot impersonate established fact.

The README's regional argument is specific. Capital, manufacturing, power, and policy couple Singapore, Malaysia, Vietnam, Indonesia, and Thailand. China-plus-one electronics, Johor-Singapore compute, and Indonesian incentive races do not stay inside one border. A Singapore power constraint becoming a Johor data-centre boom, or a Vietnam factory expansion showing up in Malaysian packaging utilisation, are the kinds of chains the product is built to hold. CausaLens is not a generic global news graph with a Southeast Asia filter glued on; the region is the primitive. Chinese hyperscaler fundraising changing Singapore wholesale cloud pricing is the same class of story: local coverage, regional mechanism. The graph is how those mechanisms stay attached to evidence instead of dissolving into a timeline.

Bright Data integration is equally specific. `backend/app/clients/brightdata.py` is documented as the collector interface. Only configured domains above `MIN_BRIGHTDATA_RELEVANCE_SCORE` are fetched. That is an operational constraint, not a metaphor: live sources are curated, then normalized, then merged.

## Storage and APIs

Persistence is SQLAlchemy on SQLite as documented. Graph operations use NetworkX. HTTP calls use httpx with tenacity. Pydantic models bound payloads. The LLM layer is a provider abstraction with JSON repair, so a broken object from a model is not silently promoted into an edge.

The three product motions are walks on the same directed graph:

- **WHY?** — upstream.
- **WHAT NEXT?** — downstream.
- **REGIONAL RIPPLE** — cross-border emphasis.

Frontend layout uses React Flow and dagre so the graph is a working surface, not an illustration.

## Limits

The system depends on collector configuration and on whatever the models extract. It does not claim complete coverage of Southeast Asia. Inferred and predicted edges are not the same as observed ones. This page does not invent unpublished endpoints, dataset sizes, or precision numbers. Follow the repository README for environment files, collector credentials, and local run commands. Do not paste secrets into this journal.

## Setup

The documented stack is a Next.js frontend and a FastAPI backend. Ingestion is GDELT candidates plus Bright Data collectors, then normalize → dedupe → event extraction → causal extraction → graph. If a collector is missing, the live spine is missing; the README says not to replace it with ad-hoc HTML scraping.

A reader stepping through a node should find supporting articles on the relationship. That auditability is the UI contract. Solid / dashed / dotted encoding is the honesty contract. WHY / WHAT NEXT / RIPPLE are the three walks. Everything else in the backend exists to keep those contracts from becoming a score with no source. This journal will not add unpublished latency, precision, or coverage numbers on top of that. If those numbers appear later in the repository, a journal update can record them; they will not be guessed here.
