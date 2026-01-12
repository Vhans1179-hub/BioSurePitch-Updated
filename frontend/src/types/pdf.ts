/**
 * TypeScript types for PDF management
 * Matches backend Pydantic models
 */

export interface PDFMetadata {
  name: string;
  display_name: string;
  category: string;
  size_bytes: number;
  modified_time: number;
  hash: string;
  path: string;
}

export interface GeminiFileInfo {
  name: string;
  display_name: string;
  mime_type: string;
  size_bytes: number;
  state: 'PROCESSING' | 'ACTIVE' | 'FAILED';
  uri: string;
}

export interface PDFUploadResponse {
  success: boolean;
  message: string;
  file_metadata?: PDFMetadata;
  gemini_file?: GeminiFileInfo;
}

export interface PDFListResponse {
  pdfs: PDFMetadata[];
  total: number;
  category?: string;
}

export interface GeminiFilesResponse {
  files: GeminiFileInfo[];
  total: number;
}

export interface PDFSyncResponse {
  uploaded: number;
  skipped: number;
  failed: number;
  errors: string[];
  message: string;
}

export interface PDFSource {
  name: string;
  file_id: string;
}

export interface PDFQueryRequest {
  query: string;
  file_names?: string[];
}

export interface PDFQueryResponse {
  success: boolean;
  response: string;
  sources: PDFSource[];
  error?: string;
}

export interface PDFDeleteResponse {
  success: boolean;
  message: string;
  deleted_from_local: boolean;
  deleted_from_gemini: boolean;
}

export type PDFCategory = 'research_papers' | 'policies' | 'contracts' | 'clinical';

export const PDF_CATEGORIES: { value: PDFCategory; label: string }[] = [
  { value: 'research_papers', label: 'Research Papers' },
  { value: 'policies', label: 'Policies' },
  { value: 'contracts', label: 'Contracts' },
  { value: 'clinical', label: 'Clinical Documents' },
];