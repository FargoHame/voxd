export type HubaksModel = {
  name: string;
  engine: string;
  description: string;
  size_bytes: number;
  version: string;
  license: string;
  installed: boolean;
};

export type RuntimeStatus = {
  loaded: boolean;
  model: string | null;
  engine: string | null;
};

export type Generation = {
  id: string;
  name: string;
  model: string;
  engine: string | null;
  text: string;
  filename: string;
  media_type: string;
  sample_rate: number;
  size_bytes: number;
  duration_seconds: number | null;
  created_at: string;
};
