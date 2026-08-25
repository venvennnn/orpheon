# Orpheon

A continuously generated engineering journal.

Orpheon is not a portfolio that asks a model to rewrite a README every night. It is a **deterministic change-detection pipeline**. Git history is the source of truth. Human metadata is authoritative. The model is used only after a repository actually moved, and only to interpret that movement.

The site answers four questions for every project:

| Time you have | Page |
| --- | --- |
| Two minutes | Explain Like I'm 15 |
| You are an engineer | Technical Deep Dive |
| You want the theory | References & Ideas |
| You want the making of | Build History |

Live site (GitHub Pages project URL):

**https://venvennnn.github.io/orpheon/**

## How a night run works

During the day, commits accumulate. Nothing in this repository calls an LLM on `push`.

Around 23:30 Asia/Kolkata (`cron: 0 18 * * *` UTC) GitHub Actions:

1. Loads `config/projects.yml`
2. For each enabled repository, compares `HEAD` to `state/repositories.json`
3. **Identical SHA → skip.** No diff, no model, no rewrite.
4. Changed SHA → `git`-equivalent compare of `last_processed_sha..HEAD`, bounded context, secret redaction
5. Classification (JSON) decides which pages, if any, to touch
6. Generation + validation
7. SHA is stored only after a successful write
8. If files changed: `orpheon: nightly journal update YYYY-MM-DD`
9. `deploy.yml` rebuilds GitHub Pages

One broken repository does not stop the others. Failed projects keep their previous SHA and are retried the following night.

## Local site

```bash
npm install
npm run dev
```

Open [http://localhost:4321/orpheon/](http://localhost:4321/orpheon/).

```bash
npm run build
npm run preview
python3 -m pytest tests -q
```

## Add a project

1. Append to `config/projects.yml`:

```yaml
  - repository: venvennnn/your-repo
    slug: your-repo
    enabled: true
```

2. Optionally add `.orpheon.yml` to that repository (see `examples/orpheon.yml`). It is trusted human metadata and is never overridden by the model.
3. The next nightly run bootstraps the journal: ELI15, technical, references, architecture, metadata, and a single **Project imported into Orpheon** history entry. It does not fabricate a backdated log from old commits.

## GitHub Actions secrets

Configure these on the Orpheon repository. Never commit keys.

| Secret | Purpose |
| --- | --- |
| `LLM_PROVIDER` | `openai`, `anthropic`, or `gemini` |
| `LLM_MODEL` | Model id for that provider |
| `OPENAI_API_KEY` | When provider is OpenAI |
| `ANTHROPIC_API_KEY` | When provider is Anthropic |
| `GEMINI_API_KEY` | When provider is Gemini |
| `ORPHEON_GITHUB_TOKEN` | Optional PAT if you track private repos |

`GITHUB_TOKEN` is provided by Actions and is enough for public repositories.

After merging, enable **Settings → Pages → Source: GitHub Actions**.

You can also run **Orpheon nightly** manually from the Actions tab (`workflow_dispatch`), including a single project or a dry run.

## What the model is not allowed to do

- Publish secrets, tokens, `.env` contents, or private URLs
- Invent papers, APIs, files, benchmarks, users, or business claims
- Rewrite old build-history entries
- Treat “Related Reading Discovered by Orpheon” as original influence
- Override `.orpheon.yml`

## Layout

```text
config/projects.yml          tracked repositories
state/repositories.json      last processed SHA per repo
scripts/                     nightly pipeline
src/content/projects/<slug>/ generated journal
  metadata.json
  eli15.md
  technical.md
  references.md
  build-log.md
  architecture.mmd
  evolution.md               major transitions only
```

## Cost control

HEAD comparison → changed filenames → diff → rule-based ignore → classification → generation. Unchanged repositories never reach the model.
