---
project: OrbitCast
generated_by: orpheon
generated_at: 2026-08-09
source_repository: venvennnn/orbitcast
source_commit: 589c9efd0a8c0113f394321a88fc9506defc8458
---

## Problem

Generated audio usually dies after one file. OrbitCast turns a topic into a living RSS podcast.

## Architecture

Seven Zerops services: nginx web, FastAPI API, managed PostgreSQL, managed Valkey, a Python worker, a cron service, and S3 object storage. Only web and API are public. Internal traffic stays on the private network. Object storage uses a public-read bucket and direct URLs, not expiring presigned links.

Pipeline: cron enqueues due feeds → Valkey (`LPUSH` / `BRPOP`) → worker stages researching → writing → voicing → publishing. Anthropic Claude with web search writes a change-aware JSON script (or skip). `synthesize()` is edge-tts with OpenAI TTS fallback. `GET /feed/{slug}.xml` serves RSS.

Each service has its own `zerops.yaml`. Live app and API URLs are in the README.

## Limits

The product is the pipeline and the skip behaviour, not a custom player. Figures and topology should be taken from the repo (`DECISIONS.md`, `zerops.yaml`), not invented here.
