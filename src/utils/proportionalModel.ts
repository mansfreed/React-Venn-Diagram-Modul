/**
 * Generate a VennDocument from proportional layout.
 * Produces the same structure as parseSvg() for compatibility with all views.
 */
import type { VennDocument } from '../types.ts';
import type { ProportionalCircle, ProportionalLayout } from './proportionalLayout.ts';

const COLORS: Record<string, string> = {
  A: '#FFF200', B: '#2E3192', C: '#ED1C24',
};

/**
 * Sample grid to find centroid of a region defined by bitmask.
 */
function sampleRegionCentroid(
  circles: ProportionalCircle[],
  targetMask: number,
  canvasSize: number,
  resolution = 60,
): { x: number; y: number } | null {
  let sumX = 0, sumY = 0, count = 0;
  const step = canvasSize / resolution;

  for (let gx = 0; gx < resolution; gx++) {
    const px = step * (gx + 0.5);
    for (let gy = 0; gy < resolution; gy++) {
      const py = step * (gy + 0.5);
      let mask = 0;
      for (let i = 0; i < circles.length; i++) {
        const c = circles[i];
        const dx = px - c.cx, dy = py - c.cy;
        if (dx * dx + dy * dy <= c.r * c.r) mask |= (1 << i);
      }
      if (mask === targetMask) {
        sumX += px;
        sumY += py;
        count++;
      }
    }
  }

  return count > 0 ? { x: sumX / count, y: sumY / count } : null;
}

export function generateProportionalModel(
  n: number,
  setNames: string[],
  exclusiveCounts: Map<string, number>,
  inclusiveCounts: Map<string, number>,
  layout: ProportionalLayout,
): VennDocument {
  const letters = 'ABC'.slice(0, n).split('');
  const canvasSize = 700;
  const circles = layout.circles;

  // Shapes
  const shapes = circles.map(c => ({
    id: `Shape${c.letter}`,
    tagName: 'circle',
    attributes: { cx: String(Math.round(c.cx * 10) / 10), cy: String(Math.round(c.cy * 10) / 10), r: String(Math.round(c.r * 10) / 10) },
    style: `opacity:0.2;fill:${COLORS[c.letter] ?? '#888'};stroke:#000000;stroke-width:3;stroke-miterlimit:10;`,
  }));

  // Title — slightly below top
  const header = {
    id: 'Title',
    x: canvasSize / 2,
    y: 55,
    content: `Area-Proportional ${n}-set diagram`,
    style: 'font-size:24;font-family:Tahoma;text-anchor:middle;',
  };

  // Name labels — bottom-left legend, stacked vertically
  const legendX = 45;
  const legendStartY = canvasSize - 30 - (n - 1) * 22;
  const names = circles.map((c, i) => ({
    id: `Name${c.letter}`,
    x: legendX,
    y: legendStartY + i * 22,
    content: setNames[i] ?? c.letter,
    style: 'font-size:14;font-family:Tahoma;text-anchor:start;',
  }));

  // CountSUM labels — positioned after the longest name
  const maxNameLen = Math.max(...setNames.map(s => (s ?? '').length));
  const sumX = legendX + Math.min(maxNameLen * 8.5 + 20, 300);
  const sums = circles.map((c, i) => {
    const total = inclusiveCounts.get(c.letter) ?? 0;
    return {
      id: `CountSUM_${c.letter}`,
      x: Math.round(sumX),
      y: legendStartY + i * 22,
      content: String(total),
      style: 'font-size:14;font-family:Tahoma;text-anchor:start;fill:#262262;',
    };
  });

  // Count labels — at region centroids
  const values: typeof names = [];
  for (let mask = 1; mask < (1 << n); mask++) {
    const label = letters.filter((_, i) => mask & (1 << i)).join('');
    const count = exclusiveCounts.get(label) ?? 0;
    const centroid = sampleRegionCentroid(circles, mask, canvasSize);

    if (centroid) {
      values.push({
        id: `Count_${label}`,
        x: Math.round(centroid.x),
        y: Math.round(centroid.y),
        content: String(count),
        style: 'font-size:20;font-family:Tahoma;text-anchor:middle;fill:#262262;font-weight:bold;',
      });
    } else {
      // Fallback: place near first circle of the set
      const firstLetter = label[0];
      const fc = circles.find(c => c.letter === firstLetter)!;
      values.push({
        id: `Count_${label}`,
        x: Math.round(fc.cx),
        y: Math.round(fc.cy + 5),
        content: String(count),
        style: 'font-size:20;font-family:Tahoma;text-anchor:middle;fill:#262262;font-weight:bold;',
      });
    }
  }

  // Bullets — in legend area, left of names
  const bullets = circles.map((c, i) => ({
    id: `Bullet${c.letter}`,
    cx: legendX - 14,
    cy: legendStartY + i * 22 - 4,
    r: 6,
    style: `fill:${COLORS[c.letter] ?? '#888'};opacity:0.2;`,
  }));

  return {
    filename: '__proportional__.svg',
    rawSvgAttrs: `xmlns="http://www.w3.org/2000/svg" version="1.1" x="0px" y="0px" style="enable-background:new 0 0 ${canvasSize} ${canvasSize};" xml:space="preserve" viewBox="0 0 ${canvasSize} ${canvasSize}"`,
    viewBox: { x: 0, y: 0, w: canvasSize, h: canvasSize },
    comment: '<!-- Area-Proportional Venn Diagram (computed) -->',
    shapes,
    shapesExtras: [],
    texts: { header, names, values, sums },
    bullets,
    meta: { headerHidden: false, bulletsHidden: false, hiddenIds: new Set(), hiddenGroups: new Set() },
  };
}
