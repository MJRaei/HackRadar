'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, FolderKanban, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { listProjects, deleteProject } from '@/lib/api/projects'
import { queryKeys } from '@/lib/queryKeys'
import { PageHeader } from '@/components/layout/PageHeader'
import { ProjectCard } from '@/components/projects/ProjectCard'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'

export default function ProjectsPage() {
  const queryClient = useQueryClient()
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [showBulkDelete, setShowBulkDelete] = useState(false)

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.projects.list(0, 50),
    queryFn: () => listProjects(0, 50),
  })

  const bulkDeleteMutation = useMutation({
    mutationFn: async (ids: string[]) => {
      await Promise.all(ids.map((id) => deleteProject(id)))
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all })
      toast.success(`Deleted ${selectedIds.size} project${selectedIds.size !== 1 ? 's' : ''}`)
      setSelectedIds(new Set())
      setShowBulkDelete(false)
    },
    onError: (err: Error) => toast.error(err.message),
  })

  function toggleSelect(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const allIds = data?.items.map((p) => p.id) ?? []
  const allSelected = allIds.length > 0 && allIds.every((id) => selectedIds.has(id))

  function toggleSelectAll() {
    setSelectedIds(allSelected ? new Set() : new Set(allIds))
  }

  const hasSelection = selectedIds.size > 0

  return (
    <div>
      <PageHeader
        title="Projects"
        description="Hackathon submissions being indexed and judged."
        action={
          <Link href="/projects/new">
            <Button size="sm">
              <Plus className="w-3.5 h-3.5" />
              Add project
            </Button>
          </Link>
        }
      />

      {isLoading && (
        <div className="flex justify-center py-16">
          <Spinner className="w-5 h-5" />
        </div>
      )}

      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">Failed to load projects.</p>
      )}

      {data && data.items.length === 0 && (
        <EmptyState
          icon={FolderKanban}
          title="No projects yet"
          description="Add a GitHub repository to get started."
          action={
            <Link href="/projects/new">
              <Button size="sm">
                <Plus className="w-3.5 h-3.5" />
                Add project
              </Button>
            </Link>
          }
        />
      )}

      {data && data.items.length > 0 && (
        <>
          {/* Selection action bar — slides in when something is selected */}
          <div className={`flex items-center justify-between mb-4 transition-all duration-150 ${hasSelection ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
            <span className="text-xs text-zinc-500 dark:text-zinc-400">
              {selectedIds.size} selected
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={toggleSelectAll}
                className="text-xs text-zinc-500 dark:text-zinc-400 hover:text-zinc-800 dark:hover:text-zinc-200 transition-colors"
              >
                {allSelected ? 'Deselect all' : 'Select all'}
              </button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setShowBulkDelete(true)}
              >
                <Trash2 className="w-3.5 h-3.5" />
                Delete {selectedIds.size}
              </Button>
            </div>
          </div>

          {/* Count line — hidden when selection bar is showing */}
          {!hasSelection && (
            <p className="text-xs text-zinc-400 dark:text-zinc-500 mb-4">
              {data.total} project{data.total !== 1 ? 's' : ''}
            </p>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.items.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                selected={selectedIds.has(project.id)}
                onToggle={toggleSelect}
              />
            ))}
          </div>
        </>
      )}

      <ConfirmDialog
        isOpen={showBulkDelete}
        title={`Delete ${selectedIds.size} project${selectedIds.size !== 1 ? 's' : ''}`}
        message={`Are you sure you want to delete ${selectedIds.size} project${selectedIds.size !== 1 ? 's' : ''}? This will also remove all scores and Qdrant collections.`}
        confirmLabel={`Delete ${selectedIds.size}`}
        onConfirm={() => bulkDeleteMutation.mutate(Array.from(selectedIds))}
        onCancel={() => setShowBulkDelete(false)}
        loading={bulkDeleteMutation.isPending}
      />
    </div>
  )
}
