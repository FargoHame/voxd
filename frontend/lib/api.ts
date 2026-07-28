import type { Generation, RuntimeStatus, HubaksModel } from "../types/api";

const API_PREFIX = "/v1";

export async function getModels(): Promise<HubaksModel[]> {
  const response = await fetch(`${API_PREFIX}/models`);
  await assertOk(response);
  const data = (await response.json()) as { models: HubaksModel[] };
  return data.models;
}

export async function getRuntime(): Promise<RuntimeStatus> {
  const response = await fetch(`${API_PREFIX}/runtime`);
  await assertOk(response);
  return (await response.json()) as RuntimeStatus;
}

export async function synthesizeSpeech(payload: {
  model: string;
  input: string;
  voice?: string;
  speed?: number;
}): Promise<{ blob: Blob; generationId: string | null }> {
  const response = await fetch(`${API_PREFIX}/audio/speech`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  await assertOk(response);
  return {
    blob: await response.blob(),
    generationId: response.headers.get("X-Hubaks-Generation-Id"),
  };
}

export async function getGenerations(): Promise<Generation[]> {
  const response = await fetch(`${API_PREFIX}/generations`);
  await assertOk(response);
  const data = (await response.json()) as { generations: Generation[] };
  return data.generations;
}

export async function renameGeneration(id: string, name: string): Promise<Generation> {
  const response = await fetch(`${API_PREFIX}/generations/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name }),
  });
  await assertOk(response);
  return (await response.json()) as Generation;
}

export function generationAudioUrl(id: string): string {
  return `${API_PREFIX}/generations/${id}/audio`;
}

async function assertOk(response: Response): Promise<void> {
  if (response.ok) {
    return;
  }

  let message = response.statusText;
  try {
    const data = (await response.json()) as { detail?: string };
    message = data.detail || message;
  } catch {
    message = await response.text();
  }

  throw new Error(message || `Request failed with ${response.status}`);
}
