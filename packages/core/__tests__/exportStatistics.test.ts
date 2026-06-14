import { describe, expect, it } from 'vitest';
import { calculateVennCounts, exportStatisticsTsv } from '../src/index.ts';

const csv = {
  headers: ['Gene', 'A', 'B'],
  rows: [['g1', '1', '0'], ['g2', '1', '1'], ['g3', '0', '1']],
};

describe('exportStatisticsTsv', () => {
  it('emits the 16-column header ending in Significant', () => {
    const venn = calculateVennCounts(csv, [1, 2]);
    const tsv = exportStatisticsTsv(venn, 2, venn.totalUniqueItems, ['A', 'B']);
    const cols = tsv.split('\n')[0].split('\t');
    expect(cols).toHaveLength(16);
    expect(cols[0]).toBe('Set_A');
    expect(cols[15]).toBe('Significant');
  });

  it('formats the A/B pair row with web-tool number formats', () => {
    const venn = calculateVennCounts(csv, [1, 2]);
    const row = exportStatisticsTsv(venn, 2, venn.totalUniqueItems, ['A', 'B']).split('\n')[1].split('\t');
    // sizeA=2 (g1,g2), sizeB=2 (g2,g3), intersection=1 (g2), union=3
    expect([row[0], row[1], row[4], row[5], row[6], row[7]]).toEqual(['A', 'B', '2', '2', '1', '3']);
    expect(row[8]).toBe('0.3333'); // jaccard 1/3, 4dp
  });
});
