# Hubaks

Ollama-style local text-to-speech runtime.

Hubaks runs open-source text-to-speech models behind one local CLI, HTTP API, and web UI. It is built for people who want to pull voices, serve them locally, generate speech, and keep generated audio on their own machine.

## Why Hubaks

Most TTS projects expose a model library or a demo script. Hubaks is the runtime layer around those models:

- One local server for supported TTS engines.
- One CLI for model install, model status, and speech generation.
- One HTTP API shaped around `/v1/audio/speech`.
- One built-in web UI for generating, replaying, downloading, and renaming audio.
- Persistent local storage for models and generated clips.

## Current Features

- FastAPI runtime server.
- Typer CLI.
- Built-in React web UI served by the runtime.
- OpenAI-style speech endpoint: `POST /v1/audio/speech`.
- Persistent generated audio history.
- Rename generated audio clips from the web UI or API.
- Local model catalog and install workflow.
- Verified Kokoro and Piper engine adapters.

## Supported Models

| Model | Engine | Notes |
| --- | --- | --- |
| `kokoro` | Kokoro | Default American English Kokoro preset |
| `kokoro-british` | Kokoro | British English Kokoro preset |
| `piper-lessac-low` | Piper | CPU-friendly ONNX voice |
| `piper-amy-low` | Piper | CPU-friendly ONNX voice |

## Install From Source

```powershell
git clone https://github.com/fargohame/hubaks.git
cd hubaks\runtime
uv venv --python 3.11
uv pip install -e ".[engines]"
```

## Start The Runtime

```powershell
hubaks serve
```

Then open:

```text
http://127.0.0.1:11435
```

## Generate Speech

Install a model:

```powershell
hubaks pull kokoro
```

Generate audio through the running local server:

```powershell
hubaks run kokoro "Hello from Hubaks" --voice af_heart --output hello.wav
```

Or call the API:

```powershell
curl http://127.0.0.1:11435/v1/audio/speech `
  -H "Content-Type: application/json" `
  -d "{\"model\":\"kokoro\",\"input\":\"Hello from Hubaks\",\"voice\":\"af_heart\",\"speed\":1.0}" `
  --output speech.wav
```

## Web UI

The runtime serves the built web UI at `http://127.0.0.1:11435`.

The current UI includes:

- Voice Generation tab.
- Voice Copying tab placeholder.
- Runtime status.
- Installed model list.
- Generated audio history.
- Audio playback and download.
- Inline rename for generated clips.

## Local Data

Hubaks stores runtime data in a per-user app data directory by default:

| Platform | Default |
| --- | --- |
| Windows | `%LOCALAPPDATA%\Hubaks` |
| macOS | `~/Library/Application Support/Hubaks` |
| Linux | `~/.local/share/hubaks` |

Override the data directory with:

```powershell
$env:HUBAKS_HOME = "D:\hubaks-data"
```

Generated audio clips are stored under:

```text
<Hubaks data directory>/outputs/generations
```

Each generation has a `.wav` file and a matching `.json` metadata file.

## CLI

```powershell
hubaks doctor
hubaks list
hubaks pull kokoro
hubaks serve
hubaks run kokoro "Hello from Hubaks" --voice af_heart --output hello.wav
hubaks ps
hubaks load kokoro
hubaks unload
hubaks rm kokoro
```

## API

```http
GET /v1/health
GET /v1/version
GET /v1/models
GET /v1/runtime
POST /v1/runtime/load
POST /v1/runtime/unload
POST /v1/audio/speech
GET /v1/generations
GET /v1/generations/{generation_id}/audio
PATCH /v1/generations/{generation_id}
```

Rename request:

```json
{
  "name": "Narration take 1"
}
```

## Development

Backend:

```powershell
cd runtime
uv run pytest
uv run ruff check .
```

Web UI:

```powershell
cd frontend
npm install
npm run build
```

The production web build is copied into `runtime/hubaks/web/dist` and included in the Python package.

## License

MIT
