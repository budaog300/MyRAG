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
  options?: IngestOptions,
): Promise<IngestResponse> => {
  const form = new FormData();
  files.forEach((file) => form.append("files", file));
  form.append("collection_id", collectionId);

  if (options) {
    Object.entries(options).forEach(([key, value]) => {
      if (value !== undefined) {
        form.append(key, value.toString());
      }
    });
  }

  const { data } = await client.post<IngestResponse>("/ingest", form);
  return data;
};
