import { Trash2 } from 'lucide-react'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Button } from '@/components/ui/Button'
import type { Criterion } from '@/lib/types'

interface CriterionRowProps {
  index: number
  value: Criterion
  onChange: (value: Criterion) => void
  onRemove: () => void
  canRemove: boolean
}

export function CriterionRow({ index, value, onChange, onRemove, canRemove }: CriterionRowProps) {
  return (
    <div className="rounded-lg border border-zinc-200 dark:border-zinc-700 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
          Criterion {index + 1}
        </span>
        {canRemove && (
          <Button variant="ghost" size="sm" onClick={onRemove} type="button">
            <Trash2 className="w-3.5 h-3.5" />
          </Button>
        )}
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="col-span-2">
          <Input
            label="Name"
            placeholder="e.g. Innovation"
            value={value.name}
            onChange={(e) => onChange({ ...value, name: e.target.value })}
          />
        </div>
        <Input
          type="number"
          label="Weight"
          placeholder="1.0"
          min={0}
          step={0.1}
          value={value.weight}
          onChange={(e) => onChange({ ...value, weight: parseFloat(e.target.value) || 1 })}
        />
      </div>
      <Textarea
        label="Description"
        placeholder="What does this criterion evaluate?"
        rows={2}
        value={value.description}
        onChange={(e) => onChange({ ...value, description: e.target.value })}
      />
    </div>
  )
}
