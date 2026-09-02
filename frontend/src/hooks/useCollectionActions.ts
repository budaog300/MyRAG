import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteCollection, clearCollection, updateCollection } from "@/api/collections";
import type { UpdateCollectionPayload, CollectionId } from "@/api/collections";
import type { ApiErrorPayload } from "@/types/api";
import type { CollectionDetails } from "@/types/collection";


export const useUpdateCollection = () => {
  const client = useQueryClient();

  return useMutation<
    CollectionDetails,
    ApiErrorPayload,
    {
      collectionId: CollectionId;
      payload: UpdateCollectionPayload;
    }
  >({
    mutationFn: ({ collectionId, payload }) =>
      updateCollection(collectionId, payload),

    onSuccess: (data, { collectionId }) => {
      client.setQueryData(
        ["collections", collectionId],
        data,
      );

      client.invalidateQueries({
        queryKey: ["collections"],
        exact: true,
      });
    },
  });
};

export const useDeleteCollection = () => {
  const client = useQueryClient();

  return useMutation<void, ApiErrorPayload, CollectionId>({
    mutationFn: (collectionId) => deleteCollection(collectionId),
    onSuccess: () => {
      client.invalidateQueries({
        queryKey: ["collections"],
        exact: true,
      });
    },
  });
};

export const useClearCollection = () => {
  const client = useQueryClient();
  return useMutation<void, ApiErrorPayload, CollectionId>({
    mutationFn: (collectionId) => clearCollection(collectionId),
    onSuccess: (_data, collectionId) => {
      client.invalidateQueries({ queryKey: ["documents", collectionId] });
      client.invalidateQueries({ queryKey: ["collections", collectionId] });
    },
  });
};
