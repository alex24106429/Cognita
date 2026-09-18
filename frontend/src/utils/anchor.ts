/**
 * Bidirectional provenance helpers.
 *
 * The backend demands a verbatim `source_citation_anchor` per block. The client
 * independently re-verifies that anchor against the raw text the user submitted
 * so a hallucinated citation is surfaced as "unverified" rather than silently
 * trusted.
 */

export interface AnchorMatch {
  found: boolean;
  start: number;
  end: number;
}

export function normaliseWhitespace(value: string): string {
  return value.replace(/\s+/g, ' ').trim();
}

/** Locate an anchor in the source, tolerating whitespace normalisation drift. */
export function findAnchor(source: string, anchor: string): AnchorMatch {
  if (!source || !anchor) {
    return { found: false, start: -1, end: -1 };
  }

  const exact = source.indexOf(anchor);
  if (exact !== -1) {
    return { found: true, start: exact, end: exact + anchor.length };
  }

  const escaped = anchor.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\s+/g, '\\s+');
  const match = new RegExp(escaped, 'i').exec(source);
  if (match) {
    return { found: true, start: match.index, end: match.index + match[0].length };
  }

  return { found: false, start: -1, end: -1 };
}

export function isAnchorVerified(source: string, anchor: string): boolean {
  return findAnchor(source, anchor).found;
}

/** Count words using whitespace-delimited tokens. */
export function countWords(text: string): number {
  const trimmed = text.trim();
  return trimmed ? trimmed.split(/\s+/).length : 0;
}

/**
 * Heuristic linguistic-complexity predictor (1-10), shown live in the
 * ingestion view before the LLM is ever called.
 */
export function predictComplexity(text: string): number {
  const trimmed = text.trim();
  if (!trimmed) return 1;

  const sentences = trimmed.split(/[.!?]+/).filter((s) => s.trim().length > 0);
  const words = countWords(trimmed);
  const sentenceCount = Math.max(1, sentences.length);
  const averageSentenceLength = words / sentenceCount;

  const longWordRatio =
    trimmed.split(/\s+/).filter((w) => w.replace(/[^A-Za-z]/g, '').length >= 9).length /
    Math.max(1, words);

  const score =
    averageSentenceLength / 3.2 + longWordRatio * 30;

  return Math.min(10, Math.max(1, Math.round(score)));
}
