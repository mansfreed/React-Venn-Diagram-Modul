# venn-diagram-lab (Node)

Headless Venn diagram analysis for Node.js — the JavaScript/TypeScript companion to the
[Venn Diagram Lab](https://venndiagramlab.org/) web tool, sharing the same core code so the
TSV exports are **byte-identical** to the web tool and to the Python (`venn-diagram-lab`) and
R (`vennDiagramLab`) packages.

## Install
```bash
npm install venn-diagram-lab
```

## Library
```ts
import { analyzeCsvText, toRegionSummaryTsv, loadSampleText } from 'venn-diagram-lab';

const result = analyzeCsvText(loadSampleText('dataset_real_cancer_drivers_4'));
console.log(toRegionSummaryTsv(result));
```

## CLI
```bash
vdl analyze genes.tsv --region-summary summary.tsv
```

Phase 1 covers analysis + Region Summary TSV. Matrix/Statistics exports, SVG/UpSet/Network
rendering, and PDF reports land in later releases.
