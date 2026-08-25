---
project: Janus
generated_by: orpheon
generated_at: 2026-08-16
source_repository: venvennnn/janus
source_commit: 19682bc54201b72b2fa84c0cf634d14d60963193
---

A lending model is supposed to measure whether someone will repay. In practice it measures whatever it is shown: documents, postcodes, job titles, ratios. If those inputs can be dressed up more cheaply than they can be earned, the model may be rewarding theatre.

Janus asks a blunt question of a credit model: does it reward genuine creditworthiness, or the ability to manipulate what it sees? Fairness is one branch of that question. Reliability is another. Gameability is a third. The product's name for the whole is model integrity.

Think of a lock on a door. A locksmith does not only ask whether the lock opens for the key. They ask whether a cheap copy of the key works, whether the bolt is attached to anything, whether a whole neighbourhood of doors fail the same way. Janus is that inspection for a scorecard.

It does not start from a vibes review. A lender can upload a model and a feature dictionary. An agent reads that dictionary in language, because "what would it cost to fake this field, and what would it cost to truly change it" is a judgement, not a formula. Those judgements become a mutability table. A deterministic engine then runs the checks. The engine, not the language model, produces the numbers. A hallucinated statistic is structurally out of scope: the LLM is not allowed to invent a figure.

Two human gates sit on the path. A person confirms the mutability assumptions. A person accepts or rejects each finding. Janus produces evidence. Someone accountable decides.

The reference book in the repo is a synthetic portfolio with a documented causal mechanism and a simple logistic scorecard. Standard review can look fine — a middling AUC, a calibrated cutoff — and still miss exclusion that comes from measurement error, or a gap between faking a feature in an afternoon and earning it over months. Janus is for the people who have to sign that the model measures what it claims.

Who uses it? Model risk, credit risk, and anyone who has to explain a decline to a regulator or to themselves. What goes in: a model, a feature dictionary, business context. What comes out: a findings package against a re-executable run ID, not a vibe.

The extra rule on the locksmith picture: the inspector who speaks English is not allowed to write the measurements. Numbers come from the engine. Prose comes from the agent. A person still signs. If you only have two minutes: it is a way to ask whether a lending model measures credit, or costume, without letting a language model invent the answer.
