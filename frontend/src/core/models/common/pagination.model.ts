/**
 * Modèles TypeScript pour la pagination
 * Correspond aux modèles Pydantic du backend
 */

export interface PaginationInfo {
  total_count: number;
  page: number;
  limit: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: PaginationInfo;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
}