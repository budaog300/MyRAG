import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ingestCollectionDocuments } from "@/api/ingest";
import type { IngestResponse } from "@/api/ingest";
import type { ApiErrorPayload } from "@/types/api";

export interface IngestPayload {
  collectionId: string;
  files: File[];
  options?: Record<string, unknown>;
}

export const useIngest = () => {
  const client = useQueryClient();

  const mutation = useMutation<
    IngestResponse,
    ApiErrorPayload,
    IngestPayload
  >({
    mutationFn: ({ collectionId, files, options }) => ingestCollectionDocuments(collectionId, files, options),
    onSuccess: (_data, variables) => {
      client.invalidateQueries({ queryKey: ["documents", variables.collectionId] });
    },
  });

  return mutation;
};
