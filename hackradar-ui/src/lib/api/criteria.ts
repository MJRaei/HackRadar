import { apiClient } from './client'
import type { CriteriaSetCreate, CriteriaSetListResponse, CriteriaSetResponse } from '../types'

export async function createCriteriaSet(data: CriteriaSetCreate): Promise<CriteriaSetResponse> {
  const res = await apiClient.post<CriteriaSetResponse>('/api/v1/criteria', data)
  return res.data
}

export async function listCriteriaSets(offset = 0, limit = 50): Promise<CriteriaSetListResponse> {
  const res = await apiClient.get<CriteriaSetListResponse>('/api/v1/criteria', {
    params: { offset, limit },
  })
  return res.data
}

export async function getCriteriaSet(id: string): Promise<CriteriaSetResponse> {
  const res = await apiClient.get<CriteriaSetResponse>(`/api/v1/criteria/${id}`)
  return res.data
}

export async function deleteCriteriaSet(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/criteria/${id}`)
}
