import client from "./client";

export interface HealthResponse {
  status: string;
}

export const fetchHealth = async (): Promise<HealthResponse> => {
  const { data } = await client.get<HealthResponse>("/health");
  return data;
};
