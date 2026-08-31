import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { CollectionDetails } from "@/types/collection";
import type { ApiErrorPayload } from "@/types/api";
import { fetchCollection, deleteCollection, clearCollection } from "@/api/collections";
import type { CollectionId } from "@/api/collections";

export const useCollection = (collectionId?: CollectionId) => {
  const client = useQueryClient();

  const query = useQuery<CollectionDetails, ApiErrorPayload>({
    queryKey: ["collections", collectionId],
    queryFn: () => fetchCollection(collectionId!),
    enabled: Boolean(collectionId),
  });

  const deleteMutation = useMutation<void, ApiErrorPayload, CollectionId>({
    mutationFn: deleteCollection,
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["collections"] });
    },
  });

  const clearMutation = useMutation<void, ApiErrorPayload, CollectionId>({
    mutationFn: clearCollection,
    onSuccess: () => {
      if (!collectionId) {
        return;
      }
      client.invalidateQueries({ queryKey: ["documents", collectionId] });
      client.invalidateQueries({ queryKey: ["collections", collectionId] });
    },
  });

  return { query, deleteMutation, clearMutation };
};
