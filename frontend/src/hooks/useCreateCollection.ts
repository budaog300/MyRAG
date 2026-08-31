import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { CollectionDetails } from "@/types/collection";
import type { ApiErrorPayload } from "@/types/api";
import { createCollection } from "@/api/collections";
import type { CreateCollectionPayload } from "@/api/collections";

export const useCreateCollection = () => {
  const client = useQueryClient();

  return useMutation<CollectionDetails, ApiErrorPayload, CreateCollectionPayload>({
    mutationFn: createCollection,
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["collections"] });
    },
  });
};
