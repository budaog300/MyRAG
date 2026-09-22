import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { ApiErrorPayload } from "@/types/api";
import type { SearchRequest, SearchResponse } from "@/types/search";
import { searchCollection } from "@/api/search";

export const useSearch = (collectionId: string) => {
  const queryClient = useQueryClient();

  return useMutation<SearchResponse, ApiErrorPayload, SearchRequest>({
    mutationFn: (payload) => searchCollection(collectionId, payload),
    onSuccess: () => {
      // Search синхронно пишет запись в query history — сбрасываем кеш истории.
      queryClient.invalidateQueries({ queryKey: ["queries", collectionId] });
    },
  });
};
