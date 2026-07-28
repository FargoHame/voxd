# Voxd Product Plan

Voxd is an Ollama-style local runtime for text-to-speech. The product owns the
CLI, HTTP API, model catalog, downloads, local model registry, and runtime
lifecycle. TTS libraries are backend engines behind a stable Voxd interface.

## User Experience

```powershell
voxd pull kokoro
voxd run kokoro "Hello from Voxd" --output hello.wav
voxd serve
```

```http
POST /v1/audio/speech
```

```json
{
  "model": "kokoro",
  "input": "Hello from Voxd",
  "voice": "af_heart",
  "format": "wav"
}
```

Users should not need to know whether a model is powered by Kokoro, Piper,
Chatterbox, VoiceHub, or another backend.

## Backend Strategy

VoiceHub is optional, not required. It is useful as a compatibility backend
because it aggregates several models, but Voxd should not inherit its public API.
Each Voxd engine adapter must normalize backend behavior into one contract:

```python
class SpeechEngine:
    def load(model): ...
    def synthesize(request) -> AudioResult: ...
    def unload(): ...
```

Every engine must return encoded audio bytes through `AudioResult`.

## Engine Roadmap

Implemented and verified:

- `kokoro`: default fast local model.
- `piper`: CPU and edge fallback.

Next:

- `chatterbox`: higher-quality expressive and voice-cloning backend.
- `voicehub`: optional broad-coverage compatibility backend.

Current verified model count: four models across two backend engines.

The web UI is now part of the runtime surface. It exposes separate Voice
Generation and Voice Copying tabs, with Voice Copying disabled until a verified
cloning-capable backend is available.

Later candidates:

- `orpheus`: expressive conversational speech.
- `dia`: dialogue-style synthesis.
- `f5-tts`: optional only, because pretrained model licensing can be
  non-commercial.

## Dependency Model

Base Voxd should stay lightweight:

```powershell
pip install voxd
```

Engines are optional extras:

```powershell
pip install "voxd[kokoro]"
pip install "voxd[piper]"
pip install "voxd[chatterbox]"
pip install "voxd[voicehub]"
pip install "voxd[all]"
```

When an upstream package is behind its repository, use a pinned Git dependency
inside the relevant extra. Once PyPI has the required version, switch back to a
normal version constraint.

## Milestones

1. Stable speech request and audio result contract.
2. API and CLI workflow for `voxd run <model>`.
3. Direct Kokoro adapter and valid WAV synthesis.
4. Atomic model installs and repair/reinstall support.
5. Piper adapter.
6. Chatterbox adapter.
7. Expanded model catalog with per-model engine metadata.
8. Cross-platform packaging and installer docs.
