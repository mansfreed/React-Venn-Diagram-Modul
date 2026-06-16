import {
  buildNetworkData,
  buildNetworkSvgString,
  buildShareDistributionSvg,
  calculateVennCounts,
  calculateVennCountsFromAggregated,
  detectDelimiter,
  exportMatrixTsv,
  exportRegionSummaryTsv,
  exportStatisticsTsv,
  getBinaryColumns,
  itemShareDistribution,
  parseCsvWithDelimiter,
  parseGmt,
  parseGmx,
  type CsvData,
  type EdgeWeightMetric,
  type VennResult,
} from '@venn-diagram-lab/core';

const LETTERS = 'ABCDEFGHI';

export interface AnalyzeResult {
  csv: CsvData;
  columns: number[];
  setNames: string[];
  venn: VennResult;
}

/** Analyse an already-parsed CsvData, auto-detecting binary vs aggregated mode. */
export function analyzeCsv(csv: CsvData): AnalyzeResult {
  const binaryColumns = getBinaryColumns(csv);
  if (binaryColumns.length >= 2) {
    const setNames = binaryColumns.map(i => csv.headers[i]);
    return { csv, columns: binaryColumns, setNames, venn: calculateVennCounts(csv, binaryColumns) };
  }
  // Aggregated: every column is a set, cells hold the items.
  const columns = csv.headers.map((_, i) => i);
  const setNames = columns.map(i => csv.headers[i]);
  return { csv, columns, setNames, venn: calculateVennCountsFromAggregated(csv, columns) };
}

/** Parse raw CSV/TSV text and analyse it (auto binary vs aggregated). */
export function analyzeCsvText(text: string): AnalyzeResult {
  const delimiter = detectDelimiter(text);
  return analyzeCsv(parseCsvWithDelimiter(text, delimiter, true));
}

/** Region Summary TSV — byte-identical to the web tool's "Export → Region Summary". */
export function toRegionSummaryTsv(result: AnalyzeResult): string {
  return exportRegionSummaryTsv(
    result.venn,
    result.columns.length,
    result.setNames,
    result.venn.totalUniqueItems,
  );
}

/** Item Matrix TSV — byte-identical to the web tool's "Export -> Item Matrix". */
export function toMatrixTsv(result: AnalyzeResult): string {
  return exportMatrixTsv(result.venn, result.columns.length, result.setNames);
}

/** Pairwise Statistics TSV — byte-identical to the web tool's "Export -> Statistics". */
export function toStatisticsTsv(result: AnalyzeResult): string {
  return exportStatisticsTsv(
    result.venn,
    result.columns.length,
    result.venn.totalUniqueItems,
    result.setNames,
  );
}

/** Analyse a GMT (Gene Matrix Transposed) gene-set file. */
export function analyzeGmtText(text: string): AnalyzeResult {
  return analyzeCsv(parseGmt(text).csv);
}

/** Analyse a GMX (column-oriented gene-set) file. */
export function analyzeGmxText(text: string): AnalyzeResult {
  return analyzeCsv(parseGmx(text).csv);
}

/** Force-directed Network SVG of the set relationships. */
export function toNetworkSvg(result: AnalyzeResult, metric: EdgeWeightMetric = 'intersection'): string {
  const data = buildNetworkData(
    result.venn, result.columns.length, result.venn.totalUniqueItems, result.setNames, metric,
  );
  return buildNetworkSvgString(data, metric);
}

/** Binary item × set membership matrix from the result's exclusive items. */
function binaryMatrix(result: AnalyzeResult): number[][] {
  const letters = LETTERS.slice(0, result.columns.length).split('');
  const matrix: number[][] = [];
  for (const [label, items] of result.venn.exclusiveItems) {
    if (label === '') continue; // items in no set — skip
    for (let i = 0; i < items.length; i++) {
      matrix.push(letters.map(l => (label.includes(l) ? 1 : 0)));
    }
  }
  return matrix;
}

/** Item-Share-Distribution histogram SVG. */
export function toShareDistributionSvg(result: AnalyzeResult): string {
  const dist = itemShareDistribution(binaryMatrix(result), result.columns.length);
  return buildShareDistributionSvg(dist);
}
