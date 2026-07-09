export interface JobExtractionResponse {
  id: string;
  job_title: string;
  required_stack: string[];
  location: string;
  salary_min: number | null;
  salary_max: number | null;
  availability: string | null;
  seniority_level: string | null;
  remote_policy: string | null;
  key_responsibilities: string[];
  nice_to_have: string[];
  confidence_score: number;
  created_at: string;
}

export interface JobExtractionDetailResponse
  extends JobExtractionResponse {
  source_type: string;
  source_url: string | null;
}

export interface ExtractionListItem {
  id: string;
  job_title: string;
  required_stack: string[];
  location: string;
  salary_min: number | null;
  salary_max: number | null;
  confidence_score: number;
  created_at: string;
}

export interface ExtractionListResponse {
  items: ExtractionListItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface ErrorDetail {
  code: string;
  message: string;
  details: Record<string, unknown>;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ErrorDetail;
}

export interface ExtractRequest {
  source: 'url' | 'pdf';
  url?: string;
  file?: File;
}
