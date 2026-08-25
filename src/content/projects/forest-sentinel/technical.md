---
project: Forest Sentinel
generated_by: orpheon
generated_at: 2026-08-03
source_repository: venvennnn/forest_sentinel
source_commit: ea17dff9ab7ba07ab3c3f18623362a4a2e55d1c5
---

## Problem

Passive acoustic recorders are cheap; analysis usually is not. The README's constraint is bandwidth: remote sites often have a few hundred bytes per message, not a path for raw PCM.

## Product

Forest Sentinel is documented as an autonomous environmental monitoring station powered by Gemma, with a Streamlit app (`app.py`). Demo path: `pip install -r requirements.txt`, `python scripts/generate_demo_data.py`, `streamlit run app.py`. Cached backend, no login required for the documented demo.

This page does not invent on-device latency, detection accuracy, or dataset sizes the README does not pin.
