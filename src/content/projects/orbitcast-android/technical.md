---
project: OrbitCast Android
generated_by: orpheon
generated_at: 2026-08-15
source_repository: venvennnn/orbitcast_android
source_commit: d4462f968e1aefefc3026d6c4977be4df448bb4c
---

## Problem

The OrbitCast web dashboard is not a phone. This app is a first-Android-project control plane: one module, no Hilt, no Room, no player stack. Read `ARCHITECTURE.md` before changing shape.

## What it does

Feed list, feed detail with 3s polling while visible, episode detail, create/share-seed, RSS handoff (`ACTION_VIEW` or AntennaPod `pcast://`), settings for API base URL and a Keystore-backed token.

Default API is the live Zerops deployment documented in the README. Auth is not enforced there yet; the interceptor is ready.

## Layout

`MainActivity.kt` is the single activity. `AppContainer.kt` is manual wiring. Retrofit plus an auth interceptor live under `data/api`. Token storage is DataStore and EncryptedFile. UI packages cover feeds, feed, episode, editor, settings.

Open in Android Studio, JDK 17+, API 26+. There is no play button (NG1).
