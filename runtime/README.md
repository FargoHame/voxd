# Voxd Runtime

Voxd is a local text-to-speech runtime with a CLI and HTTP API.

## Quickstart

Install the runtime package from this directory:

```powershell
uv pip install -e .
```

Install the current VoiceHub backend from the repository commit that matches
Voxd's adapter:

```powershell
uv pip install "voicehub @ git+https://github.com/kadirnar/voicehub.git@2c081336cee7110a97a8501496c65777a76586d7"
```

Start the server:

```powershell
voxd serve
```

Generate speech through the running server:

```powershell
voxd run kokoro "Hello from Voxd" --voice af_heart --output hello.wav
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

VoiceHub temporarily uses a Git dependency pinned to the repository commit that
matches Voxd's adapter. Once PyPI contains the required API, this should move
back to a normal `voicehub>=...` version constraint.
