import type { QueryHistoryResponse, QueryHistory } from "@/types/query_history";
import client from "./client";

export interface QueryHistoryParams {
    page?: number;
    size?: number;
}

export const fetchQueries = async (
    collectionId: string,
    params: QueryHistoryParams = {},
): Promise<QueryHistoryResponse> => {
    const { data } = await client.get<QueryHistoryResponse>(
        `/collections/${collectionId}/queries`,
        { params },
    );

    return data;
};

export const fetchQuery = async (
    collectionId: string,
    queryId: string,
): Promise<QueryHistory> => {
    const { data } = await client.get<QueryHistory>(
        `/collections/${collectionId}/queries/${queryId}`,
    );

    return data;
};

export const deleteQuery = async (
    collectionId: string,
    queryId: string,
): Promise<void> => {
    await client.delete(
        `/collections/${collectionId}/queries/${queryId}`,
    );
};

export const deleteQueries = async (
    collectionId: string,
): Promise<void> => {
    await client.delete(`/collections/${collectionId}/queries`);
};