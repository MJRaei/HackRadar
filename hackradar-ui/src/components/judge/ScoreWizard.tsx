'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChevronRight } from 'lucide-react'
import { listProjects } from '@/lib/api/projects'
import { listCriteriaSets } from '@/lib/api/criteria'
import { queryKeys } from '@/lib/queryKeys'
import { useScoreMutation } from '@/hooks/useScoreMutation'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import { StatusBadge } from '@/components/ui/Badge'

type Step = 'select-projects' | 'select-criteria'

export function ScoreWizard() {
  const [step, setStep] = useState<Step>('select-projects')
  const [selectedProjects, setSelectedProjects] = useState<Set<string>>(new Set())
  const [selectedCriteria, setSelectedCriteria] = useState<string>('')

  const { score, isPending } = useScoreMutation()

  const { data: projectsData, isLoading: loadingProjects } = useQuery({
    queryKey: queryKeys.projects.list(0, 200),
    queryFn: () => listProjects(0, 200),
  })

  const { data: criteriaData, isLoading: loadingCriteria } = useQuery({
    queryKey: queryKeys.criteria.list(),
    queryFn: () => listCriteriaSets(),
  })

  const indexedProjects = projectsData?.items.filter((p) => p.status === 'indexed') ?? []

  function toggleProject(id: string) {
    setSelectedProjects((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  function toggleAll() {
    if (selectedProjects.size === indexedProjects.length) {
      setSelectedProjects(new Set())
    } else {
      setSelectedProjects(new Set(indexedProjects.map((p) => p.id)))
    }
  }

  async function handleScore() {
    if (!selectedCriteria || selectedProjects.size === 0) return
    await score({ project_ids: Array.from(selectedProjects), criteria_set_id: selectedCriteria })
  }

  return (
    <div className="max-w-2xl">
      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-6 text-xs">
        <span
          className={step === 'select-projects' ? 'text-violet-700 dark:text-violet-300 font-medium' : 'text-zinc-400'}
        >
          1. Select projects
        </span>
        <ChevronRight className="w-3 h-3 text-zinc-300 dark:text-zinc-600" />
        <span
          className={step === 'select-criteria' ? 'text-violet-700 dark:text-violet-300 font-medium' : 'text-zinc-400'}
        >
          2. Select criteria set
        </span>
      </div>

      {step === 'select-projects' && (
        <div>
          <Card className="divide-y divide-zinc-100 dark:divide-zinc-800 mb-4">
            {loadingProjects && (
              <div className="flex justify-center py-8">
                <Spinner className="w-5 h-5" />
              </div>
            )}
            {!loadingProjects && indexedProjects.length === 0 && (
              <p className="text-sm text-zinc-500 dark:text-zinc-400 p-6 text-center">
                No indexed projects yet. Wait for projects to finish indexing.
              </p>
            )}
            {!loadingProjects && indexedProjects.length > 0 && (
              <label className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors">
                <input
                  type="checkbox"
                  checked={selectedProjects.size === indexedProjects.length}
                  ref={(el) => { if (el) el.indeterminate = selectedProjects.size > 0 && selectedProjects.size < indexedProjects.length }}
                  onChange={toggleAll}
                  className="rounded border-zinc-300 dark:border-zinc-600 text-violet-600 focus:ring-violet-500"
                />
                <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">Select all</span>
              </label>
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
                  <p className="text-xs text-zinc-400 dark:text-zinc-500 truncate">
                    {p.github_url.replace('https://github.com/', '')}
                  </p>
                </div>
                <StatusBadge status={p.status} />
              </label>
            ))}
          </Card>

          <div className="flex items-center justify-between">
            <span className="text-xs text-zinc-500 dark:text-zinc-400">
              {selectedProjects.size} of {indexedProjects.length} selected
            </span>
            <Button
              onClick={() => setStep('select-criteria')}
              disabled={selectedProjects.size === 0}
              size="sm"
            >
              Next
              <ChevronRight className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>
      )}

      {step === 'select-criteria' && (
        <div>
          <Card className="divide-y divide-zinc-100 dark:divide-zinc-800 mb-4">
            {loadingCriteria && (
              <div className="flex justify-center py-8">
                <Spinner className="w-5 h-5" />
              </div>
            )}
            {!loadingCriteria && (criteriaData?.items.length ?? 0) === 0 && (
              <p className="text-sm text-zinc-500 dark:text-zinc-400 p-6 text-center">
                No criteria sets found. Create one first.
              </p>
            )}
            {criteriaData?.items.map((cs) => (
              <label
                key={cs.id}
                className="flex items-start gap-3 px-4 py-3 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors"
              >
                <input
                  type="radio"
                  name="criteria_set"
                  value={cs.id}
                  checked={selectedCriteria === cs.id}
                  onChange={() => setSelectedCriteria(cs.id)}
                  className="mt-0.5 text-violet-600 focus:ring-violet-500"
                />
                <div>
                  <p className="text-sm text-zinc-900 dark:text-zinc-100">{cs.name}</p>
                  {cs.description && (
                    <p className="text-xs text-zinc-500 dark:text-zinc-400">{cs.description}</p>
                  )}
                  <div className="flex flex-wrap gap-1 mt-1">
                    {cs.criteria.map((c) => (
                      <span
                        key={c.name}
                        className="text-xs bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 px-1.5 py-0.5 rounded"
                      >
                        {c.name}
                      </span>
                    ))}
                  </div>
                </div>
              </label>
            ))}
          </Card>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setStep('select-projects')}>
              Back
            </Button>
            <Button
              onClick={handleScore}
              disabled={!selectedCriteria || isPending}
              loading={isPending}
              size="sm"
            >
              Score {selectedProjects.size} project{selectedProjects.size !== 1 ? 's' : ''}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
