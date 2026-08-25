---
project: Underwritten Autonomy
generated_by: orpheon
generated_at: 2026-08-13
source_repository: venvennnn/underwritten_autonomy
source_commit: 5b3e3fa097704bcae9e4854ac870e2ec1d816d24
---

Authorization asks whether an agent can spend. Underwriting asks how much it should be trusted to spend right now. Static limits are easy. They are also blunt.

This repository is a Stage-1 evidence package from NTU InnovateX 2026: a risk engine, a frozen scorecard, a simulator, evaluation, and a single-file demo. Hard gates bound maximum possible loss. A risk engine plus an attestation shrinks expected loss. If a hard gate fails, the spend is blocked. If size or a window is too large, it escalates. Otherwise it can go autonomous, with a signed attestation.

Who is this for? People who want agents that spend under a written policy, not a vibe. What goes in: behaviour and a proposed amount. What comes out: block, escalate, or autonomous.
