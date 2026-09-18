import type { TransformationResponse } from '../types';

/**
 * Backend client.
 *
 * The base URL is configurable through `VITE_API_URL` so the same build works
 * locally (http://localhost:8000) and inside the docker-compose topology
 * (http://backend:8000).
 */
export const API_BASE_URL: string = (
  import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
).replace(/\/+$/, '');

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

interface ErrorPayload {
  detail?: string;
}

/**
 * POST /api/transform
 *
 * Maps transport and provider failures onto human-readable, actionable
 * messages (rate limits, missing keys, unvalidated model output).
 */
export async function transformAcademicText(
  rawText: string,
  signal?: AbortSignal
): Promise<TransformationResponse> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/api/transform`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_text: rawText }),
      signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error;
    }
    throw new ApiError(
      `Cannot reach the Cognita backend at ${API_BASE_URL}. Start the FastAPI server and try again.`,
      0
    );
  }

  if (!response.ok) {
    let detail = `Transformation failed with status ${response.status}.`;
    try {
      const payload = (await response.json()) as ErrorPayload;
      if (payload?.detail) detail = payload.detail;
    } catch {
      // Non-JSON error body - keep the status-based message.
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as TransformationResponse;
}

export interface HealthResponse {
  status: string;
  model: string;
  base_url: string;
  api_key_configured: boolean;
}

export async function checkHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/health`, { signal });
  if (!response.ok) {
    throw new ApiError('Health check failed.', response.status);
  }
  return (await response.json()) as HealthResponse;
}
