'use client'

import Link from 'next/link'
import { ExternalLink, Loader2 } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { StatusBadge } from '@/components/ui/Badge'
import { ScoreBar } from '@/components/ui/ScoreBar'
import { useProjectPoller } from '@/hooks/useProjectPoller'
import { formatDate, isTerminal } from '@/lib/utils'
import type { ProjectResponse } from '@/lib/types'

interface ProjectCardProps {
  project: ProjectResponse
}

export function ProjectCard({ project: initial }: ProjectCardProps) {
  const needsPolling = !isTerminal(initial.status)
  const { data: project = initial } = useProjectPoller(initial.id, needsPolling)

  const active = !isTerminal(project.status)

  return (
    <Card className="p-4 hover:shadow-md transition-shadow group">
      <Link href={`/projects/${project.id}`} className="block">
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 min-w-0">
            {active && <Loader2 className="w-3.5 h-3.5 text-violet-500 animate-spin shrink-0" />}
            <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-100 truncate group-hover:text-violet-700 dark:group-hover:text-violet-300 transition-colors">
              {project.name}
            </h3>
          </div>
          <StatusBadge status={project.status} className="shrink-0" />
        </div>

        <div className="flex items-center gap-1 mb-3">
          <span className="text-xs text-zinc-400 dark:text-zinc-500 truncate">
            {project.github_url.replace('https://github.com/', '')}
          </span>
          <ExternalLink className="w-3 h-3 text-zinc-300 dark:text-zinc-600 shrink-0" />
        </div>

        {project.summary && (
          <p className="text-xs text-zinc-500 dark:text-zinc-400 line-clamp-2 mb-3">
            {project.summary}
          </p>
        )}

        {project.status === 'failed' && project.error_message && (
          <p className="text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950 rounded-lg px-2 py-1 mb-3 line-clamp-2">
            {project.error_message}
          </p>
        )}

        <div className="flex items-center justify-between text-xs text-zinc-400 dark:text-zinc-500">
          <span>{formatDate(project.created_at)}</span>
        </div>
      </Link>
    </Card>
  )
}

interface ProjectScoreCardProps {
  project: ProjectResponse
  overallScore?: number | null
}

export function ProjectScoreCard({ project, overallScore }: ProjectScoreCardProps) {
  return (
    <Card className="p-4">
      <div className="flex items-center justify-between gap-2 mb-1">
        <Link
          href={`/projects/${project.id}`}
          className="text-sm font-medium text-zinc-900 dark:text-zinc-100 hover:text-violet-700 dark:hover:text-violet-300 transition-colors truncate"
        >
          {project.name}
        </Link>
        <StatusBadge status={project.status} />
      </div>
      {overallScore != null && <ScoreBar score={overallScore} className="mt-2" />}
    </Card>
  )
}
