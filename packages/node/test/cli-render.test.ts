import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { describe, expect, it } from 'vitest';

const PKG = join(dirname(fileURLToPath(import.meta.url)), '..');
const CLI = join(PKG, 'dist', 'cli.js');
const SAMPLE = join(PKG, '..', '..', 'data', 'dataset_real_cancer_drivers_4.tsv');

describe('vdl render', () => {
  for (const kind of ['network', 'share-dist', 'enrichment-bar', 'enrichment-lollipop']) {
    it(`renders ${kind} to an SVG file`, () => {
      const out = join(mkdtempSync(join(tmpdir(), 'vdl-')), `${kind}.svg`);
      execFileSync('node', [CLI, 'render', kind, SAMPLE, '--out', out], { encoding: 'utf8' });
      const svg = readFileSync(out, 'utf8');
      expect(svg.startsWith('<svg')).toBe(true);
      expect(svg.trimEnd().endsWith('</svg>')).toBe(true);
    });
  }
});
