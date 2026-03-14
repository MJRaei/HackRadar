'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { scoreProjects } from '@/lib/api/judging'
import { queryKeys } from '@/lib/queryKeys'
import { toast } from 'sonner'
import type { ScoreRequest } from '@/lib/types'
import { useEffect } from 'react'

export function useScoreMutation() {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (data: ScoreRequest) => scoreProjects(data),
    onSuccess: (scores, variables) => {
      // Invalidate rankings for the criteria set
      queryClient.invalidateQueries({
        queryKey: queryKeys.rankings(variables.criteria_set_id),
      })
      // Invalidate scores for each project
      variables.project_ids.forEach((id) => {
        queryClient.invalidateQueries({ queryKey: queryKeys.projects.scores(id) })
      })
    },
  })

  // Handle beforeunload while scoring is in progress
  useEffect(() => {
    if (!mutation.isPending) return
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault()
    }
    window.addEventListener('beforeunload', handler)
    return () => window.removeEventListener('beforeunload', handler)
  }, [mutation.isPending])

  function score(data: ScoreRequest) {
    return toast.promise(mutation.mutateAsync(data), {
      loading: `Scoring ${data.project_ids.length} project(s)… this may take a few minutes`,
      success: (scores) => `Scored ${scores.length} project(s) successfully`,
      error: (err: Error) => err.message,
    })
  }

  return { score, ...mutation }
}
