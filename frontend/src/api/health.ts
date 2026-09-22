import client from "./client";

export interface HealthResponse {
  status: string;
  services: Record<string, boolean>;
}

export const fetchHealth = async (): Promise<HealthResponse> => {
  const { data } = await client.get<HealthResponse>("/health");
  return data;
};
