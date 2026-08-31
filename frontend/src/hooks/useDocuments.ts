import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { DocumentListResponse } from "@/types/document";
import type { ApiErrorPayload } from "@/types/api";
import { fetchDocuments, deleteDocument } from "@/api/documents";

export interface UseDocumentsOptions {
  collectionId: string;
  page?: number;
  size?: number;
}

export const useDocuments = ({ collectionId, page = 1, size = 10 }: UseDocumentsOptions) => {
  const client = useQueryClient();

  const query = useQuery<DocumentListResponse, ApiErrorPayload>({
    queryKey: ["documents", collectionId, page, size],
    queryFn: () => fetchDocuments(collectionId, { page, size }),
    enabled: Boolean(collectionId),
  });

  const deleteMutation = useMutation<void, ApiErrorPayload, { documentId: string }>({
    mutationFn: ({ documentId }) => deleteDocument(collectionId, documentId),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["documents", collectionId] });
    },
  });

  return { query, deleteMutation };
};
