import client from "./client";
import type { SearchRequest, SearchResponse } from "@/types/search";

export const searchCollection = async (
  collectionId: string,
  payload: SearchRequest,
): Promise<SearchResponse> => {
  const { data } = await client.post<SearchResponse>(`/collections/${collectionId}/search`, payload);
  return data;
};
