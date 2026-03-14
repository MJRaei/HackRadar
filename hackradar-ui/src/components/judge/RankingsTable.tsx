'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { listCriteriaSets } from '@/lib/api/criteria'
import { getRankings } from '@/lib/api/judging'
import { queryKeys } from '@/lib/queryKeys'
import { ScoreBar } from '@/components/ui/ScoreBar'
import { Spinner } from '@/components/ui/Spinner'
import { Card } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Trophy } from 'lucide-react'
import { useState } from 'react'

const medals: Record<number, string> = { 1: '🥇', 2: '🥈', 3: '🥉' }

export function RankingsTable() {
  const [selectedCriteria, setSelectedCriteria] = useState<string>('')

  const { data: criteriaData, isLoading: loadingCriteria } = useQuery({
    queryKey: queryKeys.criteria.list(),
    queryFn: () => listCriteriaSets(),
  })

  const { data: rankings, isLoading: loadingRankings } = useQuery({
    queryKey: queryKeys.rankings(selectedCriteria),
    queryFn: () => getRankings(selectedCriteria),
    enabled: !!selectedCriteria,
  })

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <label className="text-sm text-zinc-700 dark:text-zinc-300 shrink-0">Criteria set</label>
        {loadingCriteria ? (
          <Spinner className="w-4 h-4" />
        ) : (
          <select
            value={selectedCriteria}
            onChange={(e) => setSelectedCriteria(e.target.value)}
            className="rounded-lg border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-3 py-1.5 text-sm text-zinc-900 dark:text-zinc-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500"
          >
            <option value="">Select a criteria set…</option>
            {criteriaData?.items.map((cs) => (
              <option key={cs.id} value={cs.id}>
                {cs.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {!selectedCriteria && (
        <EmptyState
          icon={Trophy}
          title="Select a criteria set"
          description="Choose a criteria set above to see the rankings."
        />
      )}

      {selectedCriteria && loadingRankings && (
        <div className="flex justify-center py-12">
          <Spinner className="w-5 h-5" />
        </div>
      )}

      {rankings && rankings.length === 0 && (
        <EmptyState
          icon={Trophy}
          title="No rankings yet"
          description="Score projects with this criteria set to see rankings."
        />
      )}

      {rankings && rankings.length > 0 && (
        <Card className="divide-y divide-zinc-100 dark:divide-zinc-800">
          {rankings.map((r) => (
            <div key={r.project_id} className="flex items-center gap-4 px-4 py-3 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors">
              <span className="w-8 text-center text-sm font-medium text-zinc-500 dark:text-zinc-400 shrink-0">
                {medals[r.rank] ?? `#${r.rank}`}
              </span>
              <div className="flex-1 min-w-0">
                <Link
                  href={`/projects/${r.project_id}`}
                  className="text-sm font-medium text-zinc-900 dark:text-zinc-100 hover:text-violet-700 dark:hover:text-violet-300 transition-colors truncate block"
                >
                  {r.project_name}
                </Link>
                {r.overall_score != null && (
                  <ScoreBar score={r.overall_score} className="mt-1.5 max-w-xs" />
                )}
              </div>
              {r.overall_score != null && (
                <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 shrink-0 tabular-nums">
                  {r.overall_score.toFixed(2)}
                </span>
              )}
            </div>
          ))}
        </Card>
      )}
    </div>
  )
}
