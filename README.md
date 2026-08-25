# Orpheon

A simple engineering journal for public repositories on this account.

Excluded: this site, OrbitCast Android, and empty/placeholder repos (PhysAI Track 2, Google Waxal Challenge).

Each project has four depths: Explain Like I'm 15, Technical, References, and Build History.

Site: **https://venvennnn.github.io/orpheon/**

## When it updates

It does **not** run overnight. It does **not** run when a tracked repo changes.

It runs when you trigger **Actions → Update journal**.

That Action still skips repositories whose HEAD matches `state/repositories.json`, so unchanged projects do not call a model.

## Local site

```bash
npm install
npm run dev
```

Open [http://localhost:4321/orpheon/](http://localhost:4321/orpheon/).

```bash
npm run build
python3 -m pytest tests -q
```

## GitHub Actions secrets

Needed only when you run **Update journal**:

| Secret | Purpose |
| --- | --- |
| `LLM_PROVIDER` | `openai`, `anthropic`, or `gemini` |
| `LLM_MODEL` | Model id |
| Matching API key | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GEMINI_API_KEY` |
| `ORPHEON_GITHUB_TOKEN` | Optional PAT for private repos |

Enable **Settings → Pages → Source: GitHub Actions** after merge.
