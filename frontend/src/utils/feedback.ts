/**
 * Optional audio-visual feedback helpers for the dopamine checkpoints.
 *
 * Everything here is defensive: browsers without Web Audio, or users who
 * prefer reduced motion, simply get the visual confirmation instead.
 */

export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined' || !window.matchMedia) return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

interface AudioContextConstructor {
  new (): AudioContext;
}

function getAudioContext(): AudioContext | null {
  if (typeof window === 'undefined') return null;
  const Ctor: AudioContextConstructor | undefined =
    window.AudioContext ??
    (window as unknown as { webkitAudioContext?: AudioContextConstructor })
      .webkitAudioContext;
  if (!Ctor) return null;
  try {
    return new Ctor();
  } catch {
    return null;
  }
}

function playTone(frequencies: number[], durationMs: number): void {
  const context = getAudioContext();
  if (!context) return;

  try {
    frequencies.forEach((frequency, index) => {
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      const startAt = context.currentTime + index * (durationMs / 1000) * 0.65;

      oscillator.type = 'sine';
      oscillator.frequency.value = frequency;
      gain.gain.setValueAtTime(0.0001, startAt);
      gain.gain.exponentialRampToValueAtTime(0.06, startAt + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, startAt + durationMs / 1000);

      oscillator.connect(gain);
      gain.connect(context.destination);
      oscillator.start(startAt);
      oscillator.stop(startAt + durationMs / 1000 + 0.02);
    });
  } catch {
    // Audio is a nice-to-have; never let it break the reading flow.
  } finally {
    window.setTimeout(() => {
      void context.close().catch(() => undefined);
    }, durationMs + 400);
  }
}

/** Bright ascending triad — the "you got it" reward. */
export function playSuccessChime(): void {
  if (prefersReducedMotion()) return;
  playTone([523.25, 659.25, 783.99], 180);
}

/** Gentle descending pair — clarification, never punishment. */
export function playClarificationTone(): void {
  if (prefersReducedMotion()) return;
  playTone([392.0, 329.63], 200);
}
