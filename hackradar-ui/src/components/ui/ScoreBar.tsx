import { cn } from '@/lib/utils'

interface ScoreBarProps {
  score: number
  max?: number
  className?: string
}

export function ScoreBar({ score, max = 10, className }: ScoreBarProps) {
  const pct = Math.min(100, Math.max(0, (score / max) * 100))
  const color =
    score >= 8
      ? 'bg-emerald-500'
      : score >= 5
        ? 'bg-amber-500'
        : 'bg-red-500'

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="flex-1 h-1.5 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-300', color)}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs tabular-nums text-zinc-600 dark:text-zinc-400 w-6 text-right">
        {score.toFixed(1)}
      </span>
    </div>
  )
}
