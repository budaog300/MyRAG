import { useQuery } from "@tanstack/react-query";
import type { CollectionSummary } from "@/types/collection";
import type { ApiErrorPayload } from "@/types/api";
import { fetchCollections } from "@/api/collections";

export const useCollections = () =>
  useQuery<CollectionSummary[], ApiErrorPayload>({
    queryKey: ["collections"],
    queryFn: fetchCollections,
    staleTime: 1000 * 60 * 2,
    refetchOnWindowFocus: false,
  });
