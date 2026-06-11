import { describe, expect, it } from 'vitest';
import { listSamples, loadSampleText } from '../src/samples.ts';

describe('samples', () => {
  it('lists the five bundled sample ids', () => {
    expect(listSamples().sort()).toEqual([
      'dataset_mock_gene_sets',
      'dataset_mock_streaming_platforms',
      'dataset_real_cancer_drivers_4',
      'dataset_real_msigdb_cancer_pathways',
      'dataset_real_msigdb_immune_pathways',
    ]);
  });

  it('loads a sample as raw text with a header line', () => {
    const text = loadSampleText('dataset_real_cancer_drivers_4');
    expect(text.split('\n')[0]).toContain('Vogelstein');
  });

  it('throws on an unknown sample', () => {
    expect(() => loadSampleText('nope')).toThrow(/unknown sample/i);
  });
});
