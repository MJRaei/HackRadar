import { PageHeader } from '@/components/layout/PageHeader'
import { AddCriteriaSetForm } from '@/components/criteria/AddCriteriaSetForm'

export default function NewCriteriaSetPage() {
  return (
    <div>
      <PageHeader
        title="New criteria set"
        description="Define the criteria and weights for scoring projects."
      />
      <AddCriteriaSetForm />
    </div>
  )
}
