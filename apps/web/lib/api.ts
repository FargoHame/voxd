import type { RuntimeStatus, VoxdModel } from "../types/api";

const API_PREFIX = "/v1";

export async function getModels(): Promise<VoxdModel[]> {
  const response = await fetch(`${API_PREFIX}/models`);
  await assertOk(response);
  const data = (await response.json()) as { models: VoxdModel[] };
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
}): Promise<Blob> {
  const response = await fetch(`${API_PREFIX}/audio/speech`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  await assertOk(response);
  return response.blob();
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
