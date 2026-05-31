/**
 * scripts/dump_expected_fixtures.ts
 *
 * Dump webtool reference fixtures for the v2.2.2 statistics additions
 * (item share distribution + cluster set order) on the 4-set cancer-drivers
 * dataset. Output JSON files live under python/tests/fixtures/expected/ and
 * are consumed by the cross-package parity tests in Python and R.
 *
 * Usage:
 *   npx tsx scripts/dump_expected_fixtures.ts
 *
 * Re-run whenever shareDistribution.ts, clusterHeatmap.ts, csvParser.ts, or
 * statistics.ts change in a way that affects the reference outputs.
 */

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

import { itemShareDistribution } from '../src/utils/shareDistribution.ts';
import { clusterSetOrder } from '../src/utils/clusterHeatmap.ts';
import {
  parseCsvWithDelimiter,
  getBinaryColumns,
  calculateVennCounts,
} from '../src/utils/csvParser.ts';
import { pairwiseStatistics } from '../src/utils/statistics.ts';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(HERE, '..');
const DATASET_PATH = join(REPO_ROOT, 'data', 'dataset_real_cancer_drivers_4.tsv');
const OUT_DIR = join(REPO_ROOT, 'python', 'tests', 'fixtures', 'expected');

const text = readFileSync(DATASET_PATH, 'utf-8');
const csv = parseCsvWithDelimiter(text, '\t', true);
const cols = getBinaryColumns(csv);
const result = calculateVennCounts(csv, cols);

// Derive the item × set binary matrix from result.exclusiveItems, mirroring
// the App.tsx `testItemSetMatrix` useMemo so the matrix the webtool feeds
// into itemShareDistribution is the same one the Python/R packages must
// reproduce via their own dataset → matrix derivation.
const letters = 'ABCDEFGHI'.slice(0, cols.length).split('');
const matrix: number[][] = [];
for (const [label, items] of result.exclusiveItems.entries()) {
  const row = letters.map(l => (label.includes(l) ? 1 : 0));
  for (let i = 0; i < items.length; i++) matrix.push(row);
}

const dist = itemShareDistribution(matrix, cols.length);

// Build the distance matrix D = 1 - Jaccard the same way the Cluster Heatmap
// renderer does: read pairwise Jaccard from pairwiseStatistics and place each
// pair in both upper and lower triangles. Diagonal stays at zero.
const setNames = cols.map(i => csv.headers[i]);
const stats = pairwiseStatistics(result, cols.length, csv.rows.length, setNames);
const n = cols.length;
const letterIndex = new Map<string, number>();
letters.forEach((l, i) => letterIndex.set(l, i));
const D: number[][] = Array.from({ length: n }, () =>
  Array.from({ length: n }, () => 0),
);
for (const st of stats) {
  const i = letterIndex.get(st.a)!;
  const j = letterIndex.get(st.b)!;
  const d = 1 - st.jaccard;
  D[i][j] = d;
  D[j][i] = d;
}
const co = clusterSetOrder(D, 'average');

mkdirSync(OUT_DIR, { recursive: true });

const shareJson =
  JSON.stringify(Object.fromEntries(dist), null, 2) + '\n';
writeFileSync(join(OUT_DIR, 'share_distribution_4set.json'), shareJson);

const clusterJson =
  JSON.stringify(
    {
      leafOrder: co.leafOrder,
      merges: co.merges.map(m => ({
        left: m.left,
        right: m.right,
        height: m.height,
        size: m.size,
      })),
    },
    null,
    2,
  ) + '\n';
writeFileSync(join(OUT_DIR, 'cluster_order_4set.json'), clusterJson);

console.log('Wrote expected fixtures to', OUT_DIR);
console.log('Distribution:', Object.fromEntries(dist));
console.log('Total items:',
  Array.from(dist.values()).reduce((a, b) => a + b, 0));
console.log('Set names (cols):', setNames);
console.log('Leaf order:', co.leafOrder);
console.log('Merges:', co.merges);
