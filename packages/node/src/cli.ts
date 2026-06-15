#!/usr/bin/env node
import { readFileSync, writeFileSync } from 'node:fs';
import { Command } from 'commander';
import { detectGeneSetFormat } from '@venn-diagram-lab/core';
import { analyzeGmtText, analyzeGmxText, analyzeCsvText, toMatrixTsv, toRegionSummaryTsv, toStatisticsTsv } from './api.ts';

const program = new Command();

program
  .name('vdl')
  .description('Headless Venn Diagram Lab — analysis & export from the shell.')
  .version('0.0.0');

program
  .command('analyze')
  .description('Analyse a CSV/TSV and write the Region Summary TSV.')
  .argument('<input>', 'input CSV/TSV path (first column = item id, set columns are 0/1)')
  .option('--region-summary <path>', 'write the Region Summary TSV to this path')
  .option('--matrix <path>', 'write the Item Matrix TSV to this path')
  .option('--statistics <path>', 'write the pairwise Statistics TSV to this path')
  .action((input: string, opts: { regionSummary?: string; matrix?: string; statistics?: string }) => {
    const text = readFileSync(input, 'utf8');
    const fmt = detectGeneSetFormat(input);
    const result =
      fmt === 'gmt' ? analyzeGmtText(text) :
      fmt === 'gmx' ? analyzeGmxText(text) :
      analyzeCsvText(text);
    let wroteFile = false;
    if (opts.regionSummary) { writeFileSync(opts.regionSummary, toRegionSummaryTsv(result), 'utf8'); wroteFile = true; }
    if (opts.matrix) { writeFileSync(opts.matrix, toMatrixTsv(result), 'utf8'); wroteFile = true; }
    if (opts.statistics) { writeFileSync(opts.statistics, toStatisticsTsv(result), 'utf8'); wroteFile = true; }
    if (!wroteFile) { process.stdout.write(toRegionSummaryTsv(result) + '\n'); }
  });

program.parse();
