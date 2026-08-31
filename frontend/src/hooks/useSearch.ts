import { useMutation } from "@tanstack/react-query";
import type { ApiErrorPayload } from "@/types/api";
import type { SearchRequest, SearchResponse } from "@/types/search";
import { searchCollection } from "@/api/search";

export const useSearch = (collectionId: string) =>
  useMutation<SearchResponse, ApiErrorPayload, SearchRequest>({
    mutationFn: (payload) => searchCollection(collectionId, payload),
  });
