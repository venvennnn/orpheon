---
project: DriftGuard
generated_by: orpheon
generated_at: 2026-07-26
source_repository: venvennnn/sitrep_venvenn
source_commit: 8eee32a23e15b7d5a228c1f1d74bfbcf39a9ce62
---

## Shape

Code-track agent for the SitRep Marketplace, built on the SitRep Agent Starter Kit. Layout: `handler.py` entrypoint; `driftguard/extract.py`, `detect.py`, `store.py` (SQLite glossary), `report.py`, `pipeline.py`; fixtures for a three-meeting Activation + ARR demo; `scripts/demo_driftguard.py` runs offline without an LLM.

LLM is optional: default Ollama `llama3.2:1b`, or OpenAI / OpenRouter via `.env`. Workspace scoping partitions the glossary (`workspace: acme-corp`, or `DRIFTGUARD_WORKSPACE` / `DRIFTGUARD_DB_PATH`).

Tests: `python -m unittest discover -s tests -v`. Local SitRep: `bash scripts/run-local.sh`.
