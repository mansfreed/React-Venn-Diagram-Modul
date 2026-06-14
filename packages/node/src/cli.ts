#!/usr/bin/env node
import { readFileSync, writeFileSync } from 'node:fs';
import { Command } from 'commander';
import { analyzeCsvText, toMatrixTsv, toRegionSummaryTsv, toStatisticsTsv } from './api.ts';

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
    const result = analyzeCsvText(readFileSync(input, 'utf8'));
    let wroteFile = false;
    if (opts.regionSummary) { writeFileSync(opts.regionSummary, toRegionSummaryTsv(result), 'utf8'); wroteFile = true; }
    if (opts.matrix) { writeFileSync(opts.matrix, toMatrixTsv(result), 'utf8'); wroteFile = true; }
    if (opts.statistics) { writeFileSync(opts.statistics, toStatisticsTsv(result), 'utf8'); wroteFile = true; }
    if (!wroteFile) { process.stdout.write(toRegionSummaryTsv(result) + '\n'); }
  });

program.parse();
