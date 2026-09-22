import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { ApiErrorPayload } from "@/types/api";
import { deleteDocument } from "@/api/documents";

/** Общая мутация удаления документа (используется из списка и карточки). */
export const useDeleteDocumentMutation = (collectionId: string) => {
  const client = useQueryClient();

  return useMutation<void, ApiErrorPayload, { documentId: string }>({
    mutationFn: ({ documentId }) => deleteDocument(collectionId, documentId),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["documents", collectionId] });
      client.invalidateQueries({ queryKey: ["collections", collectionId] });
    },
  });
};
