'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, ListChecks } from 'lucide-react'
import { listCriteriaSets } from '@/lib/api/criteria'
import { queryKeys } from '@/lib/queryKeys'
import { PageHeader } from '@/components/layout/PageHeader'
import { CriteriaSetCard } from '@/components/criteria/CriteriaSetCard'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { EmptyState } from '@/components/ui/EmptyState'

export default function CriteriaPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.criteria.list(),
    queryFn: () => listCriteriaSets(),
  })

  return (
    <div>
      <PageHeader
        title="Criteria sets"
        description="Define what matters when judging submissions."
        action={
          <Link href="/criteria/new">
            <Button size="sm">
              <Plus className="w-3.5 h-3.5" />
              New criteria set
            </Button>
          </Link>
        }
      />

      {isLoading && (
        <div className="flex justify-center py-16">
          <Spinner className="w-5 h-5" />
        </div>
      )}
      {error && <p className="text-sm text-red-600 dark:text-red-400">Failed to load criteria sets.</p>}

      {data && data.items.length === 0 && (
        <EmptyState
          icon={ListChecks}
          title="No criteria sets yet"
          description="Create a criteria set to start scoring projects."
          action={
            <Link href="/criteria/new">
              <Button size="sm">
                <Plus className="w-3.5 h-3.5" />
                New criteria set
              </Button>
            </Link>
          }
        />
      )}

      {data && data.items.length > 0 && (
        <>
          <p className="text-xs text-zinc-400 dark:text-zinc-500 mb-4">
            {data.total} criteria set{data.total !== 1 ? 's' : ''}
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.items.map((set) => (
              <CriteriaSetCard key={set.id} set={set} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
