---
project: Underwritten Autonomy
generated_by: orpheon
generated_at: '2026-08-13'
source_repository: venvennnn/underwritten_autonomy
source_commit: 5b3e3fa097704bcae9e4854ac870e2ec1d816d24
---

Don't give agents static spending limits. Underwrite exposure from behaviour, then enforce it.

### Hard gates bound worst case
G1–G4, described as an ERC-7715 grant on ERC-4337, bound maximum possible loss.

### Behaviour shrinks expected loss
A frozen scorecard plus a mandatory EIP-712 attestation at execution sizes the spend.

### Block, escalate, or autonomous
If a hard gate fails, the spend is blocked. If size or a window is too large, it escalates. Otherwise it can go autonomous, with a signed attestation.

