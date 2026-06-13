#!/usr/bin/env node
import { readFileSync, writeFileSync } from 'node:fs';
import { Command } from 'commander';
import { analyzeCsvText, toRegionSummaryTsv } from './api.ts';

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
  .action((input: string, opts: { regionSummary?: string }) => {
    const result = analyzeCsvText(readFileSync(input, 'utf8'));
    const tsv = toRegionSummaryTsv(result);
    if (opts.regionSummary) {
      writeFileSync(opts.regionSummary, tsv, 'utf8');
    } else {
      process.stdout.write(tsv + '\n');
    }
  });

program.parse();
