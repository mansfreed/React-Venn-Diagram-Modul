import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { analyzeCsvText, toRegionSummaryTsv } from '../src/api.ts';
import { loadSampleText } from '../src/samples.ts';

const FIXTURES = join(dirname(fileURLToPath(import.meta.url)), 'fixtures');

function golden(name: string): string {
  // Goldens are stored without a trailing newline; normalise both sides.
  return readFileSync(join(FIXTURES, name), 'utf8').replace(/\n$/, '');
}

describe('byte-parity vs web tool / Python / R', () => {
  it('region summary matches the cancer-drivers golden exactly', () => {
    const tsv = toRegionSummaryTsv(analyzeCsvText(loadSampleText('dataset_real_cancer_drivers_4')));
    expect(tsv.replace(/\n$/, '')).toBe(
      golden('dataset_real_cancer_drivers_4__venn-4-set__region_summary.tsv'),
    );
  });
});
