import {
  calculateVennCounts,
  detectDelimiter,
  exportRegionSummaryTsv,
  getBinaryColumns,
  parseCsvWithDelimiter,
  type CsvData,
  type VennResult,
} from '@venn-diagram-lab/core';

export interface AnalyzeResult {
  csv: CsvData;
  columns: number[];
  setNames: string[];
  venn: VennResult;
}

/** Parse raw CSV/TSV text, auto-detect the binary set columns, and compute Venn counts. */
export function analyzeCsvText(text: string): AnalyzeResult {
  const delimiter = detectDelimiter(text);
  const csv = parseCsvWithDelimiter(text, delimiter, true);
  const columns = getBinaryColumns(csv);
  const setNames = columns.map(i => csv.headers[i]);
  const venn = calculateVennCounts(csv, columns);
  return { csv, columns, setNames, venn };
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
