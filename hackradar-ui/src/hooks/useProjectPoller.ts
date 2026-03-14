'use client'

import { useQuery, useQueryClient } from '@tanstack/react-query'
import { getProject } from '@/lib/api/projects'
import { queryKeys } from '@/lib/queryKeys'
import { isTerminal } from '@/lib/utils'
import { useEffect } from 'react'

export function useProjectPoller(projectId: string, enabled = true) {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: queryKeys.projects.detail(projectId),
    queryFn: () => getProject(projectId),
    enabled,
    refetchInterval: (q) => {
      const status = q.state.data?.status
      return isTerminal(status) ? false : 3_000
    },
  })

  // When the project becomes indexed, invalidate its scores
  useEffect(() => {
    if (query.data?.status === 'indexed') {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.scores(projectId) })
    }
  }, [query.data?.status, projectId, queryClient])

  return query
}
