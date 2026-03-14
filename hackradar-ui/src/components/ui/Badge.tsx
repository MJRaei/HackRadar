import { cn } from '@/lib/utils'
import type { ProjectStatus } from '@/lib/types'

const statusStyles: Record<ProjectStatus, string> = {
  pending: 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400',
  cloning: 'bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300',
  indexing: 'bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-300',
  indexed: 'bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300',
  failed: 'bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300',
}

const statusLabels: Record<ProjectStatus, string> = {
  pending: 'Pending',
  cloning: 'Cloning',
  indexing: 'Indexing',
  indexed: 'Indexed',
  failed: 'Failed',
}

const activePulse: Set<ProjectStatus> = new Set(['cloning', 'indexing'])

interface StatusBadgeProps {
  status: ProjectStatus
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const pulse = activePulse.has(status)
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium',
        statusStyles[status],
        className
      )}
    >
      {pulse && (
        <span className="relative flex h-1.5 w-1.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 bg-current" />
          <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-current" />
        </span>
      )}
      {statusLabels[status]}
    </span>
  )
}

interface ScoreBadgeProps {
  score: number
  className?: string
}

export function ScoreBadge({ score, className }: ScoreBadgeProps) {
  const variant =
    score >= 8
      ? 'bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300'
      : score >= 5
        ? 'bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-300'
        : 'bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300'

  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
        variant,
        className
      )}
    >
      {score.toFixed(1)}
    </span>
  )
}
