import { describe, expect, it } from 'vitest';
import { analyzeCsvText, toNetworkSvg } from '../src/api.ts';
import { loadSampleText } from '../src/samples.ts';

describe('toNetworkSvg', () => {
  it('produces a well-formed SVG for a 4-set sample', () => {
    const svg = toNetworkSvg(analyzeCsvText(loadSampleText('dataset_real_cancer_drivers_4')));
    expect(svg.startsWith('<svg')).toBe(true);
    expect(svg).toContain('viewBox="0 0 600 500"');
    expect(svg.trimEnd().endsWith('</svg>')).toBe(true);
    for (const name of ['Vogelstein', 'COSMIC_CGC', 'OncoKB', 'IntOGen']) {
      expect(svg).toContain(name);
    }
  });

  it('accepts an edge metric', () => {
    const svg = toNetworkSvg(analyzeCsvText(loadSampleText('dataset_real_cancer_drivers_4')), 'jaccard');
    expect(svg.startsWith('<svg')).toBe(true);
  });
});
