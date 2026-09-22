export interface DocumentRecord {
  id: string;
  filename: string | null;
  status: "pending" | "processing" | "ready" | "failed" | "deleted" | "deleting";
  mime_type: string | null;
  size_bytes: number | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  items: DocumentRecord[];
  total: number;
}
