'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Plus } from 'lucide-react'
import { createCriteriaSet } from '@/lib/api/criteria'
import { queryKeys } from '@/lib/queryKeys'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { CriterionRow } from './CriterionRow'
import type { Criterion } from '@/lib/types'

const defaultCriterion = (): Criterion => ({ name: '', description: '', weight: 1.0 })

export function AddCriteriaSetForm() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [criteria, setCriteria] = useState<Criterion[]>([defaultCriterion()])
  const [errors, setErrors] = useState<Record<string, string>>({})

  const mutation = useMutation({
    mutationFn: createCriteriaSet,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.criteria.all })
      toast.success('Criteria set created')
      router.push('/criteria')
    },
    onError: (err: Error) => toast.error(err.message),
  })

  function validate() {
    const errs: Record<string, string> = {}
    if (!name.trim()) errs.name = 'Name is required'
    criteria.forEach((c, i) => {
      if (!c.name.trim()) errs[`criterion_${i}_name`] = 'required'
      if (!c.description.trim()) errs[`criterion_${i}_desc`] = 'required'
    })
    return errs
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }
    setErrors({})
    mutation.mutate({
      name: name.trim(),
      description: description.trim() || undefined,
      criteria,
    })
  }

  return (
    <Card className="p-6 max-w-2xl">
      <form onSubmit={handleSubmit} className="space-y-5">
        <Input
          id="name"
          label="Name"
          placeholder="e.g. Technical Evaluation"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={errors.name}
        />
        <Textarea
          id="description"
          label="Description (optional)"
          placeholder="What is this criteria set for?"
          rows={2}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        <div>
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Criteria</span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setCriteria((c) => [...c, defaultCriterion()])}
            >
              <Plus className="w-3.5 h-3.5" />
              Add criterion
            </Button>
          </div>
          <div className="space-y-3">
            {criteria.map((c, i) => (
              <CriterionRow
                key={i}
                index={i}
                value={c}
                onChange={(v) => setCriteria((prev) => prev.map((x, j) => (j === i ? v : x)))}
                onRemove={() => setCriteria((prev) => prev.filter((_, j) => j !== i))}
                canRemove={criteria.length > 1}
              />
            ))}
          </div>
        </div>

        <div className="flex gap-2 pt-1">
          <Button type="submit" loading={mutation.isPending}>
            Create criteria set
          </Button>
          <Button type="button" variant="ghost" onClick={() => router.back()}>
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  )
}
