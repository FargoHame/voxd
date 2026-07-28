# Hubaks

Ollama-style local text-to-speech runtime.

Hubaks runs open-source text-to-speech models behind one local CLI, HTTP API, and web UI. It is built for people who want to pull voices, serve them locally, generate speech, and keep generated audio on their own machine.

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

## Install With pipx

`pipx` is the recommended install path for Hubaks because it creates an isolated Python environment and exposes a global `hubaks` command. Hubaks currently targets Python 3.11.

On Windows, install pipx first if the `pipx` command is not available:

```powershell
py -m pip install --user pipx
py -m pipx ensurepath
```

Close and reopen PowerShell after `ensurepath`.

After Hubaks is published:

```powershell
pipx install --python 3.11 "hubaks[engines]"
hubaks web
```

From a local release wheel:

```powershell
uv build
pipx install --python 3.11 ..\dist\hubaks-1.5.1-py3-none-any.whl
pipx inject hubaks kokoro piper-tts
hubaks web
```

If pipx reports a local `uv` backend version mismatch, use pipx with the pip backend:

```powershell
pipx install --backend pip --python 3.11 ..\dist\hubaks-1.5.1-py3-none-any.whl
```

If Python 3.11 is not registered with the Windows launcher, pass the full Python path:

```powershell
pipx install --python C:\Path\To\Python311\python.exe ..\dist\hubaks-1.5.1-py3-none-any.whl
```

## Install From Source

From the repository:

```powershell
uv venv --python 3.11
uv pip install -e ".[engines]"
```

## Start The Runtime

One command starts both the local API and the bundled web UI:

```powershell
hubaks serve
```

Open the web UI:

```text
http://127.0.0.1:11435
```

To open the UI automatically:

```powershell
hubaks web
```

or:

```powershell
hubaks serve --open
```

## Generate Speech

```powershell
hubaks pull kokoro
hubaks run kokoro "Hello from Hubaks" --voice af_heart --output hello.wav
```

API:

```http
POST /v1/audio/speech
```

```json
{
  "model": "kokoro",
  "input": "Hello from Hubaks",
  "voice": "af_heart",
  "speed": 1.0,
  "format": "wav"
}
```

The endpoint returns WAV audio bytes.

## Web UI

The runtime serves the built web UI when `hubaks/web/dist` exists. The current UI includes voice generation, runtime status, installed models, generated audio history, playback, download, and inline rename.

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

## Configuration

Environment variables use the `HUBAKS_` prefix.

```powershell
$env:HUBAKS_HOST = "127.0.0.1"
$env:HUBAKS_PORT = "11435"
$env:HUBAKS_DEVICE = "cpu"
```

## CLI

```powershell
hubaks doctor
hubaks list
hubaks pull kokoro
hubaks serve
hubaks web
hubaks run kokoro "Hello from Hubaks" --voice af_heart --output hello.wav
hubaks ps
hubaks load kokoro
hubaks unload
hubaks rm kokoro
```

## Development

```powershell
uv run pytest
uv run ruff check .
```

Build the web UI from the repository root:

```powershell
cd ..\frontend
npm install
npm run build
```

## License

MIT
