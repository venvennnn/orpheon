---
project: Underwritten Autonomy
generated_by: orpheon
generated_at: 2026-08-13
source_repository: venvennnn/underwritten_autonomy
source_commit: 5b3e3fa097704bcae9e4854ac870e2ec1d816d24
---

## Architecture

Hard gates G1–G4 are described as an ERC-7715 grant on ERC-4337, bounding maximum possible loss. Off-chain sizing plus a mandatory EIP-712 attestation at execution shrinks expected loss.

Haircut bands are frozen in `BANDS_FROZEN.md` (tag `bands-v1.0`) before the generator. Policy versions live in `engine/bands_v1.py` through `v3`; thresholds stay in `engine/bands.py`. Figures come from `evaluate.py`, not from the HTML demo's JS.

Repo map: `engine/`, `sim/`, `eval/`, `reference/` (CreditTransAct study), `artifacts/`. Demo: `underwritten-autonomy-demo.html`. Stage 2 (P1) is scoped as a later grant contract and testnet loop — not this repo's claim of being done.

Reproduce: venv, `pip install -r requirements.txt`, `PYTHONPATH=. python3 evaluate.py`.
