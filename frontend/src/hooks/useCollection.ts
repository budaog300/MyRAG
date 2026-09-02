import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { CollectionDetails } from "@/types/collection";
import type { ApiErrorPayload } from "@/types/api";
import { fetchCollection } from "@/api/collections";
import type { CollectionId } from "@/api/collections";

export const useCollection = (collectionId?: CollectionId) => {
  const client = useQueryClient();

  const query = useQuery<CollectionDetails, ApiErrorPayload>({
    queryKey: ["collections", collectionId],
    queryFn: () => fetchCollection(collectionId!),
    enabled: Boolean(collectionId),
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    gcTime: 0,
  });

  return {
    query,
  };
};
