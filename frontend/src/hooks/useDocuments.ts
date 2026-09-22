import { useQuery } from "@tanstack/react-query";
import type { DocumentListResponse, DocumentRecord } from "@/types/document";
import type { ApiErrorPayload } from "@/types/api";
import { fetchDocuments } from "@/api/documents";
import { useDeleteDocumentMutation } from "@/hooks/useDeleteDocument";

export interface UseDocumentsOptions {
  collectionId: string;
  page?: number;
  size?: number;
}

const PROCESSING_STATUSES: DocumentRecord["status"][] = ["pending", "processing"];

export const useDocuments = ({ collectionId, page = 1, size = 10 }: UseDocumentsOptions) => {
  const query = useQuery<DocumentListResponse, ApiErrorPayload>({
    queryKey: ["documents", collectionId, page, size],
    queryFn: () => fetchDocuments(collectionId, { page, size }),
    enabled: Boolean(collectionId),
    refetchOnWindowFocus: false,
    retry: 1,
    // Пока есть документы в очереди/обработке — опрашиваем статусы.
    refetchInterval: (currentQuery) => {
      const items = currentQuery.state.data?.items ?? [];
      const hasProcessing = items.some((item) => PROCESSING_STATUSES.includes(item.status));
      return hasProcessing ? 4000 : false;
    },
  });

  const deleteMutation = useDeleteDocumentMutation(collectionId);

  return { query, deleteMutation };
};
