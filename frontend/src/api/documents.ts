import client from "./client";
import type { DocumentListResponse } from "@/types/document";

export interface DocumentQueryParams {
  page?: number;
  size?: number;
}

export const fetchDocuments = async (
  collectionId: string,
  params: DocumentQueryParams = {},
): Promise<DocumentListResponse> => {
  const { data } = await client.get<DocumentListResponse>(
    `/collections/${collectionId}/documents`,
    { params },
  );
  return data;
};

export const fetchDocument = async (
  collectionId: string,
  documentId: string,
): Promise<DocumentListResponse["items"][number]> => {
  const { data } = await client.get<
    DocumentListResponse["items"][number]
  >(`/collections/${collectionId}/documents/${documentId}`);
  return data;
};

export const deleteDocument = async (
  collectionId: string,
  documentId: string,
): Promise<void> => {
  await client.delete(`/collections/${collectionId}/documents/${documentId}`);
};
