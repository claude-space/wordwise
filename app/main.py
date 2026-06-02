"""WordWise — a tiny word-count & reading-time agent.

Self-contained FastAPI app: it serves its own UI (no external assets, so it
renders correctly behind ShellAgent's path-stripping proxy at
`/agents/<slug>/`) and exposes a JSON `/run` endpoint that does the analysis
server-side.

Endpoints:
  GET  /health  -> {"status": "ok"}   (liveness probe ShellAgent checks)
  GET  /        -> the WordWise web UI
  POST /run     -> {"input": "..."}   -> word/char counts + reading time
"""
from __future__ import annotations

import re

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="WordWise")

WORDS_PER_MINUTE = 200


def analyze(text: str) -> dict:
    text = text or ""
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)
    minutes = word_count / WORDS_PER_MINUTE if word_count else 0.0
    if minutes == 0:
        reading_time = "0 sec"
    elif minutes < 1:
        reading_time = f"{round(minutes * 60)} sec"
    else:
        reading_time = f"{minutes:.1f} min"
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    return {
        "words": word_count,
        "characters": len(text),
        "characters_no_spaces": len(re.sub(r"\s+", "", text)),
        "sentences": len(sentences),
        "reading_time_minutes": round(minutes, 2),
        "reading_time": reading_time,
    }


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.post("/run")
async def run(request: Request) -> JSONResponse:
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    text = ""
    if isinstance(payload, dict):
        text = payload.get("input") or payload.get("text") or ""
    return JSONResponse(analyze(str(text)))


@app.get("/", response_class=HTMLResponse)
async def home() -> HTMLResponse:
    return HTMLResponse(PAGE_HTML)


PAGE_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>WordWise</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { margin:0; font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
         background:#0b0d12; color:#e7e9ee; display:flex; min-height:100vh; align-items:center; justify-content:center; padding:24px; }
  .card { width:100%; max-width:680px; background:#12151c; border:1px solid #232838; border-radius:16px; padding:28px; box-shadow:0 10px 40px rgba(0,0,0,.4); }
  h1 { margin:0 0 4px; font-size:22px; letter-spacing:-.01em; display:flex; align-items:center; gap:10px; }
  .sub { margin:0 0 20px; color:#8b93a7; font-size:13px; }
  textarea { width:100%; min-height:160px; resize:vertical; background:#0b0d12; color:#e7e9ee;
             border:1px solid #232838; border-radius:10px; padding:12px 14px; font-size:14px; line-height:1.5; }
  textarea:focus { outline:none; border-color:#3b82f6; }
  .row { display:flex; gap:10px; margin-top:14px; align-items:center; }
  button { background:#3b82f6; color:#fff; border:0; border-radius:10px; padding:10px 18px; font-size:14px; font-weight:600; cursor:pointer; }
  button:hover { background:#2f6fe0; }
  .stats { display:grid; grid-template-columns:repeat(2,1fr); gap:10px; margin-top:20px; }
  .stat { background:#0b0d12; border:1px solid #232838; border-radius:10px; padding:14px; }
  .stat .v { font-size:24px; font-weight:700; }
  .stat .l { font-size:12px; color:#8b93a7; margin-top:2px; }
  .muted { color:#8b93a7; font-size:12px; }
  .pill { font-size:11px; color:#9bf6c0; background:#0f1f17; border:1px solid #1d3a2a; border-radius:999px; padding:3px 9px; font-weight:600; }
</style>
</head>
<body>
  <div class="card">
    <h1>WordWise <span class="pill">live on ShellAgent</span></h1>
    <p class="sub">Paste text — get word count, characters, sentences, and reading time. Analysis runs server-side.</p>
    <textarea id="t" placeholder="Paste an article, a draft, anything…"></textarea>
    <div class="row">
      <button id="go">Analyze</button>
      <span id="status" class="muted"></span>
    </div>
    <div class="stats" id="stats" hidden>
      <div class="stat"><div class="v" id="words">0</div><div class="l">Words</div></div>
      <div class="stat"><div class="v" id="rt">0</div><div class="l">Reading time</div></div>
      <div class="stat"><div class="v" id="chars">0</div><div class="l">Characters</div></div>
      <div class="stat"><div class="v" id="sent">0</div><div class="l">Sentences</div></div>
    </div>
  </div>
<script>
  // Resolve /run RELATIVE to the current path so it works behind
  // ShellAgent's /agents/<slug>/ proxy (which strips that prefix before
  // forwarding). An absolute "/run" would miss the proxy route.
  function base() {
    const p = location.pathname;
    return p.endsWith("/") ? p : p + "/";
  }
  const $ = (id) => document.getElementById(id);
  async function analyze() {
    $("status").textContent = "Analyzing…";
    try {
      const res = await fetch(base() + "run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: $("t").value }),
      });
      const d = await res.json();
      $("words").textContent = d.words;
      $("rt").textContent = d.reading_time;
      $("chars").textContent = d.characters;
      $("sent").textContent = d.sentences;
      $("stats").hidden = false;
      $("status").textContent = "";
    } catch (e) {
      $("status").textContent = "Error: " + e;
    }
  }
  $("go").addEventListener("click", analyze);
</script>
</body>
</html>"""
