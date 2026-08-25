---
project: OrbitCast
generated_by: orpheon
generated_at: 2026-08-09
source_repository: venvennnn/orbitcast
source_commit: 589c9efd0a8c0113f394321a88fc9506defc8458
---

Most generated audio is a one-shot: you type a prompt, you get an MP3, it goes stale. OrbitCast is a podcast that keeps going.

You give it a topic. It researches, writes a script, turns that into speech, puts the MP3 in object storage, and serves an RSS feed any podcast app can play. A cron wakes the feeds that are due. If nothing episode-worthy happened, it logs a skip instead of publishing filler. The novelty the README insists on is memory: each episode reads previous scripts and covers what changed.

Who is this for? Anyone who wants a real feed, not a custom player and an account wall. The flagship example in the repo is MSME Credit Pulse: RBI circulars and credit data as a short daily briefing, with public sources in the show notes.

What goes in: a prompt and a cadence. What comes out: Apple-valid RSS and MP3s. The dashboard shows live stages — researching, writing, voicing, publishing — so a failed job is visible instead of a silent zombie.
