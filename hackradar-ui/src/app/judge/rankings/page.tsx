import { Suspense } from 'react'
import { PageHeader } from '@/components/layout/PageHeader'
import { RankingsTable } from '@/components/judge/RankingsTable'

export default function RankingsPage() {
  return (
    <div>
      <PageHeader
        title="Rankings"
        description="Leaderboard ranked by overall score for a criteria set."
      />
      <Suspense>
        <RankingsTable />
      </Suspense>
    </div>
  )
}
