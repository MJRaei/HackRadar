import { PageHeader } from '@/components/layout/PageHeader'
import { ScoreWizard } from '@/components/judge/ScoreWizard'

export default function ScorePage() {
  return (
    <div>
      <PageHeader
        title="Score projects"
        description="Select projects and a criteria set to run AI-powered scoring."
      />
      <ScoreWizard />
    </div>
  )
}
