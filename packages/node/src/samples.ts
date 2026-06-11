import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const SAMPLES_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'assets', 'samples');

const SAMPLE_FILES: Record<string, string> = {
  dataset_real_cancer_drivers_4: 'dataset_real_cancer_drivers_4.tsv',
  dataset_real_msigdb_cancer_pathways: 'dataset_real_msigdb_cancer_pathways.tsv',
  dataset_real_msigdb_immune_pathways: 'dataset_real_msigdb_immune_pathways.tsv',
  dataset_mock_gene_sets: 'dataset_mock_gene_sets.csv',
  dataset_mock_streaming_platforms: 'dataset_mock_streaming_platforms.csv',
};

export function listSamples(): string[] {
  return Object.keys(SAMPLE_FILES);
}

export function loadSampleText(name: string): string {
  const file = SAMPLE_FILES[name];
  if (!file) throw new Error(`Unknown sample: ${name}`);
  return readFileSync(join(SAMPLES_DIR, file), 'utf8');
}
