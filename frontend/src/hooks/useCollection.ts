import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { CollectionDetails } from "@/types/collection";
import type { ApiErrorPayload } from "@/types/api";
import { fetchCollection, clearCollection } from "@/api/collections";
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

  const clearMutation = useMutation<void, ApiErrorPayload, CollectionId>({
    mutationFn: clearCollection,
    onSuccess: () => {
      if (!collectionId) {
        return;
      }

      client.invalidateQueries({
        queryKey: ["documents", collectionId],
      });

      client.invalidateQueries({
        queryKey: ["collections", collectionId],
      });
    },
  });

  return {
    query,
    clearMutation,
  };
};
