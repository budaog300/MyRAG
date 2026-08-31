import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteCollection, clearCollection } from "@/api/collections";
import type { ApiErrorPayload } from "@/types/api";

export const useDeleteCollection = () => {
  const client = useQueryClient();
  return useMutation<void, ApiErrorPayload, string>({
    mutationFn: (collectionId) => deleteCollection(collectionId),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["collections"] });
    },
  });
};

export const useClearCollection = () => {
  const client = useQueryClient();
  return useMutation<void, ApiErrorPayload, string>({
    mutationFn: (collectionId) => clearCollection(collectionId),
    onSuccess: (_data, collectionId) => {
      client.invalidateQueries({ queryKey: ["documents", collectionId] });
      client.invalidateQueries({ queryKey: ["collections", collectionId] });
    },
  });
};
