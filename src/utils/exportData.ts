export * from '@venn-diagram-lab/core';

/** Download a text file with BOM for Excel UTF-8 compatibility */
export function downloadFile(content: string, filename: string, mimeType = 'text/tab-separated-values'): void {
  const blob = new Blob(['﻿' + content], { type: `${mimeType};charset=utf-8` });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
