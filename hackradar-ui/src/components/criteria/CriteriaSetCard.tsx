import Link from 'next/link'
import { Card } from '@/components/ui/Card'
import { formatDate } from '@/lib/utils'
import type { CriteriaSetResponse } from '@/lib/types'

interface CriteriaSetCardProps {
  set: CriteriaSetResponse
  selected?: boolean
  onToggle?: (id: string) => void
}

export function CriteriaSetCard({ set, selected, onToggle }: CriteriaSetCardProps) {
  return (
    <Card className={`p-4 hover:shadow-md transition-shadow group relative${selected ? ' ring-2 ring-violet-500 dark:ring-violet-400' : ''}`}>
      {onToggle && (
        <button
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); onToggle(set.id) }}
          aria-label={selected ? 'Deselect' : 'Select'}
          className={`absolute top-3 left-3 z-10 w-4 h-4 rounded border transition-all flex items-center justify-center
            ${selected
              ? 'bg-violet-600 border-violet-600 opacity-100'
              : 'bg-white dark:bg-zinc-900 border-zinc-300 dark:border-zinc-600 opacity-0 group-hover:opacity-100'
            }`}
        >
          {selected && (
            <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 10 10">
              <path d="M1.5 5l2.5 2.5 4.5-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          )}
        </button>
      )}

      <Link href={`/criteria/${set.id}`} className={`block${onToggle ? ' pl-6' : ''}`}>
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
