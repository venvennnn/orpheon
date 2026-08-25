---
project: Aftermath
generated_by: orpheon
generated_at: 2026-08-25
source_repository: venvennnn/aftermath
source_commit: 8a53a6327d2b226489cf0fae92a0dc7fc0b19f39
---

## Used / Influenced This Project

These items are named in the repository README, scripts, or dependency manifests. Orpheon does not claim additional influence.

- **Next.js 15** — framework. Application runtime and API routes (`POST /api/simulate`, `/api/converse`, `/api/voice`, `/api/health`).
- **TypeScript** — language. Source of the world engine and UI.
- **Gemini** — model provider. Documented as required for Decision Agent prose and live conversations.
- **ElevenLabs** — optional voice API. Used for cinematic voices on the future call; JSON fallback if absent.
- **Vitest** — test runner, from `vitest.config.ts` and the README test command.

The README describes a seeded multi-agent world and a Freshworks-like support cloud called Meridian. That product framing is treated as a repository fact. Tailwind CSS appears in the project's config files as the UI layer. No paper, dataset size, or third-party evaluation is cited in the repo, so none is listed here as an original source.

How to read this section: if a library is in `package.json` or named in the README, it can appear as used. If Orpheon merely finds a similar paper on the web, it cannot. The Meridian setting is fiction documented by the author; it is not a claim about Freshworks as a vendor relationship.

## Related Reading Discovered by Orpheon

These resources were not found as citations in Aftermath. They are labelled as discoveries, not as the author's sources. Each item is here because it helps a reader stand next to the repo, not because the commit history says it was used.

- **Multi-agent systems** — concept. [https://en.wikipedia.org/wiki/Multi-agent_system](https://en.wikipedia.org/wiki/Multi-agent_system). Relates to the Decision, Observer, and Counterfactual agents that share a simulated month. Aftermath's agents are a product architecture, not a claim that the repo implements a particular academic MAS framework.
- **Next.js documentation** — technical documentation. [https://nextjs.org/docs](https://nextjs.org/docs). Relates to the App Router application and API handlers. Useful if you want the framework's own words for routing and server handlers.
- **Gemini API docs** — technical documentation. [https://ai.google.dev/gemini-api/docs](https://ai.google.dev/gemini-api/docs). Relates to the required prose and conversation path. The README does not pin a model id, so this journal does not invent one.
- **ElevenLabs API** — technical documentation. [https://elevenlabs.io/docs](https://elevenlabs.io/docs). Relates to optional voice synthesis for the breaking-day call. Absence of the key is a documented fallback to JSON, not a failure of the rest of the engine.
- **Counterfactual reasoning** — concept. [https://en.wikipedia.org/wiki/Counterfactual_thinking](https://en.wikipedia.org/wiki/Counterfactual_thinking). Relates to the Counterfactual Agent's milder and mitigated universes. This is a conceptual neighbour, not a paper the README cites.
- **Vitest documentation** — technical documentation. [https://vitest.dev/](https://vitest.dev/). Relates to `npm test` as the documented verification command.

If a future nightly run finds an explicit citation in `.orpheon.yml`, comments, or commit messages, it belongs in the used/influenced list instead of here. Until then, this section stays labelled as discovery. The point of the split is boring on purpose: a continuously generated journal that quietly promotes related reading into "what we used" would be worse than no journal at all. Aftermath's own agents are documented in the README; Wikipedia and vendor docs are not. Keep the lists apart.