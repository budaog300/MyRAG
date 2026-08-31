export interface DocumentRecord {
  filename: string | null
  status: "pending" | "processing" | "ready" | "failed" | "deleted"
  mime_type: string | null
  size_bytes: number
  error_message: string | null
  created_at: string
  updated_at: string
  id: string
  document_id?: string
}

export interface DocumentListResponse {
  items: DocumentRecord[]
  total: number
}
