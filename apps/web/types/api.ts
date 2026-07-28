export type VoxdModel = {
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
  model: string;
  text: string;
  url: string;
  createdAt: string;
  bytes: number;
};
