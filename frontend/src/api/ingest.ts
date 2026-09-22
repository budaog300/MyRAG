import client from "./client";

export interface IngestResponse {
  status: "queued" | string;
  count: number;
  document_ids: string[];
}

export interface IngestOptions {
  chunk_size?: number;
  chunk_overlap?: number;
  parent_chunk_size?: number;
  parent_chunk_overlap?: number;
}

export const ingestCollectionDocuments = async (
  collectionId: string,
  files: File[],
  options?: IngestOptions & { onUploadProgress?: (percent: number) => void },
): Promise<IngestResponse> => {
  const form = new FormData();
  files.forEach((file) => form.append("files", file));
  form.append("collection_id", collectionId);

  if (options) {
    Object.entries(options).forEach(([key, value]) => {
      if (value !== undefined && typeof value === "number") {
        form.append(key, value.toString());
      }
    });
  }

  const { data } = await client.post<IngestResponse>("/ingest", form, {
    // Загрузка файлов может занимать время — не рвём запрос по короткому таймауту.
    timeout: 300_000,
    onUploadProgress: options?.onUploadProgress
      ? (progressEvent) => {
          const total = progressEvent.total ?? 0;
          if (total > 0) {
            options.onUploadProgress?.(Math.round((progressEvent.loaded / total) * 100));
          }
        }
      : undefined,
  });
  return data;
};
