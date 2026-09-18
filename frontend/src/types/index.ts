/**
 * Cognita domain types.
 *
 * These mirror the Pydantic contract in `backend/schemas.py`. Keeping them in
 * lock-step guarantees that a validated backend response renders without
 * defensive reshaping on the client.
 */

export interface MicroQuizOption {
  id: string;
  text: string;
  is_correct: boolean;
  feedback: string;
}

export interface MicroQuiz {
  question: string;
  options: MicroQuizOption[];
  explanation: string;
}

export interface ReadingBlock {
  block_id: number;
  headline: string;
  estimated_reading_seconds: number;
  bionic_chunks: string[];
  key_takeaway: string;
  source_citation_anchor: string;
  quiz?: MicroQuiz | null;
}

export interface TransformationResponse {
  document_title: string;
  overall_read_time_minutes: number;
  difficulty_score: number;
  executive_summary: string;
  blocks: ReadingBlock[];
  nuance_caveats: string[];
}

export type FontFamily =
  | 'OpenDyslexic'
  | 'Atkinson Hyperlegible'
  | 'Inter'
  | 'System';

export type ColorTheme = 'classic' | 'sepia' | 'dark' | 'solarized';

export interface AccessibilitySettings {
  fontSize: number;
  lineHeight: number;
  letterSpacing: number;
  fontFamily: FontFamily;
  colorTheme: ColorTheme;
  bionicMode: boolean;
  focusRuler: boolean;
}

export interface ThemePalette {
  background: string;
  surface: string;
  text: string;
  mutedText: string;
  border: string;
  accent: string;
  shortcutBackground: string;
}

/** Return the concrete colours for a theme key, with a dark-mode safe accent. */
export function resolvePalette(theme: ColorTheme): ThemePalette {
  switch (theme) {
    case 'sepia':
      return {
        background: '#FBF0D9',
        surface: 'rgba(255, 255, 255, 0.72)',
        text: '#433422',
        mutedText: '#6B5B45',
        border: 'rgba(67, 52, 34, 0.18)',
        accent: '#B45309',
        shortcutBackground: 'rgba(180, 83, 9, 0.10)',
      };
    case 'dark':
      return {
        background: '#16181D',
        surface: 'rgba(38, 41, 48, 0.85)',
        text: '#E6E6E6',
        mutedText: '#A9AFB8',
        border: 'rgba(255, 255, 255, 0.14)',
        accent: '#8AB4F8',
        shortcutBackground: 'rgba(138, 180, 248, 0.14)',
      };
    case 'solarized':
      return {
        background: '#FDF6E3',
        surface: 'rgba(255, 255, 255, 0.70)',
        text: '#073642',
        mutedText: '#4A6572',
        border: 'rgba(7, 54, 66, 0.16)',
        accent: '#268BD2',
        shortcutBackground: 'rgba(38, 139, 210, 0.12)',
      };
    case 'classic':
    default:
      return {
        background: '#FFFFFF',
        surface: 'rgba(248, 249, 250, 0.92)',
        text: '#1A1B1E',
        mutedText: '#5A6068',
        border: 'rgba(0, 0, 0, 0.12)',
        accent: '#4C6EF5',
        shortcutBackground: 'rgba(76, 110, 245, 0.10)',
      };
  }
}

/** CSS font stack for the selected accessibility font. */
export function resolveFontStack(fontFamily: FontFamily): string {
  switch (fontFamily) {
    case 'OpenDyslexic':
      return "'OpenDyslexic', 'Atkinson Hyperlegible', system-ui, sans-serif";
    case 'Atkinson Hyperlegible':
      return "'Atkinson Hyperlegible', 'Inter', system-ui, sans-serif";
    case 'Inter':
      return "'Inter', system-ui, sans-serif";
    case 'System':
    default:
      return 'system-ui, -apple-system, "Segoe UI", sans-serif';
  }
}
