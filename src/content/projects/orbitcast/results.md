---
project: OrbitCast
generated_by: orpheon
generated_at: '2026-08-09'
source_repository: venvennnn/orbitcast
source_commit: 589c9efd0a8c0113f394321a88fc9506defc8458
---

Seven Zerops services: nginx web, FastAPI API, managed PostgreSQL, managed Valkey, a Python worker, a cron, and S3 object storage. Only web and API are public.

Pipeline: cron enqueues due feeds → Valkey → worker stages researching → writing → voicing → publishing. Anthropic Claude with web search writes a change-aware JSON script or a skip. Speech is edge-tts with OpenAI TTS fallback. `GET /feed/{slug}.xml` serves RSS.

The product is the pipeline and the skip behaviour, not a custom player. Topology should be taken from `DECISIONS.md` and `zerops.yaml`.

