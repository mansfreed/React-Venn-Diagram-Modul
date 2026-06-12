import { describe, expect, it } from 'vitest';
import { analyzeCsvText, toRegionSummaryTsv } from '../src/api.ts';

// 2-set binary matrix: col0 = item id, cols A/B are 0/1 membership.
const TSV = [
  'Gene\tA\tB',
  'g1\t1\t0',
  'g2\t1\t1',
  'g3\t0\t1',
].join('\n');

describe('analyzeCsvText', () => {
  it('detects the two binary set columns and their names', () => {
    const r = analyzeCsvText(TSV);
    expect(r.columns).toEqual([1, 2]);
    expect(r.setNames).toEqual(['A', 'B']);
  });

  it('computes exclusive region counts', () => {
    const r = analyzeCsvText(TSV);
    expect(r.venn.exclusive.get('A')).toBe(1);  // g1 only
    expect(r.venn.exclusive.get('B')).toBe(1);  // g3 only
    expect(r.venn.exclusive.get('AB')).toBe(1); // g2 both
  });
});

describe('toRegionSummaryTsv', () => {
  it('emits the 7-column header and one row per non-empty region', () => {
    const tsv = toRegionSummaryTsv(analyzeCsvText(TSV));
    const lines = tsv.split('\n');
    expect(lines[0]).toBe('Region\tSets\tDepth\tExclusive_Count\tInclusive_Count\tExclusive_Pct\tItems');
    // 2^2 - 1 = 3 regions => 1 header + 3 rows
    expect(lines).toHaveLength(4);
  });
});
