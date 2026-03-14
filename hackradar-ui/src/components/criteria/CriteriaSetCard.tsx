import Link from 'next/link'
import { Card } from '@/components/ui/Card'
import { formatDate } from '@/lib/utils'
import type { CriteriaSetResponse } from '@/lib/types'

export function CriteriaSetCard({ set }: { set: CriteriaSetResponse }) {
  return (
    <Card className="p-4 hover:shadow-md transition-shadow group">
      <Link href={`/criteria/${set.id}`} className="block">
        <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-100 group-hover:text-violet-700 dark:group-hover:text-violet-300 transition-colors mb-1">
          {set.name}
        </h3>
        {set.description && (
          <p className="text-xs text-zinc-500 dark:text-zinc-400 line-clamp-2 mb-3">
            {set.description}
          </p>
        )}
        <div className="flex flex-wrap gap-1.5 mb-3">
          {set.criteria.map((c) => (
            <span
              key={c.name}
              className="inline-flex items-center px-2 py-0.5 rounded-md bg-zinc-100 dark:bg-zinc-800 text-xs text-zinc-600 dark:text-zinc-400"
            >
              {c.name}
              <span className="ml-1 text-zinc-400 dark:text-zinc-600">×{c.weight}</span>
            </span>
          ))}
        </div>
        <span className="text-xs text-zinc-400 dark:text-zinc-500">{formatDate(set.created_at)}</span>
      </Link>
    </Card>
  )
}
