// Pure model type declarations shared by core renderers.
// The runtime catalog (MODEL_LIST) and fetch helpers stay in the web app's src/models.ts.

export interface ModelEntry {
  filename: string;
  label: string;
  setCount: number;
}

export interface RegionData {
  name: string;
  n: number;
  sets: string[];
  curves: string[];
  regions: string[];
  colors: Record<string, string>;
  region_labels: Record<string, [number, number]>;
  set_names: Record<string, string>;
}
