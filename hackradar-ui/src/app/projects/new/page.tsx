import { PageHeader } from '@/components/layout/PageHeader'
import { AddProjectForm } from '@/components/projects/AddProjectForm'

export default function NewProjectPage() {
  return (
    <div>
      <PageHeader
        title="Add project"
        description="Submit a GitHub repository for indexing and judging."
      />
      <AddProjectForm />
    </div>
  )
}
