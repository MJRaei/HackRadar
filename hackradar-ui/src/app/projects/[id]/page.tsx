'use client'

import { use, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ExternalLink, Trash2, ChevronLeft } from 'lucide-react'
import { toast } from 'sonner'
import { getProjectScores } from '@/lib/api/judging'
import { deleteProject } from '@/lib/api/projects'
import { queryKeys } from '@/lib/queryKeys'
import { useProjectPoller } from '@/hooks/useProjectPoller'
import { PageHeader } from '@/components/layout/PageHeader'
import { StatusBadge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import { ScoreBar } from '@/components/ui/ScoreBar'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { formatDate, isTerminal } from '@/lib/utils'

export default function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const router = useRouter()
  const queryClient = useQueryClient()
  const [showDelete, setShowDelete] = useState(false)

  const { data: project, isLoading } = useProjectPoller(id, true)

  const { data: scores } = useQuery({
    queryKey: queryKeys.projects.scores(id),
    queryFn: () => getProjectScores(id),
    enabled: project?.status === 'indexed',
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteProject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all })
      toast.success('Project deleted')
      router.push('/projects')
    },
    onError: (err: Error) => toast.error(err.message),
  })

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner className="w-5 h-5" />
      </div>
    )
  }

  if (!project) {
    return <p className="text-sm text-zinc-500">Project not found.</p>
  }

  return (
    <div>
      <div className="mb-6">
        <Link
          href="/projects"
          className="inline-flex items-center gap-1 text-xs text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors"
        >
          <ChevronLeft className="w-3.5 h-3.5" />
          Projects
        </Link>
      </div>

      <PageHeader
        title={project.name}
        action={
          <Button variant="destructive" size="sm" onClick={() => setShowDelete(true)}>
            <Trash2 className="w-3.5 h-3.5" />
            Delete
          </Button>
        }
      />

      {/* Meta */}
      <Card className="p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-zinc-500 dark:text-zinc-400">Status</span>
            <StatusBadge status={project.status} />
          </div>
          <a
            href={project.github_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-violet-600 dark:text-violet-400 hover:underline"
          >
            {project.github_url.replace('https://github.com/', '')}
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
          <span className="text-zinc-400 dark:text-zinc-500 text-xs">
            Added {formatDate(project.created_at)}
          </span>
        </div>

        {!isTerminal(project.status) && (
          <div className="mt-3 flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
            <Spinner className="w-3.5 h-3.5" />
            {project.status === 'cloning' && 'Cloning repository…'}
            {project.status === 'indexing' && 'Indexing codebase into Qdrant…'}
            {project.status === 'pending' && 'Waiting to start…'}
          </div>
        )}

        {project.status === 'failed' && project.error_message && (
          <div className="mt-3 text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950 rounded-lg px-3 py-2">
            {project.error_message}
          </div>
        )}
      </Card>

      {project.summary && (
        <div className="mb-6">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
            Summary
          </h2>
          <p className="text-sm text-zinc-700 dark:text-zinc-300">{project.summary}</p>
        </div>
      )}

      {/* Scores */}
      {scores && scores.length > 0 && (
        <div className="mb-6">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-3">
            Scores
          </h2>
          <div className="space-y-4">
            {scores.map((score) => (
              <Card key={score.id} className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs text-zinc-500 dark:text-zinc-400">
                    Criteria set: {score.criteria_set_id.slice(0, 8)}…
                  </span>
                  {score.overall_score != null && (
                    <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                      {score.overall_score.toFixed(2)} / 10
                    </span>
                  )}
                </div>
                {score.overall_score != null && (
                  <ScoreBar score={score.overall_score} className="mb-4" />
                )}
                <div className="space-y-3">
                  {Object.entries(score.criterion_scores).map(([criterion, cs]) => (
                    <div key={criterion}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-zinc-700 dark:text-zinc-300">
                          {criterion}
                        </span>
                      </div>
                      <ScoreBar score={cs.score} className="mb-1" />
                      <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
                        {cs.rationale}
                      </p>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* README */}
      {project.readme && (
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-3">
            README
          </h2>
          <Card className="p-4">
            <pre className="text-xs text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap font-mono leading-relaxed overflow-auto max-h-96">
              {project.readme}
            </pre>
          </Card>
        </div>
      )}

      <ConfirmDialog
        isOpen={showDelete}
        title="Delete project"
        message={`Are you sure you want to delete "${project.name}"? This will also remove all scores and the Qdrant collection.`}
        onConfirm={() => deleteMutation.mutate()}
        onCancel={() => setShowDelete(false)}
        loading={deleteMutation.isPending}
      />
    </div>
  )
}
