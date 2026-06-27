# 5-Pillar Adwi Architecture Upgrade — 2026-06-15

## Summary

Full architectural expansion covering NLU, iPhone remote control, voice I/O, observability, and multi-modal document indexing.

---

## Pillar A: NLU Upgrade

**Model change:** `qwen3:0.6b` → `llama3.1:8b` for intent classification  
**Method:** Ollama native JSON schema enforcement (`format` parameter in API call)  
**Result:** Model physically cannot output an intent token not in the allowed enum

### Intent Coverage (55 total)
Filesystem, Web search (SearXNG/Tavily/Exa/Firecrawl), Memory (3-layer), Obsidian vault, Git/backup, Voice I/O, Nightly loop, Repair/eval, Media, Email, Chat

### Classification Pipeline
1. YouTube/image URL detect (instant, no model)
2. Regex prefilter (zero-latency, ~30 patterns)
3. `llama3.1:8b` + JSON schema (constrained decoding, ~1-2s)
4. `qwen3:0.6b` fallback if model is cold (~0.3s)

---

## Pillar B: iPhone Control Plane

**Full guide:** `adwi/iphone-control-plane.md`

| Component | Status |
|---|---|
| Home Assistant (:8123) | Added to docker-compose.yml — needs `up -d homeassistant` |
| Tailscale VPN | Installed — needs `sudo tailscale up` + auth |
| Cloudflare Tunnel | Added to docker-compose.yml — needs CLOUDFLARE_TUNNEL_TOKEN |
| n8n webhook endpoints | Spec in iphone-control-plane.md |
| Siri Shortcuts | Spec in iphone-control-plane.md |
| Apple Watch | Shortcuts complication setup in guide |

### Siri Phrase → Action Map
- "Run morning brief" → n8n /webhook/morning-brief → Safe Command API
- "What needs my approval?" → n8n → reads Pending User Approval from morning_brief.md
- "Force nightly maintenance" → n8n /webhook/run-nightly → nightly.py

---

## Pillar C: Voice I/O

**New file:** `adwi/voice.py`

| Component | Technology |
|---|---|
| STT | faster-whisper 1.2.1 (base.en model, int8, Apple ANE) |
| TTS | piper-tts 1.4.2 (en_US-lessac-medium, ~63MB, Metal) |
| Recording | sox (brew install sox) |
| Playback | afplay (macOS built-in) |

### Commands
- `/voice-in` or `/listen` — record 6s, transcribe, dispatch as NLU
- `/voice-out <text>` — synthesize and play text
- `/voice-brief` — read morning brief aloud

### Natural language
- "listen to my voice command" → `voice_in` intent
- "read the morning brief out loud" → `voice_out` intent

---

## Pillar D: Observability

### Arize Phoenix (:6006)
- Docker container: `arizephoenix/phoenix:version-8.1.0`
- Start: `bin/start-phoenix` or `docker compose up -d phoenix`
- UI: http://localhost:6006

### OpenTelemetry Instrumentation
- `_otel_span()` context manager in adwi_cli.py — no-op when Phoenix is down
- `classify_intent()` emits spans with: input text, model name, latency_ms
- Data goes to OTLP gRPC collector at localhost:4317

### Promptfoo Eval (nightly)
- Runs 50 ground-truth routing test cases via `promptfoo eval`
- Config: `adwi/promptfoo-eval.yaml` (auto-generated on first run)
- If precision < 95%: added to **Pending User Approval** in morning brief

---

## Pillar E: Multi-Modal Indexing

**Library:** markitdown 0.1.6 (Microsoft open-source)

### Supported Rich Formats (via markitdown)
`.pdf`, `.docx`, `.xlsx`, `.pptx`, `.csv`, `.epub`, `.zip`

### Integration
- `overnight_learn.py` → `read_file_content()` dispatches to markitdown for rich formats
- Rich files allowed up to 5MB (plain text still capped at 180KB)
- Obsidian vault `.md` files and documents in workspace are all indexed

---

## New Port Map

| Port | Service |
|---|---|
| 3000 | Open WebUI |
| 4317 | Phoenix OTLP gRPC |
| 4318 | Phoenix OTLP HTTP |
| 5055 | Safe Command API |
| 5056 | Obsidian Bridge |
| 5678 | n8n |
| 6006 | Arize Phoenix UI |
| 6333 | Qdrant |
| 8123 | Home Assistant |
| 8888 | SearXNG |
| 11434 | Ollama |

---

## Pending User Actions

1. `sudo tailscale up` — authenticate Tailscale
2. `docker compose up -d homeassistant` + complete onboarding at :8123
3. Generate HA Long-Lived Access Token → add to `config/.env`
4. Get Cloudflare Tunnel token → add `CLOUDFLARE_TUNNEL_TOKEN` to `config/.env`
5. `brew install sox` — required for `/voice-in` mic recording
6. Install Tailscale + HA Companion on iPhone (see iphone-control-plane.md)
