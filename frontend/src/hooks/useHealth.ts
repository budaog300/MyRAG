import { useQuery } from "@tanstack/react-query";
import { fetchHealth } from "@/api/health";
import type { ApiErrorPayload } from "@/types/api";
import type { HealthResponse } from "@/api/health";

export const useHealth = () =>
  useQuery<HealthResponse, ApiErrorPayload>({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: true,
    refetchInterval: 10_000,
    staleTime: 5_000,
    refetchOnWindowFocus: false,
  });
