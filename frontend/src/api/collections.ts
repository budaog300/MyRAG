import client from "./client";
import type { CollectionSummary, CollectionDetails } from "@/types/collection";

export interface CreateCollectionPayload {
  name: string;
  size?: number;
  distance?: string;
  description?: string;
}

export interface UpdateCollectionPayload {
  name?: string;
  description?: string;
}


export type CollectionId = string;

export const fetchCollections = async (): Promise<CollectionSummary[]> => {
  const { data } = await client.get<CollectionSummary[]>("/collections");
  return data;
};

export const fetchCollection = async (collectionId: CollectionId): Promise<CollectionDetails> => {
  const { data } = await client.get<CollectionDetails>(`/collections/${collectionId}`);
  return data;
};

export const createCollection = async (payload: CreateCollectionPayload): Promise<CollectionDetails> => {
  const { data } = await client.post<CollectionDetails>("/collections", payload);
  return data;
};

export const updateCollection = async (collectionId: CollectionId, payload: UpdateCollectionPayload): Promise<CollectionDetails> => {
  const { data } = await client.patch(`/collections/${collectionId}`, payload);
  return data;
};

export const deleteCollection = async (collectionId: CollectionId): Promise<void> => {
  await client.delete(`/collections/${collectionId}`);
};

export const clearCollection = async (collectionId: CollectionId): Promise<void> => {
  await client.delete(`/collections/${collectionId}/points`);
};
