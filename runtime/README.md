# Voxd Runtime

Voxd is a local text-to-speech runtime with a CLI and HTTP API.

## Quickstart

Install the runtime package from this directory:

```powershell
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
