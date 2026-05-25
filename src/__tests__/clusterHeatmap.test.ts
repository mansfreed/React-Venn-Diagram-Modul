import { describe, it, expect } from 'vitest';
import { clusterSetOrder } from '../utils/clusterHeatmap.ts';

describe('clusterSetOrder', () => {
  const D = [
    [0.0, 0.2, 0.9, 0.8],
    [0.2, 0.0, 0.85, 0.75],
    [0.9, 0.85, 0.0, 0.1],
    [0.8, 0.75, 0.1, 0.0],
  ];

  it('produces the expected leaf order under average linkage', () => {
    const co = clusterSetOrder(D, 'average');
    expect(co.leafOrder).toEqual([0, 1, 2, 3]);
    expect(co.merges).toHaveLength(3);
    expect(co.merges[0].height).toBeCloseTo(0.1, 6);
    expect(co.merges[1].height).toBeCloseTo(0.2, 6);
    expect(co.merges[2].height).toBeCloseTo(0.825, 6);
  });

  it('produces the expected leaf order under complete linkage', () => {
    const co = clusterSetOrder(D, 'complete');
    expect(co.leafOrder).toEqual([0, 1, 2, 3]);
    expect(co.merges[0].height).toBeCloseTo(0.1, 6);
    expect(co.merges[1].height).toBeCloseTo(0.2, 6);
    expect(co.merges[2].height).toBeCloseTo(0.9, 6);
  });

  it('produces the expected leaf order under single linkage', () => {
    const co = clusterSetOrder(D, 'single');
    expect(co.leafOrder).toEqual([0, 1, 2, 3]);
    expect(co.merges[2].height).toBeCloseTo(0.75, 6);
  });

  it('handles N=2 (one merge, identity order)', () => {
    const co = clusterSetOrder([[0.0, 0.5], [0.5, 0.0]], 'average');
    expect(co.leafOrder).toEqual([0, 1]);
    expect(co.merges).toHaveLength(1);
    expect(co.merges[0].height).toBeCloseTo(0.5, 6);
  });

  it('handles N=1 (no merges, leaf-only)', () => {
    const co = clusterSetOrder([[0.0]], 'average');
    expect(co.leafOrder).toEqual([0]);
    expect(co.merges).toHaveLength(0);
  });
});
