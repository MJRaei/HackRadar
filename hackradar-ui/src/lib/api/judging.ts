import { apiClient } from './client'
import type {
  CategorizationRequest,
  CategorizationResponse,
  RankedProject,
  ScoreRequest,
  ScoreResponse,
} from '../types'

export async function scoreProjects(data: ScoreRequest): Promise<ScoreResponse[]> {
  const res = await apiClient.post<ScoreResponse[]>('/api/v1/judge/score', data)
  return res.data
}

export async function getProjectScores(projectId: string): Promise<ScoreResponse[]> {
  const res = await apiClient.get<ScoreResponse[]>(`/api/v1/judge/score/${projectId}`)
  return res.data
}

export async function getRankings(criteriaSetId: string): Promise<RankedProject[]> {
  const res = await apiClient.get<RankedProject[]>('/api/v1/judge/rankings', {
    params: { criteria_set_id: criteriaSetId },
  })
  return res.data
}

export async function categorizeProjects(
  data: CategorizationRequest
): Promise<CategorizationResponse> {
  const res = await apiClient.post<CategorizationResponse>('/api/v1/judge/categorize', data)
  return res.data
}
