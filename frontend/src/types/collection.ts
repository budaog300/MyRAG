export interface CollectionSummary {
  id: string
  name: string
  size: number
  distance: string
  description: string
  created_at: string
  updated_at: string
}

export interface CollectionDetails extends CollectionSummary {
  vector_repo_info: {
    size: number
    distance: string
    status: string
    points_count: number
  }
  keyword_repo_info: {
    status: string
    points_count: number
  }
}
