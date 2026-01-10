export interface ModelEntry {
  filename: string;
  label: string;
  setCount: number;
}

export const MODEL_LIST: ModelEntry[] = [
  { filename: 'venn-2-set.svg', label: '2-set (Euler-Venn)', setCount: 2 },
  { filename: 'venn-2a-set-edwards.svg', label: '2-set (Edwards)', setCount: 2 },
  { filename: 'venn-2e-set-rectangle.svg', label: '2-set (rectangle)', setCount: 2 },
  { filename: 'venn-2e-set-carroll-triangle.svg', label: '2-set (Carroll triangle)', setCount: 2 },
  { filename: 'venn-3-set.svg', label: '3-set (Euler-Venn)', setCount: 3 },
  { filename: 'venn-3a-set-edwards.svg', label: '3-set (Edwards)', setCount: 3 },
  { filename: 'venn-3b-set-anderson.svg', label: '3-set (Anderson)', setCount: 3 },
  { filename: 'venn-3e-set-rectangles.svg', label: '3-set (rectangle)', setCount: 3 },
  { filename: 'venn-3e-set-rectangle-curved.svg', label: '3-set (rectangle curved)', setCount: 3 },
  { filename: 'venn-3e-set-carroll-triangle.svg', label: '3-set (Carroll triangle)', setCount: 3 },
  { filename: 'venn-4f-set.svg', label: '4-set (Venn 3+1)', setCount: 4 },
  { filename: 'venn-4-set.svg', label: '4-set (Venn shapes)', setCount: 4 },
  { filename: 'venn-4e-set-euler.svg', label: '4-set (Euler, not Venn)', setCount: 4 },
  { filename: 'venn-4a-set-edwards.svg', label: '4-set (Edwards)', setCount: 4 },
  { filename: 'venn-4b-set-anderson.svg', label: '4-set (Anderson)', setCount: 4 },
  { filename: 'venn-4e-set-rectangle.svg', label: '4-set (rectangle)', setCount: 4 },
  { filename: 'venn-4e-set-carroll-triangle.svg', label: '4-set (Carroll triangle)', setCount: 4 },
  { filename: 'venn-5f-set.svg', label: '5-set (Venn)', setCount: 5 },
  { filename: 'venn-5e-set-euler.svg', label: '5-set (Euler, not Venn)', setCount: 5 },
  { filename: 'venn-5-set-grunbaum.svg', label: '5-set (Grünbaum)', setCount: 5 },
  { filename: 'venn-5a-set-edwards.svg', label: '5-set (Edwards)', setCount: 5 },
  { filename: 'venn-5b-set-anderson.svg', label: '5-set (Anderson)', setCount: 5 },
  { filename: 'venn-5d-set-bannier.svg', label: '5-set (Bannier-Bodin)', setCount: 5 },
  { filename: 'venn-5e-set.svg', label: '5-set (Shapes)', setCount: 5 },
  { filename: 'venn-5e-set-carroll-triangle.svg', label: '5-set (Carroll triangle)', setCount: 5 },
  { filename: 'venn-6-set.svg', label: '6-set (SUMO)', setCount: 6 },
  { filename: 'venn-6a-set-edwards.svg', label: '6-set (Edwards)', setCount: 6 },
  { filename: 'venn-6b-set-anderson.svg', label: '6-set (Anderson)', setCount: 6 },
  { filename: 'venn-6d-set-bannier.svg', label: '6-set (Bannier-Bodin)', setCount: 6 },
  { filename: 'venn-6e-set-carroll-triangle.svg', label: '6-set (Carroll triangle)', setCount: 6 },
  { filename: 'venn-7-set-grunbaum.svg', label: '7-set (Grünbaum)', setCount: 7 },
  { filename: 'venn-7a-set-edwards.svg', label: '7-set (Edwards)', setCount: 7 },
  { filename: 'venn-7c-set-adelaide.svg', label: '7-set (Adelaide v1)', setCount: 7 },
  { filename: 'venn-7e-set-adelaide.svg', label: '7-set (Adelaide v2)', setCount: 7 },
  { filename: 'venn-7d-set-bannier.svg', label: '7-set (Bannier-Bodin)', setCount: 7 },
  { filename: 'venn-7e-set-hamilton.svg', label: '7-set (Hamilton)', setCount: 7 },
  { filename: 'venn-7e-set-manawatu.svg', label: '7-set (Manawatu)', setCount: 7 },
  { filename: 'venn-7e-set-massey.svg', label: '7-set (Massey)', setCount: 7 },
  { filename: 'venn-7e-set-palmerston-north.svg', label: '7-set (Palmerston North)', setCount: 7 },
  { filename: 'venn-7e-set-victoria.svg', label: '7-set (Victoria)', setCount: 7 },
  { filename: 'venn-8-set.svg', label: '8-set (SUMO)', setCount: 8 },
  { filename: 'venn-8a-set-edwards.svg', label: '8-set (generated)', setCount: 8 },
  { filename: 'venn-8d-set-bannier.svg', label: '8-set (Bannier-Bodin)', setCount: 8 },
  { filename: 'venn-9a-set-edwards.svg', label: '9-set (generated)', setCount: 9 },
];

export function getModelsBySetCount(): Map<number, ModelEntry[]> {
  const map = new Map<number, ModelEntry[]>();
  for (const m of MODEL_LIST) {
    if (!map.has(m.setCount)) map.set(m.setCount, []);
    map.get(m.setCount)!.push(m);
  }
  return map;
}

export async function fetchModel(filename: string): Promise<string> {
  const resp = await fetch(`./models/svg/${filename}`);
  if (!resp.ok) throw new Error(`Failed to load ${filename}: ${resp.status}`);
  return resp.text();
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

export async function fetchRegionData(filename: string): Promise<RegionData> {
  const jsonName = filename.replace('.svg', '.json');
  const resp = await fetch(`./models/json/${jsonName}`);
  if (!resp.ok) throw new Error(`Failed to load region data ${jsonName}: ${resp.status}`);
  return resp.json();
}
