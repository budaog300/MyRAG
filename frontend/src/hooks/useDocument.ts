import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { ApiErrorPayload } from "@/types/api";
import type { DocumentRecord } from "@/types/document";
import { fetchDocument, deleteDocument } from "@/api/documents";

export const useDocument = (collectionId?: string, documentId?: string) => {
  const client = useQueryClient();

  const query = useQuery<DocumentRecord, ApiErrorPayload>({
    queryKey: ["documents", collectionId, documentId],
    queryFn: () => fetchDocument(collectionId!, documentId!),
    enabled: Boolean(collectionId && documentId),
  });

  const deleteMutation = useMutation<void, ApiErrorPayload, { documentId: string }>({
    mutationFn: ({ documentId }) => deleteDocument(collectionId!, documentId),
    // onSuccess: () => {
    //   if (!collectionId || !documentId) {
    //     return;
    //   }
    //   client.invalidateQueries({ queryKey: ["documents", collectionId] });
    // },
  });

  return { query, deleteMutation };
};
