export interface SearchRequest {
  query: string
  retrieve_limit: number
  merge_limit: number
  top_k: number
  temperature: number
  max_tokens: number
  only_context: boolean
}

export interface SearchDocument {
  id: string | null
  content: string
  raw_content: string | null
  score: number | null
  metadata: Record<string, unknown>
  source: string | null
  is_parent: boolean
}

export interface SearchResponse {
  answer: string | null
  documents: SearchDocument[]
  count: number
  only_context: boolean
}
