/**
 * Hierarchical agglomerative clustering: UPGMA (average),
 * complete linkage, and single linkage.
 *
 * Input: symmetric distance matrix (NxN, distances >= 0, diagonal = 0).
 * Output: leaf_order (left-to-right ordering of original indices) and
 *         merges (N-1 entries, each with left, right cluster ids and height).
 *
 * Cluster ids: leaves are [0, N-1]; internal nodes are [N, 2N-2].
 *
 * Tie-breaking: when multiple pairs share the minimum distance, pick the
 * pair with the lowest (i, j) lexicographic order. Within a merged cluster,
 * the lower-indexed leaf is placed on the left so the leaf_order is
 * deterministic.
 */

export type LinkageMethod = 'average' | 'complete' | 'single';

export interface Merge {
  left: number;
  right: number;
  height: number;
  size: number;
}

export interface ClusterOrder {
  leafOrder: number[];
  merges: Merge[];
}

interface Cluster {
  id: number;
  size: number;
  leaves: number[];
}

function combine(d1: number, d2: number, n1: number, n2: number, method: LinkageMethod): number {
  if (method === 'single')   return Math.min(d1, d2);
  if (method === 'complete') return Math.max(d1, d2);
  return (d1 * n1 + d2 * n2) / (n1 + n2);
}

export function clusterSetOrder(D: readonly (readonly number[])[], method: LinkageMethod): ClusterOrder {
  const N = D.length;
  if (N === 0) return { leafOrder: [], merges: [] };
  if (N === 1) return { leafOrder: [0], merges: [] };

  const dist = new Map<number, Map<number, number>>();
  const clusters = new Map<number, Cluster>();
  for (let i = 0; i < N; i++) {
    dist.set(i, new Map());
    clusters.set(i, { id: i, size: 1, leaves: [i] });
  }
  for (let i = 0; i < N; i++) {
    for (let j = i + 1; j < N; j++) {
      dist.get(i)!.set(j, D[i][j]);
      dist.get(j)!.set(i, D[i][j]);
    }
  }

  const merges: Merge[] = [];
  let nextId = N;

  while (clusters.size > 1) {
    let bestI = -1, bestJ = -1, bestD = Infinity;
    const ids = Array.from(clusters.keys());
    for (let a = 0; a < ids.length; a++) {
      for (let b = a + 1; b < ids.length; b++) {
        const i = Math.min(ids[a], ids[b]);
        const j = Math.max(ids[a], ids[b]);
        const d = dist.get(i)!.get(j)!;
        if (
          d < bestD ||
          (d === bestD && (i < bestI || (i === bestI && j < bestJ)))
        ) {
          bestD = d;
          bestI = i;
          bestJ = j;
        }
      }
    }

    const cI = clusters.get(bestI)!;
    const cJ = clusters.get(bestJ)!;
    const newId = nextId++;

    const leftFirst = cI.leaves[0] <= cJ.leaves[0];
    const leaves = leftFirst ? [...cI.leaves, ...cJ.leaves] : [...cJ.leaves, ...cI.leaves];
    const newCluster: Cluster = { id: newId, size: cI.size + cJ.size, leaves };

    const row = new Map<number, number>();
    for (const k of clusters.keys()) {
      if (k === bestI || k === bestJ) continue;
      const dIK = dist.get(bestI)!.get(k)!;
      const dJK = dist.get(bestJ)!.get(k)!;
      const dNew = combine(dIK, dJK, cI.size, cJ.size, method);
      row.set(k, dNew);
      dist.get(k)!.set(newId, dNew);
      dist.get(k)!.delete(bestI);
      dist.get(k)!.delete(bestJ);
    }
    dist.delete(bestI);
    dist.delete(bestJ);
    dist.set(newId, row);

    clusters.delete(bestI);
    clusters.delete(bestJ);
    clusters.set(newId, newCluster);

    merges.push({ left: bestI, right: bestJ, height: bestD, size: newCluster.size });
  }

  const root = Array.from(clusters.values())[0];
  return { leafOrder: root.leaves, merges };
}
