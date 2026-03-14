'use client'

import { useState } from 'react'
import { PageHeader } from '@/components/layout/PageHeader'
import { AddProjectForm } from '@/components/projects/AddProjectForm'
import { BulkUploadForm } from '@/components/projects/BulkUploadForm'

type Tab = 'single' | 'bulk'

export default function NewProjectPage() {
  const [tab, setTab] = useState<Tab>('single')

  return (
    <div>
      <PageHeader
        title="Add project"
        description="Submit one GitHub repository or upload a file to add many at once."
      />

      <div className="mb-6 flex gap-1 rounded-lg border border-zinc-200 dark:border-zinc-700 bg-zinc-100 dark:bg-zinc-900 p-1 w-fit">
        <TabButton active={tab === 'single'} onClick={() => setTab('single')}>
          Single
        </TabButton>
        <TabButton active={tab === 'bulk'} onClick={() => setTab('bulk')}>
          Bulk upload
        </TabButton>
      </div>

      {tab === 'single' ? <AddProjectForm /> : <BulkUploadForm />}
    </div>
  )
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        'px-4 py-1.5 rounded-md text-sm font-medium transition-colors',
        active
          ? 'bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm'
          : 'text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200',
      ].join(' ')}
    >
      {children}
    </button>
  )
}
