'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { createProject } from '@/lib/api/projects'
import { queryKeys } from '@/lib/queryKeys'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'

export function AddProjectForm() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [githubUrl, setGithubUrl] = useState('')
  const [summary, setSummary] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})

  const mutation = useMutation({
    mutationFn: createProject,
    onSuccess: (project) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all })
      toast.success(`Project "${project.name}" submitted`)
      router.push(`/projects/${project.id}`)
    },
    onError: (err: Error) => {
      toast.error(err.message)
    },
  })

  function validate() {
    const errs: Record<string, string> = {}
    if (!name.trim()) errs.name = 'Name is required'
    if (!githubUrl.trim()) errs.githubUrl = 'GitHub URL is required'
    else if (!githubUrl.startsWith('https://github.com/'))
      errs.githubUrl = 'Must start with https://github.com/'
    return errs
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) {
      setErrors(errs)
      return
    }
    setErrors({})
    mutation.mutate({ name: name.trim(), github_url: githubUrl.trim(), summary: summary.trim() || undefined })
  }

  return (
    <Card className="p-6 max-w-xl">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          id="name"
          label="Project name"
          placeholder="My Awesome Project"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={errors.name}
        />
        <Input
          id="github_url"
          label="GitHub URL"
          placeholder="https://github.com/owner/repo"
          value={githubUrl}
          onChange={(e) => setGithubUrl(e.target.value)}
          error={errors.githubUrl}
        />
        <Textarea
          id="summary"
          label="Summary (optional)"
          placeholder="Brief description of the project…"
          rows={3}
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
        />
        <div className="flex gap-2 pt-1">
          <Button type="submit" loading={mutation.isPending}>
            Add project
          </Button>
          <Button type="button" variant="ghost" onClick={() => router.back()}>
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  )
}
