---
project: Janus
generated_by: orpheon
generated_at: 2026-08-16
source_repository: venvennnn/janus
source_commit: 19682bc54201b72b2fa84c0cf634d14d60963193
---

## Used / Influenced This Project

Taken from the Janus README and repository layout:

- **Anthropic Claude** — model. Language work for mutability proposals and investigation write-ups. Documented as never producing a number.
- **FastAPI** — framework. Upload/review service hosted on Render because GitHub Pages cannot run Python.
- **Logistic scorecard (13 features)** — algorithm / reference model. Documented in the README as the book the engine inspects.
- **Synthetic portfolio generator** — dataset. `janus/data_gen.py` holds a documented causal mechanism for 24,000 applicants.
- **GitHub Pages** — deployment. Static recorded walkthrough / essay.

NaijaLedger and GemLedger are named in the README as independent products that attack the same absence of documented income from the supply side. They are listed here because the repository mentions them, not because Orpheon inferred a partnership or a shared repository.

The README also documents GOAI 2026 Track 2 (Boundless Agents, AI + Finance) as the competition framing, and a live demo plus YouTube walkthrough. Those are product pointers, not academic citations. Figure discipline — only `python -m janus.run_audit` numbers in a deliverable — is a process influence: it shapes what this journal is allowed to repeat.

How to read this section: if the README names it, it can sit under used/influenced. A famous fairness paper cannot, unless the repo cites it.

## Related Reading Discovered by Orpheon

Not cited by the repository as original sources. Useful as orientation; not a claim of lineage.

- **Fairness in machine learning** — concept. [https://en.wikipedia.org/wiki/Fairness_(machine_learning)](https://en.wikipedia.org/wiki/Fairness_(machine_learning)). Relates to exclusion and proxy leakage as branches of integrity. Janus's own framing is broader: gameability and reliability sit beside fairness.
- **FastAPI documentation** — technical documentation. [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/). Relates to the Render review service that returns the same findings package as `run_audit.py`.
- **Anthropic API docs** — technical documentation. [https://docs.anthropic.com/](https://docs.anthropic.com/). Relates to the language agent path. The README's constraint still applies: the model proposes mutability and writes investigation prose; it does not emit the figures.
- **Logistic regression** — algorithm. [https://en.wikipedia.org/wiki/Logistic_regression](https://en.wikipedia.org/wiki/Logistic_regression). Relates to the 13-feature reference scorecard. The journal does not treat Wikipedia as the author's source, only as a public description of the algorithm the README names.
- **GitHub Pages docs** — technical documentation. [https://docs.github.com/pages](https://docs.github.com/en/pages). Relates to the static essay/walkthrough half of the demo.
- **Model risk management** — concept. [https://en.wikipedia.org/wiki/Model_risk](https://en.wikipedia.org/wiki/Model_risk). Relates to why a human still accepts or rejects findings. Janus produces evidence; it does not replace the signer.

If later commits cite a paper in `.orpheon.yml` or a comment, that paper moves to the used/influenced list. Until then, Orpheon will not pretend it was always there. Integrity writing that blurs those two lists would repeat the thing Janus is built to catch: a system that claims to measure one thing while actually rewarding another. Claude, FastAPI, the synthetic book, and the scorecard are named. A fairness textbook is not, unless a future commit says so in a place Orpheon is allowed to trust. Related reading exists so an engineer can orient. Used/influenced exists so an auditor can check. Mixing them would make this page look more learned and less true.