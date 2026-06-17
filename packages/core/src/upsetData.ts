import type { RegionData } from './models.ts';
import type { VennResult } from './csvParser.ts';
import type { VennDocument } from './types.ts';

export interface UpsetIntersection {
  members: string[];   // e.g. ['A', 'C']
  size: number;
  label: string;       // 'AC'
}

export interface UpsetData {
  sets: string[];
  intersections: UpsetIntersection[];
}

/**
 * Build UpsetData from RegionData + SVG document (View mode).
 * Reads Count_X text values from the loaded document.
 */
export function upsetDataFromRegionData(
  regionData: RegionData,
  doc: VennDocument,
): UpsetData {
  const sets = regionData.sets;
  const n = sets.length;
  const intersections: UpsetIntersection[] = [];

  for (let mask = 1; mask < (1 << n); mask++) {
    const members = sets.filter((_, i) => mask & (1 << i));
    const label = members.join('');
    const countText = doc.texts.values.find(t => t.id === `Count_${label}`);
    const size = countText ? parseInt(countText.content, 10) || 0 : 0;
    intersections.push({ members, size, label });
  }

  return { sets, intersections };
}

/**
 * Build UpsetData from VennResult (Data mode, after Calculate).
 * Uses exclusive counts (exact region, not inclusive).
 */
export function upsetDataFromVennResult(
  vennResult: VennResult,
  n: number,
): UpsetData {
  const sets = 'ABCDEFGHI'.slice(0, n).split('');
  const intersections: UpsetIntersection[] = [];

  for (const [label, size] of vennResult.exclusive) {
    const members = label.split('');
    intersections.push({ members, size, label });
  }

  return { sets, intersections };
}

/**
 * Sort intersections by size descending (default).
 */
export function sortBySize(data: UpsetData): UpsetIntersection[] {
  return [...data.intersections].sort((a, b) => b.size - a.size);
}

/**
 * Sort intersections by set membership order:
 * first by number of members (ascending), then alphabetically.
 */
export function sortByDegree(data: UpsetData): UpsetIntersection[] {
  return [...data.intersections].sort(
    (a, b) => a.members.length - b.members.length || a.label.localeCompare(b.label),
  );
}

/**
 * Compute set sizes (total items in each set, across all intersections).
 */
export function computeSetSizes(data: UpsetData): Map<string, number> {
  const sizes = new Map<string, number>();
  for (const s of data.sets) sizes.set(s, 0);
  for (const int of data.intersections) {
    for (const m of int.members) {
      sizes.set(m, (sizes.get(m) ?? 0) + int.size);
    }
  }
  return sizes;
}
