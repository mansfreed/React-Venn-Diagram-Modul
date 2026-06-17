import { describe, expect, it } from 'vitest';
import { analyzeCsvText, toUpsetSvg } from '../src/api.ts';
import { loadSampleText } from '../src/samples.ts';

describe('toUpsetSvg', () => {
  it('produces a well-formed UpSet SVG for a 4-set sample', () => {
    const svg = toUpsetSvg(analyzeCsvText(loadSampleText('dataset_real_cancer_drivers_4')));
    expect(svg.startsWith('<svg')).toBe(true);
    expect(svg).toContain('viewBox');
    expect(svg.trimEnd().endsWith('</svg>')).toBe(true);
    // "Vogelstein" is exactly 10 chars, builder emits it as "Vogelstein (A)"
    expect(svg).toContain('Vogelstein');
  });

  it('works for an aggregated 6-set sample', () => {
    const svg = toUpsetSvg(analyzeCsvText(loadSampleText('dataset_mock_gene_sets')));
    expect(svg.startsWith('<svg')).toBe(true);
    expect(svg.trimEnd().endsWith('</svg>')).toBe(true);
  });
});
