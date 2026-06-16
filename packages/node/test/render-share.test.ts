import { describe, expect, it } from 'vitest';
import { analyzeCsvText, toShareDistributionSvg } from '../src/api.ts';
import { loadSampleText } from '../src/samples.ts';

describe('toShareDistributionSvg', () => {
  it('produces a well-formed share-distribution SVG', () => {
    const svg = toShareDistributionSvg(analyzeCsvText(loadSampleText('dataset_real_cancer_drivers_4')));
    expect(svg.startsWith('<svg')).toBe(true);
    expect(svg).toContain('viewBox="0 0 480 280"');
    expect(svg.trimEnd().endsWith('</svg>')).toBe(true);
  });

  it('renders for a small aggregated input', () => {
    const svg = toShareDistributionSvg(analyzeCsvText('SetA,SetB\nx,y\ny,z\nz,'));
    expect(svg.startsWith('<svg')).toBe(true);
  });
});
