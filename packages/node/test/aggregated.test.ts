import { describe, expect, it } from 'vitest';
import { analyzeCsvText } from '../src/api.ts';

const BINARY = ['Gene\tA\tB', 'g1\t1\t0', 'g2\t1\t1', 'g3\t0\t1'].join('\n');
const AGG = ['SetA,SetB', 'x,y', 'y,z', 'z,'].join('\n');

describe('analyzeCsvText mode detection', () => {
  it('keeps binary matrices on the binary path', () => {
    const r = analyzeCsvText(BINARY);
    expect(r.columns).toEqual([1, 2]);
    expect(r.setNames).toEqual(['A', 'B']);
    expect(r.venn.exclusive.get('AB')).toBe(1);
  });

  it('treats a no-binary-column file as aggregated (every column a set)', () => {
    const r = analyzeCsvText(AGG);
    expect(r.columns).toEqual([0, 1]);
    expect(r.setNames).toEqual(['SetA', 'SetB']);
    expect(r.venn.inclusive.get('A')).toBe(3);
    expect(r.venn.inclusive.get('B')).toBe(2);
    expect(r.venn.inclusive.get('AB')).toBe(2);
  });
});
