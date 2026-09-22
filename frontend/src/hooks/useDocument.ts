import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { ApiErrorPayload } from "@/types/api";
import type { DocumentRecord } from "@/types/document";
import { fetchDocument, deleteDocument } from "@/api/documents";

export const useDocument = (collectionId?: string, documentId?: string) => {
  const client = useQueryClient();

  const query = useQuery<DocumentRecord, ApiErrorPayload>({
    queryKey: ["documents", collectionId, "detail", documentId],
    queryFn: () => fetchDocument(collectionId!, documentId!),
    enabled: Boolean(collectionId && documentId),
    staleTime: 10_000,
    refetchOnWindowFocus: false,
    retry: 1,
  });

  const deleteMutation = useMutation<void, ApiErrorPayload, { documentId: string }>({
    mutationFn: ({ documentId: targetId }) => deleteDocument(collectionId!, targetId),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["documents", collectionId] });
      client.invalidateQueries({ queryKey: ["collections", collectionId] });
    },
  });

  return { query, deleteMutation };
};
