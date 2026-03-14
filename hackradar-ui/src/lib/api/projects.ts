import { apiClient } from './client'
import type { BulkUploadResponse, ProjectCreate, ProjectListResponse, ProjectResponse } from '../types'

export async function createProject(data: ProjectCreate): Promise<ProjectResponse> {
  const res = await apiClient.post<ProjectResponse>('/api/v1/projects', data)
  return res.data
}

export async function listProjects(offset = 0, limit = 50): Promise<ProjectListResponse> {
  const res = await apiClient.get<ProjectListResponse>('/api/v1/projects', {
    params: { offset, limit },
  })
  return res.data
}

export async function getProject(id: string): Promise<ProjectResponse> {
  const res = await apiClient.get<ProjectResponse>(`/api/v1/projects/${id}`)
  return res.data
}

export async function deleteProject(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/projects/${id}`)
}

export async function bulkUploadProjects(file: File): Promise<BulkUploadResponse> {
  const form = new FormData()
  form.append('file', file)
  const res = await apiClient.post<BulkUploadResponse>('/api/v1/projects/bulk-upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}
