import { describe, expect, it } from 'vitest';
import { analyzeGmtText, analyzeGmxText } from '../src/api.ts';

const GMT = ['SetA\tdesc\tx\ty\tz', 'SetB\tdesc\ty\tz'].join('\n');
const GMX = ['SetA\tSetB', 'descA\tdescB', 'x\ty', 'y\tz', 'z\t'].join('\n');

describe('analyzeGmtText', () => {
  it('parses a GMT file and computes set sizes', () => {
    const r = analyzeGmtText(GMT);
    expect(r.setNames).toEqual(['SetA', 'SetB']);
    expect(r.venn.inclusive.get('A')).toBe(3);
    expect(r.venn.inclusive.get('B')).toBe(2);
    expect(r.venn.inclusive.get('AB')).toBe(2);
  });
});

describe('analyzeGmxText', () => {
  it('parses a GMX file and computes set sizes', () => {
    const r = analyzeGmxText(GMX);
    expect(r.setNames).toEqual(['SetA', 'SetB']);
    expect(r.venn.inclusive.get('A')).toBe(3);
    expect(r.venn.inclusive.get('B')).toBe(2);
  });
});
