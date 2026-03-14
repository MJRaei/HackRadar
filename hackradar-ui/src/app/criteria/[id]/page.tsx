'use client'

import { use, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ChevronLeft, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { getCriteriaSet, deleteCriteriaSet } from '@/lib/api/criteria'
import { queryKeys } from '@/lib/queryKeys'
import { PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { formatDate } from '@/lib/utils'

export default function CriteriaSetDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const router = useRouter()
  const queryClient = useQueryClient()
  const [showDelete, setShowDelete] = useState(false)

  const { data: set, isLoading } = useQuery({
    queryKey: queryKeys.criteria.detail(id),
    queryFn: () => getCriteriaSet(id),
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteCriteriaSet(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.criteria.all })
      toast.success('Criteria set deleted')
      router.push('/criteria')
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

  if (!set) return <p className="text-sm text-zinc-500">Criteria set not found.</p>

  const totalWeight = set.criteria.reduce((sum, c) => sum + c.weight, 0)

  return (
    <div>
      <div className="mb-6">
        <Link
          href="/criteria"
          className="inline-flex items-center gap-1 text-xs text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors"
        >
          <ChevronLeft className="w-3.5 h-3.5" />
          Criteria sets
        </Link>
      </div>

      <PageHeader
        title={set.name}
        action={
          <Button variant="destructive" size="sm" onClick={() => setShowDelete(true)}>
            <Trash2 className="w-3.5 h-3.5" />
            Delete
          </Button>
        }
      />

      {set.description && (
        <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-6">{set.description}</p>
      )}

      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 dark:text-zinc-500">
          {set.criteria.length} Criteria
        </h2>
        <span className="text-xs text-zinc-400 dark:text-zinc-500">
          Total weight: {totalWeight.toFixed(2)}
        </span>
      </div>

      <Card className="divide-y divide-zinc-100 dark:divide-zinc-800 mb-6">
        {set.criteria.map((c) => (
          <div key={c.name} className="p-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{c.name}</span>
              <span className="text-xs text-zinc-500 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded-md">
                weight {c.weight}
              </span>
            </div>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">{c.description}</p>
          </div>
        ))}
      </Card>

      <p className="text-xs text-zinc-400 dark:text-zinc-500">Created {formatDate(set.created_at)}</p>

      <ConfirmDialog
        isOpen={showDelete}
        title="Delete criteria set"
        message={`Delete "${set.name}"? This will also remove all associated scores.`}
        onConfirm={() => deleteMutation.mutate()}
        onCancel={() => setShowDelete(false)}
        loading={deleteMutation.isPending}
      />
    </div>
  )
}
