import React from 'react';

/**
 * Bionic salience formatting.
 *
 * Bolding the first ~45% of every word creates artificial fixation points that
 * reduce visual saccade latency and line-skipping for dyslexic and ADHD
 * readers. Whitespace and punctuation are preserved exactly so that the text
 * remains indistinguishable from the original when copied or screen-read.
 */

/** Matches leading punctuation, the alphanumeric core, and trailing punctuation. */
const TOKEN_RE = /^([^\p{L}\p{N}]*)(.*?)([^\p{L}\p{N}]*)$/u;

function boldPrefixLength(core: string): number {
  if (core.length <= 1) return core.length;
  if (core.length <= 3) return 1;
  if (core.length <= 6) return 2;
  return Math.min(core.length - 1, Math.max(3, Math.round(core.length * 0.45)));
}

export function formatBionic(text: string): React.ReactNode[] {
  if (!text) return [];

  // Keep whitespace runs so line breaks and multiple spaces survive rendering.
  return text.split(/(\s+)/).map((token, index) => {
    if (!token) return null;
    if (/^\s+$/.test(token)) {
      return <React.Fragment key={`ws-${index}`}>{token}</React.Fragment>;
    }

    const match = TOKEN_RE.exec(token);
    if (!match) {
      return <React.Fragment key={`txt-${index}`}>{token}</React.Fragment>;
    }

    const [, leading, core, trailing] = match;
    if (!core) {
      return <React.Fragment key={`punct-${index}`}>{token}</React.Fragment>;
    }

    const prefix = core.slice(0, boldPrefixLength(core));
    const suffix = core.slice(prefix.length);

    return (
      <React.Fragment key={`word-${index}`}>
        {leading}
        {prefix ? <strong className="cognita-bionic-strong">{prefix}</strong> : null}
        {suffix}
        {trailing}
      </React.Fragment>
    );
  });
}

interface BionicTextProps {
  text: string;
  enabled: boolean;
  className?: string;
}

/** Convenience wrapper that toggles bionic rendering for a whole paragraph. */
export const BionicText: React.FC<BionicTextProps> = ({ text, enabled, className }) => (
  <p className={`cognita-chunk ${className ?? ''}`.trim()}>
    {enabled ? formatBionic(text) : text}
  </p>
);
