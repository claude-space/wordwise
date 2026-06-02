# WordWise

A tiny **word-count + reading-time** agent. Paste text → words, characters,
sentences, and reading time. Analysis runs server-side via a FastAPI `/run`
endpoint; the UI is a single self-contained page.

> Demo **external agent** for ShellAgent — adopted via the New Agent wizard's
> **Use an existing agent → External** path. ShellAgent forks this repo into
> the `claude-space` org, runs it on the VM (PM2 → uvicorn), and serves it at
> `/agents/<slug>/` behind auth.

## Run it locally
```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
.venv/bin/uvicorn app.main:app --reload --port 3000
```
Open http://localhost:3000

```bash
curl -s -X POST http://localhost:3000/run \
  -H 'Content-Type: application/json' \
  -d '{"input":"The quick brown fox jumps over the lazy dog."}'
```

## Files
- `app/main.py` — the app (UI + `/run` + `/health`); the platform runs `uvicorn app.main:app`
- `ecosystem.config.js` — how ShellAgent's VM starts it (PM2 → uvicorn, reads `PORT` from `.env`)
- `manifest.json` — agent metadata
- `requirements.txt` — Python deps
- `docs/prd.md` — product spec (ShellAgent shows this in the Studio **PRD** tab)
