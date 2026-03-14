'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, FolderKanban } from 'lucide-react'
import { listProjects } from '@/lib/api/projects'
import { queryKeys } from '@/lib/queryKeys'
import { PageHeader } from '@/components/layout/PageHeader'
import { ProjectCard } from '@/components/projects/ProjectCard'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { EmptyState } from '@/components/ui/EmptyState'

export default function ProjectsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.projects.list(0, 50),
    queryFn: () => listProjects(0, 50),
  })

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
          <p className="text-xs text-zinc-400 dark:text-zinc-500 mb-4">
            {data.total} project{data.total !== 1 ? 's' : ''}
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.items.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
