import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ingestCollectionDocuments } from "@/api/ingest";
import type { IngestResponse, IngestOptions } from "@/api/ingest";
import type { ApiErrorPayload } from "@/types/api";

export interface IngestPayload {
  collectionId: string;
  files: File[];
  options?: IngestOptions & { onUploadProgress?: (percent: number) => void };
}

export const useIngest = () => {
  const client = useQueryClient();

  return useMutation<IngestResponse, ApiErrorPayload, IngestPayload>({
    mutationFn: ({ collectionId, files, options }) => ingestCollectionDocuments(collectionId, files, options),
    onSuccess: (_data, variables) => {
      client.invalidateQueries({ queryKey: ["documents", variables.collectionId] });
      client.invalidateQueries({ queryKey: ["collections", variables.collectionId] });
    },
  });

};
