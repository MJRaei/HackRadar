'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { listProjects } from '@/lib/api/projects'
import { categorizeProjects } from '@/lib/api/judging'
import { queryKeys } from '@/lib/queryKeys'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Textarea } from '@/components/ui/Textarea'
import { Spinner } from '@/components/ui/Spinner'
import { StatusBadge } from '@/components/ui/Badge'
import type { CategorizationResponse } from '@/lib/types'

export function CategorizationPanel() {
  const [selectedProjects, setSelectedProjects] = useState<Set<string>>(new Set())
  const [categoryHints, setCategoryHints] = useState('')
  const [result, setResult] = useState<CategorizationResponse | null>(null)

  const { data: projectsData, isLoading } = useQuery({
    queryKey: queryKeys.projects.list(0, 200),
    queryFn: () => listProjects(0, 200),
  })

  const indexedProjects = projectsData?.items.filter((p) => p.status === 'indexed') ?? []

  const mutation = useMutation({
    mutationFn: categorizeProjects,
    onSuccess: (data) => {
      setResult(data)
      toast.success(`Categorized ${data.assignments.length} project(s)`)
    },
    onError: (err: Error) => toast.error(err.message),
  })

  function toggleProject(id: string) {
    setSelectedProjects((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  function handleCategorize() {
    const categories = categoryHints
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
    mutation.mutate({
      project_ids: Array.from(selectedProjects),
      categories: categories.length > 0 ? categories : undefined,
    })
  }

  // Group assignments by category
  const byCategory: Record<string, string[]> = {}
  result?.assignments.forEach((a) => {
    if (!byCategory[a.category]) byCategory[a.category] = []
    byCategory[a.category].push(a.project_name)
  })

  return (
    <div className="max-w-2xl space-y-6">
      <Card className="divide-y divide-zinc-100 dark:divide-zinc-800">
        {isLoading && (
          <div className="flex justify-center py-8">
            <Spinner className="w-5 h-5" />
          </div>
        )}
        {!isLoading && indexedProjects.length === 0 && (
          <p className="text-sm text-zinc-500 dark:text-zinc-400 p-6 text-center">
            No indexed projects yet.
          </p>
        )}
        {indexedProjects.map((p) => (
          <label
            key={p.id}
            className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors"
          >
            <input
              type="checkbox"
              checked={selectedProjects.has(p.id)}
              onChange={() => toggleProject(p.id)}
              className="rounded border-zinc-300 dark:border-zinc-600 text-violet-600 focus:ring-violet-500"
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-zinc-900 dark:text-zinc-100 truncate">{p.name}</p>
            </div>
            <StatusBadge status={p.status} />
          </label>
        ))}
      </Card>

      <div className="flex flex-col gap-1.5">
        <Textarea
          label="Category hints (optional)"
          placeholder="Web App, Mobile App, AI/ML, DevTools, …"
          rows={2}
          value={categoryHints}
          onChange={(e) => setCategoryHints(e.target.value)}
        />
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          Comma-separated. Leave empty for auto-discovery.
        </p>
      </div>

      <Button
        onClick={handleCategorize}
        disabled={selectedProjects.size === 0 || mutation.isPending}
        loading={mutation.isPending}
      >
        Categorize {selectedProjects.size} project{selectedProjects.size !== 1 ? 's' : ''}
      </Button>

      {result && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 dark:text-zinc-500">
              Results
            </h2>
            {result.categories_created.length > 0 && (
              <span className="text-xs text-emerald-600 dark:text-emerald-400">
                {result.categories_created.length} new categor{result.categories_created.length > 1 ? 'ies' : 'y'} created
              </span>
            )}
          </div>
          <div className="space-y-3">
            {Object.entries(byCategory).map(([category, projects]) => (
              <Card key={category} className="p-4">
                <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-100 mb-2">
                  {category}
                </h3>
                <div className="flex flex-wrap gap-1.5">
                  {projects.map((name) => (
                    <span
                      key={name}
                      className="text-xs bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 px-2 py-1 rounded-md"
                    >
                      {name}
                    </span>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
