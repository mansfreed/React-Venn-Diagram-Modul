import { describe, expect, it } from 'vitest';
import { analyzeCsvText, toEnrichmentBarSvg, toEnrichmentLollipopSvg } from '../src/api.ts';
import { loadSampleText } from '../src/samples.ts';

const result = () => analyzeCsvText(loadSampleText('dataset_real_cancer_drivers_4'));

describe('toEnrichmentBarSvg', () => {
  it('produces a well-formed bar SVG (default metric)', () => {
    const svg = toEnrichmentBarSvg(result());
    expect(svg.startsWith('<svg')).toBe(true);
    expect(svg.trimEnd().endsWith('</svg>')).toBe(true);
  });
  it('accepts the foldEnrichment metric', () => {
    expect(toEnrichmentBarSvg(result(), 'foldEnrichment').startsWith('<svg')).toBe(true);
  });
});

describe('toEnrichmentLollipopSvg', () => {
  it('produces a well-formed lollipop SVG', () => {
    const svg = toEnrichmentLollipopSvg(result());
    expect(svg.startsWith('<svg')).toBe(true);
    expect(svg.trimEnd().endsWith('</svg>')).toBe(true);
  });
});
