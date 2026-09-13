export interface QueryHistory {
    id: string;
    collection_id: string;
    query: string;
    answer: string | null;
    response_time_ms: number | null;
    created_at: string;
}

export interface QueryHistoryResponse {
    items: QueryHistory[];
    total: number;
}