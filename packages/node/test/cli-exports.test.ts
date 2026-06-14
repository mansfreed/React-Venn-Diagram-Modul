import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { describe, expect, it } from 'vitest';

const PKG = join(dirname(fileURLToPath(import.meta.url)), '..');
const CLI = join(PKG, 'dist', 'cli.js');

describe('vdl analyze --matrix / --statistics', () => {
  it('writes matrix and statistics TSVs', () => {
    const tmp = mkdtempSync(join(tmpdir(), 'vdl-'));
    const input = join(tmp, 'in.tsv');
    const mtx = join(tmp, 'matrix.tsv');
    const stats = join(tmp, 'stats.tsv');
    writeFileSync(input, 'Gene\tA\tB\ng1\t1\t0\ng2\t1\t1\ng3\t0\t1\n');

    execFileSync('node', [CLI, 'analyze', input, '--matrix', mtx, '--statistics', stats], { encoding: 'utf8' });

    expect(readFileSync(mtx, 'utf8').split('\n')[0]).toBe('Item\tA\tB\tRegion');
    expect(readFileSync(stats, 'utf8').split('\n')[0].startsWith('Set_A\tSet_B\t')).toBe(true);
  });
});
