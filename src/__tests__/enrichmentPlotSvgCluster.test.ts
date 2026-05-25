import { describe, it, expect } from 'vitest';
import { buildEnrichmentHeatmapSvg } from '../utils/enrichmentPlotSvg.ts';
import type { PairwiseStat } from '../utils/statistics.ts';

const stats: PairwiseStat[] = [
  { pair: 'AB', i: 0, j: 1, intersection: 50, union: 100, jaccard: 0.5,
    overlapCoeff: 0.5, dice: 0.6667, expected: 25, foldEnrichment: 2.0,
    pValue: 0.001, qValue: 0.001, neglog10fdr: 3.0, significant: true },
  { pair: 'AC', i: 0, j: 2, intersection: 5,  union: 100, jaccard: 0.05,
    overlapCoeff: 0.1, dice: 0.0952, expected: 25, foldEnrichment: 0.2,
    pValue: 0.5,   qValue: 0.6,   neglog10fdr: 0.22, significant: false },
  { pair: 'BC', i: 1, j: 2, intersection: 5,  union: 100, jaccard: 0.05,
    overlapCoeff: 0.1, dice: 0.0952, expected: 25, foldEnrichment: 0.2,
    pValue: 0.5,   qValue: 0.6,   neglog10fdr: 0.22, significant: false },
];

describe('buildEnrichmentHeatmapSvg cluster mode', () => {
  it('Original mode unchanged (no clusterOrder passed)', () => {
    const svg = buildEnrichmentHeatmapSvg(stats, ['A', 'B', 'C'], ['SetA', 'SetB', 'SetC'], {
      metric: 'neglog10fdr',
    });
    expect(svg.indexOf('SetA')).toBeLessThan(svg.indexOf('SetB'));
  });

  it('Cluster mode reorders by leaf order', () => {
    const svg = buildEnrichmentHeatmapSvg(stats, ['A', 'B', 'C'], ['SetA', 'SetB', 'SetC'], {
      metric: 'neglog10fdr',
      clusterOrder: { leafOrder: [1, 0, 2], merges: [
        { left: 0, right: 1, height: 0.5, size: 2 },
        { left: 3, right: 2, height: 0.95, size: 3 },
      ]},
      showRowDendrogram: true,
      showColDendrogram: true,
      dendrogramFraction: 0.12,
    });
    expect(svg.indexOf('SetB')).toBeLessThan(svg.indexOf('SetA'));
    expect(svg).toContain('class="hm-dendro-col"');
    expect(svg).toContain('class="hm-dendro-row"');
  });

  it('Cluster mode without row dendrogram skips that group', () => {
    const svg = buildEnrichmentHeatmapSvg(stats, ['A', 'B', 'C'], ['SetA', 'SetB', 'SetC'], {
      metric: 'neglog10fdr',
      clusterOrder: { leafOrder: [1, 0, 2], merges: [
        { left: 0, right: 1, height: 0.5, size: 2 },
        { left: 3, right: 2, height: 0.95, size: 3 },
      ]},
      showRowDendrogram: false,
      showColDendrogram: true,
      dendrogramFraction: 0.12,
    });
    expect(svg).not.toContain('class="hm-dendro-row"');
    expect(svg).toContain('class="hm-dendro-col"');
  });
});
