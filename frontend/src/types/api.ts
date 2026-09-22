export interface ApiErrorResponse {
  detail: string | unknown;
  extra?: Record<string, unknown>;
}

export interface ApiErrorPayload {
  status: number;
  message: string;
  detail?: string;
  extra?: Record<string, unknown>;
}
