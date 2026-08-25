---
project: Aftermath
generated_by: orpheon
generated_at: 2026-08-25
source_repository: venvennnn/aftermath
source_commit: 8a53a6327d2b226489cf0fae92a0dc7fc0b19f39
---

## Problem

Business software still skips the layer that engineering takes for granted. Code has development, staging, and production. A pricing change, a policy, or an assistant prompt often has only idea and production. Aftermath inserts a rehearsal: idea, Aftermath, then production.

## Architecture

The repository is a Next.js 15 TypeScript application. A seeded multi-agent world stands in for a fictional Bengaluru support cloud named Meridian, with Freshworks-like infrastructure: ticket workflows, knowledge search, an assistant, escalation and finance policy, and phone routing that can be disabled.

A Decision Agent turns a proposed change into prose the rest of the system can run against. A synthetic population is instantiated with plan, tenure, CLV, price sensitivity, loyalty, frustration, memory, and a churn threshold. The World Engine steps thirty simulated days. An Observer Agent reads the resulting threads and names the failure pattern. A Counterfactual Agent opens milder and mitigated universes beside the proposed one. Optional ElevenLabs audio turns the breaking day into an incoming call.

## Data flow

1. A decision is submitted through `POST /api/simulate`.
2. Population and world state are seeded.
3. The engine advances day by day; events can trigger further events.
4. Observer and counterfactual agents read the traces.
5. `POST /api/converse` speaks with a featured synthetic customer.
6. `POST /api/voice` requests cinematic voice audio, with a JSON fallback if ElevenLabs is absent.
7. `GET /api/health` exposes liveness.

## Models and libraries

Gemini is required for Decision Agent prose and live conversations. ElevenLabs is optional. The README does not publish model versions or benchmark numbers, so this journal does not invent them. Tests run with Vitest (`npm test`). The UI is React on Next.js with Tailwind.

## Design decisions

Customers are agents with memory, not rows in a survey table. Time is a first-class loop: the interesting object is a cascade, not a single metric. Voice is a product choice, not a demo flourish — the call is how a future that does not exist yet enters the room.

The README names the cascade explicitly. A price increase can become a complaint; the assistant can mishandle billing; the ticket escalates; a discount is offered; finance rejects it; the customer churns. Aftermath is built so that chain can be inspected as a chain, not collapsed into a single KPI. The Observer Agent's job is to read thousands of those threads and name the failure pattern. The Counterfactual Agent's job is to open milder and mitigated universes beside the proposed one, so a decision is not compared only to a void.

The killer feature is staged as an interruption. When the simulated month reaches the breaking day, an incoming call can enter the room. The voice is a synthetic customer generated from that future. The screen copy documented in the repository is: this customer does not exist yet. That sentence is the product, not a caption.

## Components

- **Decision Agent** — turns a proposed change into prose the world can run against. Requires Gemini as documented.
- **Population** — seeded synthetic customers with plan, tenure, CLV, price sensitivity, loyalty, frustration, memory, and a churn threshold.
- **World Engine** — steps thirty days over a Meridian-like support cloud: tickets, knowledge search, Meridian Assist, escalation, retention, finance policy, optional phone routing.
- **Observer Agent** — names the failure pattern in the traces.
- **Counterfactual Agent** — milder and mitigated universes.
- **Voice path** — ElevenLabs or JSON fallback via `POST /api/voice`.
- **Conversation path** — `POST /api/converse` for a featured synthetic customer.

## Use cases and limits

Use Aftermath to rehearse support, pricing, and assistant-policy changes before they touch real people. It is not a forecast of a named company's actual customers. The Meridian world is fictional and seeded. Without `GEMINI_API_KEY`, Decision Agent prose and live conversations will not run as documented. Voice requires `ELEVENLABS_API_KEY` or degrades to JSON.

This page does not invent latency numbers, conversion lifts, or production user counts. The repository does not publish them. Local verification is `npm test` and `npm run build`. Environment files are `.env.example` copied to `.env.local`; the Orpheon pipeline redacts credential-shaped lines before any model sees repository context.

## Setup and demo

```bash
npm install
cp .env.example .env.local
npm run dev
```

Open the local Next.js dev server. Add `GEMINI_API_KEY` for agent prose. Add `ELEVENLABS_API_KEY` only if you want the future call voiced. `npm run build` and `npm test` are the documented verification commands.

The simulate route is documented as running Decision → Population → World → Observer in one request. Conversation and voice are separate routes so a rehearsal can be inspected without always paying for audio. Health is a liveness probe, not a business metric. If you are reading this as an engineer, start with those four handlers and the seeded Meridian world; the rest of the product is the month that runs between them.

Do not commit secrets. The pipeline that writes this page redacts credential-shaped lines before any model sees them.
