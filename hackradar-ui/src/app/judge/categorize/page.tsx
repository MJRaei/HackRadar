import { PageHeader } from '@/components/layout/PageHeader'
import { CategorizationPanel } from '@/components/judge/CategorizationPanel'

export default function CategorizePage() {
  return (
    <div>
      <PageHeader
        title="Categorize"
        description="Group projects into categories automatically or with hints."
      />
      <CategorizationPanel />
    </div>
  )
}
