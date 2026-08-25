---
project: Janus
generated_by: orpheon
generated_at: 2026-08-16
source_repository: venvennnn/janus
source_commit: 19682bc54201b72b2fa84c0cf634d14d60963193
---

## Problem

Credit models can pass a standard review and still fail integrity: they may be gameable, leak proxies for excluded attributes, or miscalibrate whole segments. Janus is a credit-model integrity product. GOAI 2026 Track 2 (Boundless Agents, AI + Finance) is the documented framing.

## Architecture

A language agent (Claude, via Anthropic) reads a feature dictionary and business context and proposes a mutability table: for each feature, what it costs to fake, what it costs to move genuinely, how long that takes, and whether moving it reflects repayment capacity. Those judgements are lender-specific. The LLM never produces a numeric finding.

A deterministic audit engine records every figure against a re-executable run ID (`python -m janus.run_audit` is the documented figure discipline). Without `ANTHROPIC_API_KEY` the same loop runs on a heuristic stand-in so the demo still works.

Two human gates sit on the critical path: confirm mutability assumptions, then accept or reject each finding.

The reference book is a 24,000-applicant synthetic portfolio with a documented causal mechanism in `janus/data_gen.py`, and a 13-feature logistic scorecard with no protected attributes. Numbers that appear in deliverables must come from the audit run, not from prose.

## Serving shape

The recorded walkthrough is static (GitHub Pages). Judges can also upload a model. Pages cannot run Python, so that path is a small FastAPI service on Render with no database. The site stays the essay; the service inspects, searches, and returns the same findings package `run_audit.py` writes. A live demo is documented at the Render URL in project metadata.

## Design decisions

Separating language work from numeric work is the central tradeoff. It costs an extra system boundary and two human gates. It buys a structural ban on hallucinated statistics. Mutability is treated as a language task because feature dictionaries are text and context is local to the lender.

The README is explicit about figure discipline: only numbers from `python -m janus.run_audit` may appear in a deliverable. Two attack-cost medians exist and are not interchangeable. That sentence is a process constraint, not a slogan. Independent products named in the README (NaijaLedger, GemLedger) attack the same absence of documented income from the supply side — they build documentation. Janus measures what its absence costs. Orpheon records that mention because the repository made it; it does not infer a shared codebase.

The reference book's planted mechanism, as documented: cash income unrecorded → recorded DTI inflates → DTI is the heaviest feature → exclusion follows measurement error, not risk. Standard review can still look fine (mid-0.60s AUC, a calibrated cutoff, roughly half the holdout approved). What that review misses is the point of the engine.

Integrity is split into branches in the README: gameable attack surface, exclusion / proxy leakage, reliability of broken segments. Fairness is one branch, not the whole product.

## Serving shape

The recorded walkthrough is static (GitHub Pages). Judges can also upload a model. Pages cannot run Python, so that path is a small FastAPI service on Render with no database. The site stays the essay; the service inspects, searches, and returns the same findings package `run_audit.py` writes. A live demo is documented at the Render URL in project metadata. A YouTube walkthrough and slides are linked from the README.

Without `ANTHROPIC_API_KEY` the same loop runs on a heuristic stand-in so the demo still works. That fallback is documented so a missing key does not silently invent Claude output.

## Limits

Janus does not replace a lender's policy process. It does not publish a universal lever table that works for every book. The reference scorecard is synthetic. Demo infrastructure is intentionally split so the essay remains static. This page does not reproduce a recipe for manipulating a production lender; it describes the integrity product the repository implements.

## Setup and demo

Open the documented demo, or serve the static walkthrough from `docs/index.html` after Pages is enabled. The audit path is `python -m janus.run_audit`. Follow the repository for environment variables. Do not commit API keys. Human gates remain on the path even when the agent is present: confirm mutability, then accept or reject findings.

The upload path is for lenders who bring their own model. The reference path is the synthetic book with a documented mechanism. Both are supposed to produce the same kind of package: evidence against a run ID, not a vibe. If the language agent is unavailable, the heuristic stand-in keeps the demo loop intact; it does not license invented statistics. Read the README's figure discipline before quoting any number from this journal or from a screenshot.
