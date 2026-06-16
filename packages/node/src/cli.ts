#!/usr/bin/env node
import { readFileSync, writeFileSync } from 'node:fs';
import { Command } from 'commander';
import { detectGeneSetFormat } from '@venn-diagram-lab/core';
import {
  analyzeGmtText, analyzeGmxText, analyzeCsvText,
  toMatrixTsv, toRegionSummaryTsv, toStatisticsTsv,
  toNetworkSvg, toShareDistributionSvg, toEnrichmentBarSvg, toEnrichmentLollipopSvg,
} from './api.ts';

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

program
  .command('render')
  .description('Render an SVG figure (network | share-dist | enrichment-bar | enrichment-lollipop).')
  .argument('<kind>', 'network | share-dist | enrichment-bar | enrichment-lollipop')
  .argument('<input>', 'input CSV/TSV/GMT/GMX path')
  .option('--out <path>', 'write the SVG here (default: stdout)')
  .option('--metric <metric>', 'edge/enrichment metric')
  .action((kind: string, input: string, opts: { out?: string; metric?: string }) => {
    const text = readFileSync(input, 'utf8');
    const fmt = detectGeneSetFormat(input);
    const result =
      fmt === 'gmt' ? analyzeGmtText(text) :
      fmt === 'gmx' ? analyzeGmxText(text) :
      analyzeCsvText(text);
    let svg: string;
    switch (kind) {
      case 'network': svg = opts.metric ? toNetworkSvg(result, opts.metric as never) : toNetworkSvg(result); break;
      case 'share-dist': svg = toShareDistributionSvg(result); break;
      case 'enrichment-bar': svg = opts.metric ? toEnrichmentBarSvg(result, opts.metric as never) : toEnrichmentBarSvg(result); break;
      case 'enrichment-lollipop': svg = opts.metric ? toEnrichmentLollipopSvg(result, opts.metric as never) : toEnrichmentLollipopSvg(result); break;
      default:
        process.stderr.write(`Unknown render kind: ${kind}\n`);
        process.exitCode = 1;
        return;
    }
    if (opts.out) writeFileSync(opts.out, svg, 'utf8');
    else process.stdout.write(svg + '\n');
  });

program.parse();
