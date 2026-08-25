---
project: OrbitCast Android
generated_by: orpheon
generated_at: 2026-08-15
source_repository: venvennnn/orbitcast_android
source_commit: d4462f968e1aefefc3026d6c4977be4df448bb4c
---

OrbitCast on the server already publishes a real RSS feed. This repository is the phone app that drives that pipeline. It is a control plane, not a player. There is no play button. That is intentional.

From the phone you can see feeds, their cadence, last run and next run, live stage chips, skips, episode scripts and errors, and you can hand the RSS URL to AntennaPod. You can share an article from the browser into the create form so the prompt starts from a URL.

Who is this for? Someone who already has the OrbitCast API and wants to start or watch a feed without opening the web dashboard. What goes in: API base URL and an optional token. What comes out: commands to the pipeline and a link your podcast app understands.
