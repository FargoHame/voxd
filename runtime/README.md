# Voxd Runtime

Voxd is a local text-to-speech runtime with a CLI and HTTP API.

## Quickstart

Install the runtime package from this directory:

```powershell
uv venv --python 3.11
uv pip install -e .
```

Install the current Kokoro backend:

```powershell
uv pip install kokoro
uv pip install piper-tts
```

Start the server:

```powershell
voxd serve
```

Open the local web UI:

```text
http://127.0.0.1:11435
```

Generate speech through the running server:

```powershell
voxd pull kokoro
voxd run kokoro "Hello from Voxd" --voice af_heart --output hello.wav
voxd pull kokoro-british
voxd run kokoro-british "Hello from Voxd" --output hello-british.wav
voxd pull piper-lessac-low
voxd run piper-lessac-low "Hello from Piper through Voxd" --output hello-piper.wav
voxd pull piper-amy-low
voxd run piper-amy-low "Hello from another Piper voice" --output hello-piper-amy.wav
```

## Supported Models

The current verified runtime supports four local models across two backends:

| Model | Engine | Notes |
| --- | --- | --- |
| `kokoro` | Kokoro | Default American English Kokoro preset |
| `kokoro-british` | Kokoro | British English Kokoro preset |
| `piper-lessac-low` | Piper | CPU-friendly ONNX voice |
| `piper-amy-low` | Piper | CPU-friendly ONNX voice |

Chatterbox is a candidate backend, but it is not included in this release. Its
package install did not complete reliably in the Python 3.11 runtime during
verification.

Check the local environment:

```powershell
voxd doctor
```

## API

```http
POST /v1/audio/speech
```

```json
{
  "model": "kokoro",
  "input": "Hello from Voxd",
  "voice": "af_heart",
  "speed": 1.0,
  "format": "wav"
}
```

The endpoint returns encoded WAV bytes.

## Web UI

The web UI is served by the runtime when `runtime/voxd/web/dist` exists. It has
two workflows:

- Voice Generation: works with the currently verified Kokoro and Piper models.
- Voice Copying: visible now, ready for Chatterbox or another cloning-capable
  backend when one is verified.
- Generated clips are persisted in `runtime/data/outputs/generations`, reload
  into the history panel, and can be renamed from the web UI.

For frontend development:

```powershell
cd ..\apps\web
npm install
npm run dev
```

For production assets:

```powershell
npm run build
```

## Configuration

Environment variables use the `VOXD_` prefix.

```powershell
$env:VOXD_HOST = "127.0.0.1"
$env:VOXD_PORT = "11435"
$env:VOXD_DEVICE = "cpu"
```

## Engine Dependencies

Voxd keeps backend engines optional so the base runtime remains lightweight. The
recommended product packaging is to expose these as optional extras once each
adapter is implemented and locked:

```powershell
pip install "voxd[kokoro]"
pip install "voxd[piper]"
pip install "voxd[chatterbox]"
pip install "voxd[voicehub]"
```

VoiceHub can remain available as a compatibility backend. If PyPI is behind the
repository API required by Voxd, install it from a pinned Git commit until PyPI
catches up.
