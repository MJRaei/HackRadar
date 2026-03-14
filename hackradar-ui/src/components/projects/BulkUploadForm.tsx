'use client'

import { useRef, useState } from 'react'
import { useQueryClient, useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { UploadCloud, FileText, X, CheckCircle2, AlertCircle } from 'lucide-react'
import { bulkUploadProjects } from '@/lib/api/projects'
import { queryKeys } from '@/lib/queryKeys'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import type { BulkUploadResponse } from '@/lib/types'

const ACCEPTED = ['.txt', '.csv']
const MAX_SIZE_MB = 5

function FileDropZone({
  file,
  onSelect,
  onClear,
}: {
  file: File | null
  onSelect: (f: File) => void
  onClear: () => void
}) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  function handleFiles(files: FileList | null) {
    const f = files?.[0]
    if (!f) return
    const ext = f.name.slice(f.name.lastIndexOf('.')).toLowerCase()
    if (!ACCEPTED.includes(ext)) {
      toast.error('Only .txt and .csv files are supported.')
      return
    }
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      toast.error(`File must be smaller than ${MAX_SIZE_MB} MB.`)
      return
    }
    onSelect(f)
  }

  if (file) {
    return (
      <div className="flex items-center gap-3 rounded-lg border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-900 px-4 py-3">
        <FileText className="w-5 h-5 text-violet-500 shrink-0" />
        <span className="flex-1 text-sm font-medium text-zinc-800 dark:text-zinc-200 truncate">
          {file.name}
        </span>
        <span className="text-xs text-zinc-400 shrink-0">
          {(file.size / 1024).toFixed(1)} KB
        </span>
        <button
          type="button"
          onClick={onClear}
          className="ml-1 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200"
          aria-label="Remove file"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    )
  }

  return (
    <button
      type="button"
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragging(false)
        handleFiles(e.dataTransfer.files)
      }}
      className={[
        'w-full rounded-lg border-2 border-dashed px-6 py-10 text-center transition-colors',
        dragging
          ? 'border-violet-500 bg-violet-50 dark:bg-violet-950'
          : 'border-zinc-300 dark:border-zinc-600 hover:border-violet-400 hover:bg-zinc-50 dark:hover:bg-zinc-900',
      ].join(' ')}
    >
      <UploadCloud className="mx-auto mb-3 w-8 h-8 text-zinc-400" />
      <p className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
        Drop a file here, or <span className="text-violet-600 dark:text-violet-400">browse</span>
      </p>
      <p className="mt-1 text-xs text-zinc-400">.txt or .csv — max {MAX_SIZE_MB} MB</p>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED.join(',')}
        className="sr-only"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </button>
  )
}

function UploadSummary({ result }: { result: BulkUploadResponse }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3 text-center">
        <Stat label="Found" value={result.total_found} />
        <Stat label="Queued" value={result.queued.length} accent="green" />
        <Stat label="Skipped" value={result.skipped.length} accent="amber" />
      </div>

      {result.queued.length > 0 && (
        <div>
          <h3 className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
            <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
            Queued
          </h3>
          <ul className="space-y-1">
            {result.queued.map((p) => (
              <li key={p.id} className="flex items-center gap-2 text-sm text-zinc-700 dark:text-zinc-300">
                <span className="w-2 h-2 rounded-full bg-green-400 shrink-0" />
                <span className="font-medium">{p.name}</span>
                <span className="text-zinc-400 truncate text-xs">{p.github_url}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {result.skipped.length > 0 && (
        <div>
          <h3 className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
            <AlertCircle className="w-3.5 h-3.5 text-amber-500" />
            Skipped
          </h3>
          <ul className="space-y-1">
            {result.skipped.map((s) => (
              <li key={s.url} className="flex items-start gap-2 text-sm">
                <span className="mt-1.5 w-2 h-2 rounded-full bg-amber-400 shrink-0" />
                <span className="text-zinc-700 dark:text-zinc-300 truncate">{s.url}</span>
                <span className="text-zinc-400 shrink-0 text-xs">{s.reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function Stat({
  label,
  value,
  accent,
}: {
  label: string
  value: number
  accent?: 'green' | 'amber'
}) {
  const color =
    accent === 'green'
      ? 'text-green-600 dark:text-green-400'
      : accent === 'amber'
      ? 'text-amber-600 dark:text-amber-400'
      : 'text-zinc-800 dark:text-zinc-100'

  return (
    <div className="rounded-lg border border-zinc-200 dark:border-zinc-700 py-3">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-zinc-500 dark:text-zinc-400">{label}</p>
    </div>
  )
}

export function BulkUploadForm() {
  const queryClient = useQueryClient()
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<BulkUploadResponse | null>(null)

  const mutation = useMutation({
    mutationFn: (f: File) => bulkUploadProjects(f),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all })
      setResult(data)
      const q = data.queued.length
      const s = data.skipped.length
      if (q === 0) {
        toast.warning(`No new projects queued — ${s} duplicate${s !== 1 ? 's' : ''} skipped.`)
      } else {
        toast.success(`${q} project${q !== 1 ? 's' : ''} queued for indexing.`)
      }
    },
    onError: (err: Error) => {
      toast.error(err.message)
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!file) {
      toast.error('Please select a file first.')
      return
    }
    setResult(null)
    mutation.mutate(file)
  }

  function handleClear() {
    setFile(null)
    setResult(null)
    mutation.reset()
  }

  return (
    <Card className="p-6 max-w-xl space-y-5">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <p className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Upload file</p>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            Provide a .txt or .csv file containing GitHub repo URLs (one per line or cell).
            Project names are derived from the repository name automatically.
          </p>
        </div>

        <FileDropZone file={file} onSelect={setFile} onClear={handleClear} />

        <div className="flex gap-2 pt-1">
          <Button type="submit" loading={mutation.isPending} disabled={!file}>
            Upload &amp; queue
          </Button>
          {file && (
            <Button type="button" variant="ghost" onClick={handleClear}>
              Clear
            </Button>
          )}
        </div>
      </form>

      {result && (
        <div className="border-t border-zinc-200 dark:border-zinc-700 pt-4">
          <UploadSummary result={result} />
        </div>
      )}
    </Card>
  )
}
