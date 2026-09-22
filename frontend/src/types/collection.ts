export interface CollectionSummary {
  id: string;
  name: string;
  size: number | null;
  distance: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface CollectionDetails extends CollectionSummary {
  vector_repo_info: {
    name: string;
    size: number | null;
    distance: string | null;
    status: string | null;
    points_count: number | null;
  } | null;
  keyword_repo_info: {
    name: string;
    status: string | null;
    points_count: number | null;
  } | null;
}

export interface UpdateCollectionRequest {
  name?: string;
  description?: string;
}
