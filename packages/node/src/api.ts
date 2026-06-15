import {
  calculateVennCounts,
  calculateVennCountsFromAggregated,
  detectDelimiter,
  exportMatrixTsv,
  exportRegionSummaryTsv,
  exportStatisticsTsv,
  getBinaryColumns,
  parseCsvWithDelimiter,
  parseGmt,
  parseGmx,
  type CsvData,
  type VennResult,
} from '@venn-diagram-lab/core';

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
