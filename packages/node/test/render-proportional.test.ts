import { describe, expect, it } from 'vitest';
import { analyzeCsvText, toProportionalSvg } from '../src/api.ts';

const TWO = ['Gene\tA\tB', 'g1\t1\t0', 'g2\t1\t1', 'g3\t0\t1'].join('\n');
const THREE = ['Gene\tA\tB\tC', 'g1\t1\t0\t0', 'g2\t1\t1\t0', 'g3\t0\t1\t1', 'g4\t1\t1\t1', 'g5\t0\t0\t1'].join('\n');

describe('toProportionalSvg', () => {
  it('renders a well-formed 2-set proportional SVG', () => {
    const svg = toProportionalSvg(analyzeCsvText(TWO));
    expect(svg).toContain('<svg');
    expect(svg).toContain('viewBox');
    expect(svg).toContain('0 0 700 700');
    expect(svg.trimEnd().endsWith('</svg>')).toBe(true);
  });

  it('renders a well-formed 3-set proportional SVG', () => {
    const svg = toProportionalSvg(analyzeCsvText(THREE));
    expect(svg).toContain('<svg');
    expect(svg.trimEnd().endsWith('</svg>')).toBe(true);
  });

  it('throws for n > 3 sets', () => {
    const four = ['Gene\tA\tB\tC\tD', 'g1\t1\t0\t0\t0', 'g2\t1\t1\t1\t1'].join('\n');
    expect(() => toProportionalSvg(analyzeCsvText(four))).toThrow(/2.*3|proportional/i);
  });
});
