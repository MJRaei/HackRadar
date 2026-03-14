export type ProjectStatus = 'pending' | 'cloning' | 'indexing' | 'indexed' | 'failed'

export interface ProjectResponse {
  id: string
  name: string
  github_url: string
  summary: string | null
  readme: string | null
  local_path: string | null
  status: ProjectStatus
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface ProjectListResponse {
  items: ProjectResponse[]
  total: number
}

export interface ProjectCreate {
  name: string
  github_url: string
  summary?: string
}

export interface Criterion {
  name: string
  description: string
  weight: number
}

export interface CriteriaSetResponse {
  id: string
  name: string
  description: string | null
  criteria: Criterion[]
  created_at: string
  updated_at: string
}

export interface CriteriaSetCreate {
  name: string
  description?: string
  criteria: Criterion[]
}

export interface CriteriaSetListResponse {
  items: CriteriaSetResponse[]
  total: number
}

export interface CriterionScore {
  score: number
  rationale: string
}

export interface ScoreRequest {
  project_ids: string[]
  criteria_set_id: string
}

export interface ScoreResponse {
  id: string
  project_id: string
  criteria_set_id: string
  criterion_scores: Record<string, CriterionScore>
  overall_score: number | null
  created_at: string
  updated_at: string
}

export interface RankedProject {
  rank: number
  project_id: string
  project_name: string
  overall_score: number | null
  criteria_set_id: string
}

export interface CategorizationRequest {
  project_ids: string[]
  categories?: string[]
}

export interface ProjectCategoryAssignment {
  project_id: string
  project_name: string
  category: string
}

export interface CategorizationResponse {
  assignments: ProjectCategoryAssignment[]
  categories_created: string[]
}
