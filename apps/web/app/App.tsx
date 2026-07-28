import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  Copy,
  Download,
  Loader2,
  Mic,
  Play,
  RefreshCw,
  Upload,
  Volume2,
  Waves,
} from "lucide-react";

import { getModels, getRuntime, synthesizeSpeech } from "../lib/api";
import type { Generation, RuntimeStatus, VoxdModel } from "../types/api";

const PRESET_VOICES: Record<string, string[]> = {
  kokoro: ["af_heart", "af_bella", "am_adam", "am_michael"],
  "kokoro-british": ["bf_emma", "bf_isabella", "bm_george", "bm_lewis"],
};

function supportsVoice(model: VoxdModel | undefined): boolean {
  return model?.engine === "kokoro";
}

function supportsVoiceCopying(model: VoxdModel): boolean {
  return model.engine === "chatterbox" || model.name.includes("chatterbox");
}

export function App() {
  const [activeTab, setActiveTab] = useState<"generation" | "copying">("generation");
  const [models, setModels] = useState<VoxdModel[]>([]);
  const [runtime, setRuntime] = useState<RuntimeStatus | null>(null);
  const [selectedModel, setSelectedModel] = useState("kokoro");
  const [selectedVoice, setSelectedVoice] = useState("af_heart");
  const [text, setText] = useState("Hello from Voxd. Local speech synthesis is running.");
  const [speed, setSpeed] = useState(1);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generations, setGenerations] = useState<Generation[]>([]);

  const installedGenerationModels = useMemo(
    () => models.filter((model) => model.installed),
    [models],
  );
  const copyingModels = useMemo(
    () => models.filter((model) => model.installed && supportsVoiceCopying(model)),
    [models],
  );
  const model = models.find((item) => item.name === selectedModel);
  const voices = PRESET_VOICES[selectedModel] ?? [];

  useEffect(() => {
    void refresh();
  }, []);

  useEffect(() => {
    const nextVoice = PRESET_VOICES[selectedModel]?.[0];
    if (nextVoice) {
      setSelectedVoice(nextVoice);
    }
  }, [selectedModel]);

  async function refresh() {
    try {
      const [nextModels, nextRuntime] = await Promise.all([getModels(), getRuntime()]);
      setModels(nextModels);
      setRuntime(nextRuntime);

      const firstInstalled = nextModels.find((item) => item.installed);
      if (firstInstalled && !nextModels.some((item) => item.name === selectedModel)) {
        setSelectedModel(firstInstalled.name);
      }
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to reach Voxd.");
    }
  }

  async function generate() {
    if (!text.trim()) {
      setError("Enter text before generating audio.");
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      const blob = await synthesizeSpeech({
        model: selectedModel,
        input: text.trim(),
        voice: supportsVoice(model) ? selectedVoice : undefined,
        speed: supportsVoice(model) ? speed : undefined,
      });
      const url = URL.createObjectURL(blob);
      const id = crypto.randomUUID();
      setGenerations((items) => [
        {
          id,
          model: selectedModel,
          text: text.trim(),
          url,
          createdAt: new Date().toLocaleTimeString(),
          bytes: blob.size,
        },
        ...items,
      ]);
      await refresh();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Speech generation failed.");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <main className="shell">
      <aside className="sidebar" aria-label="Runtime">
        <div className="brand">
          <div className="brandMark">V</div>
          <div>
            <h1>Voxd</h1>
            <p>Local TTS runtime</p>
          </div>
        </div>

        <section className="statusBlock">
          <div className="sectionLabel">
            <Activity size={16} />
            Runtime
          </div>
          <div className="statusRows">
            <StatusRow label="Server" value="Online" />
            <StatusRow label="Loaded" value={runtime?.loaded ? runtime.model || "Yes" : "None"} />
            <StatusRow label="Engine" value={runtime?.engine || "-"} />
          </div>
          <button className="iconButton textButton" onClick={() => void refresh()} type="button">
            <RefreshCw size={16} />
            Refresh
          </button>
        </section>

        <section className="modelList">
          <div className="sectionLabel">
            <Waves size={16} />
            Models
          </div>
          {models.map((item) => (
            <button
              className={item.name === selectedModel ? "modelItem selected" : "modelItem"}
              key={item.name}
              onClick={() => setSelectedModel(item.name)}
              type="button"
            >
              <span>{item.name}</span>
              <small>{item.engine}</small>
            </button>
          ))}
        </section>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="tabs" role="tablist" aria-label="Voxd workflows">
            <button
              className={activeTab === "generation" ? "tab active" : "tab"}
              onClick={() => setActiveTab("generation")}
              type="button"
            >
              <Volume2 size={16} />
              Voice Generation
            </button>
            <button
              className={activeTab === "copying" ? "tab active" : "tab"}
              onClick={() => setActiveTab("copying")}
              type="button"
            >
              <Copy size={16} />
              Voice Copying
            </button>
          </div>
          <div className="versionPill">{models.length} models</div>
        </header>

        {activeTab === "generation" ? (
          <VoiceGeneration
            error={error}
            generating={generating}
            generations={generations}
            installedModels={installedGenerationModels}
            model={model}
            selectedModel={selectedModel}
            selectedVoice={selectedVoice}
            setSelectedModel={setSelectedModel}
            setSelectedVoice={setSelectedVoice}
            setSpeed={setSpeed}
            setText={setText}
            speed={speed}
            text={text}
            voices={voices}
            onGenerate={() => void generate()}
          />
        ) : (
          <VoiceCopying copyingModels={copyingModels} />
        )}
      </section>
    </main>
  );
}

function VoiceGeneration(props: {
  error: string | null;
  generating: boolean;
  generations: Generation[];
  installedModels: VoxdModel[];
  model: VoxdModel | undefined;
  selectedModel: string;
  selectedVoice: string;
  setSelectedModel: (model: string) => void;
  setSelectedVoice: (voice: string) => void;
  setSpeed: (speed: number) => void;
  setText: (text: string) => void;
  speed: number;
  text: string;
  voices: string[];
  onGenerate: () => void;
}) {
  return (
    <div className="contentGrid">
      <section className="composer">
        <div className="fieldRow">
          <label>
            Model
            <select
              value={props.selectedModel}
              onChange={(event) => props.setSelectedModel(event.target.value)}
            >
              {props.installedModels.map((item) => (
                <option key={item.name} value={item.name}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>

          {supportsVoice(props.model) ? (
            <label>
              Voice
              <select
                value={props.selectedVoice}
                onChange={(event) => props.setSelectedVoice(event.target.value)}
              >
                {props.voices.map((voice) => (
                  <option key={voice} value={voice}>
                    {voice}
                  </option>
                ))}
              </select>
            </label>
          ) : null}

          {supportsVoice(props.model) ? (
            <label>
              Speed
              <input
                max="1.4"
                min="0.7"
                onChange={(event) => props.setSpeed(Number(event.target.value))}
                step="0.05"
                type="range"
                value={props.speed}
              />
            </label>
          ) : null}
        </div>

        <textarea
          aria-label="Text to synthesize"
          onChange={(event) => props.setText(event.target.value)}
          value={props.text}
        />

        <div className="actionRow">
          {props.error ? <p className="errorText">{props.error}</p> : <p>{props.model?.description}</p>}
          <button
            className="primaryButton"
            disabled={props.generating}
            onClick={props.onGenerate}
            type="button"
          >
            {props.generating ? <Loader2 className="spin" size={17} /> : <Play size={17} />}
            Generate
          </button>
        </div>
      </section>

      <section className="history">
        <div className="sectionLabel">
          <Mic size={16} />
          Generated Audio
        </div>
        {props.generations.length === 0 ? (
          <div className="emptyState">No clips generated in this session.</div>
        ) : (
          props.generations.map((item) => <GenerationRow generation={item} key={item.id} />)
        )}
      </section>
    </div>
  );
}

function VoiceCopying(props: { copyingModels: VoxdModel[] }) {
  const enabled = props.copyingModels.length > 0;

  return (
    <div className="copyingLayout">
      <section className="composer">
        <div className="fieldRow">
          <label>
            Cloning model
            <select disabled={!enabled}>
              {enabled ? (
                props.copyingModels.map((model) => (
                  <option key={model.name} value={model.name}>
                    {model.name}
                  </option>
                ))
              ) : (
                <option>No cloning model installed</option>
              )}
            </select>
          </label>
        </div>

        <div className="uploadZone" aria-disabled={!enabled}>
          <Upload size={24} />
          <div>
            <strong>Reference voice</strong>
            <p>Upload a clean WAV sample after a voice-copying backend is installed.</p>
          </div>
        </div>

        <textarea disabled={!enabled} value="Voice copying will use this text once Chatterbox is available." readOnly />

        <div className="actionRow">
          <p>Chatterbox integration will enable this workflow.</p>
          <button className="primaryButton" disabled type="button">
            <Play size={17} />
            Generate
          </button>
        </div>
      </section>
    </div>
  );
}

function GenerationRow({ generation }: { generation: Generation }) {
  return (
    <article className="generationRow">
      <div>
        <strong>{generation.model}</strong>
        <p>{generation.text}</p>
        <small>
          {generation.createdAt} · {Math.round(generation.bytes / 1024)} KB
        </small>
      </div>
      <audio controls src={generation.url} />
      <a className="iconButton" download={`${generation.model}-${generation.id}.wav`} href={generation.url}>
        <Download size={16} />
      </a>
    </article>
  );
}

function StatusRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="statusRow">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
