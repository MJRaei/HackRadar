'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import {
  FolderKanban,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ListChecks,
  Plus,
  Zap,
  Trophy,
  Upload,
  ArrowRight,
} from 'lucide-react'
import { listProjects } from '@/lib/api/projects'
import { listCriteriaSets } from '@/lib/api/criteria'
import { getRankings } from '@/lib/api/judging'
import { queryKeys } from '@/lib/queryKeys'
import { PageHeader } from '@/components/layout/PageHeader'
import { Card } from '@/components/ui/Card'
import { StatusBadge, ScoreBadge } from '@/components/ui/Badge'
import { Spinner } from '@/components/ui/Spinner'
import type { ProjectStatus } from '@/lib/types'

// ── Stat card ────────────────────────────────────────────────────────────────

interface StatCardProps {
  label: string
  value: number | string
  icon: React.ReactNode
  sub?: string
  color?: string
}

function StatCard({ label, value, icon, sub, color = 'text-violet-600' }: StatCardProps) {
  return (
    <Card className="p-5 flex items-start gap-4">
      <div className={`mt-0.5 ${color}`}>{icon}</div>
      <div>
        <p className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 leading-none">{value}</p>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">{label}</p>
        {sub && <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-0.5">{sub}</p>}
      </div>
    </Card>
  )
}

// ── Status bar ────────────────────────────────────────────────────────────────

const statusColors: Record<ProjectStatus, string> = {
  indexed: 'bg-emerald-500',
  indexing: 'bg-amber-400',
  cloning: 'bg-blue-400',
  pending: 'bg-zinc-300 dark:bg-zinc-600',
  failed: 'bg-red-500',
}

const statusOrder: ProjectStatus[] = ['indexed', 'indexing', 'cloning', 'pending', 'failed']

interface StatusBreakdownProps {
  counts: Record<ProjectStatus, number>
  total: number
}

function StatusBreakdown({ counts, total }: StatusBreakdownProps) {
  return (
    <div>
      {/* Stacked bar */}
      <div className="flex h-2.5 w-full rounded-full overflow-hidden gap-0.5 mb-3">
        {statusOrder.map((s) => {
          const pct = total > 0 ? (counts[s] / total) * 100 : 0
          if (pct === 0) return null
          return (
            <div
              key={s}
              className={`${statusColors[s]} rounded-sm`}
              style={{ width: `${pct}%` }}
              title={`${s}: ${counts[s]}`}
            />
          )
        })}
      </div>
      {/* Legend */}
      <div className="flex flex-wrap gap-x-4 gap-y-1.5">
        {statusOrder.map((s) => (
          <div key={s} className="flex items-center gap-1.5 text-xs text-zinc-500 dark:text-zinc-400">
            <span className={`inline-block w-2 h-2 rounded-sm ${statusColors[s]}`} />
            <span className="capitalize">{s}</span>
            <span className="font-medium text-zinc-700 dark:text-zinc-300">{counts[s]}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Quick action button ───────────────────────────────────────────────────────

interface QuickActionProps {
  href: string
  icon: React.ReactNode
  label: string
  description: string
}

function QuickAction({ href, icon, label, description }: QuickActionProps) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 hover:border-violet-300 dark:hover:border-violet-700 hover:bg-violet-50 dark:hover:bg-violet-950/30 transition-colors group"
    >
      <div className="text-violet-600 group-hover:scale-110 transition-transform">{icon}</div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{label}</p>
        <p className="text-xs text-zinc-500 dark:text-zinc-400 truncate">{description}</p>
      </div>
      <ArrowRight className="w-4 h-4 text-zinc-400 group-hover:text-violet-500 transition-colors shrink-0" />
    </Link>
  )
}

// ── Main dashboard ────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { data: projectsData, isLoading: loadingProjects } = useQuery({
    queryKey: queryKeys.projects.list(0, 200),
    queryFn: () => listProjects(0, 200),
  })

  const { data: criteriaData, isLoading: loadingCriteria } = useQuery({
    queryKey: queryKeys.criteria.list(),
    queryFn: () => listCriteriaSets(0, 50),
  })

  // Pick first criteria set for rankings preview
  const firstCriteriaSet = criteriaData?.items[0]

  const { data: rankingsData } = useQuery({
    queryKey: firstCriteriaSet ? queryKeys.rankings(firstCriteriaSet.id) : ['rankings', 'none'],
    queryFn: () => getRankings(firstCriteriaSet!.id),
    enabled: !!firstCriteriaSet,
  })

  const loading = loadingProjects || loadingCriteria

  // Compute stats
  const allProjects = projectsData?.items ?? []
  const total = projectsData?.total ?? 0

  const counts: Record<ProjectStatus, number> = {
    indexed: 0,
    indexing: 0,
    cloning: 0,
    pending: 0,
    failed: 0,
  }
  for (const p of allProjects) counts[p.status]++

  const inProgress = counts.cloning + counts.indexing + counts.pending
  const totalCriteria = criteriaData?.total ?? 0

  // Recent projects — last 5 by created_at desc
  const recentProjects = [...allProjects]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)

  // Top 5 ranked
  const topRanked = rankingsData?.slice(0, 5) ?? []

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Overview of your hackathon judging pipeline."
      />

      {loading ? (
        <div className="flex justify-center py-16">
          <Spinner className="w-5 h-5" />
        </div>
      ) : (
        <div className="space-y-8">

          {/* ── Stat cards ── */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              label="Total projects"
              value={total}
              icon={<FolderKanban className="w-5 h-5" />}
            />
            <StatCard
              label="Indexed"
              value={counts.indexed}
              icon={<CheckCircle2 className="w-5 h-5" />}
              sub={total > 0 ? `${Math.round((counts.indexed / total) * 100)}% ready` : undefined}
              color="text-emerald-600"
            />
            <StatCard
              label="In progress"
              value={inProgress}
              icon={<Loader2 className="w-5 h-5" />}
              color="text-amber-500"
            />
            <StatCard
              label="Failed"
              value={counts.failed}
              icon={<AlertCircle className="w-5 h-5" />}
              color="text-red-500"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* ── Status breakdown + recent projects (left 2/3) ── */}
            <div className="lg:col-span-2 space-y-6">

              {/* Status distribution */}
              {total > 0 && (
                <Card className="p-5">
                  <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 mb-4">
                    Project status distribution
                  </h2>
                  <StatusBreakdown counts={counts} total={total} />
                </Card>
              )}

              {/* Recent projects */}
              <Card className="p-5">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                    Recent projects
                  </h2>
                  <Link
                    href="/projects"
                    className="text-xs text-violet-600 hover:text-violet-700 dark:text-violet-400 dark:hover:text-violet-300 transition-colors"
                  >
                    View all
                  </Link>
                </div>

                {recentProjects.length === 0 ? (
                  <p className="text-sm text-zinc-400 dark:text-zinc-500 py-4 text-center">
                    No projects yet.
                  </p>
                ) : (
                  <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
                    {recentProjects.map((project) => (
                      <Link
                        key={project.id}
                        href={`/projects/${project.id}`}
                        className="flex items-center justify-between py-2.5 gap-3 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 -mx-5 px-5 transition-colors"
                      >
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100 truncate">
                            {project.name}
                          </p>
                          <p className="text-xs text-zinc-400 dark:text-zinc-500 truncate">
                            {project.github_url.replace('https://github.com/', '')}
                          </p>
                        </div>
                        <StatusBadge status={project.status} />
                      </Link>
                    ))}
                  </div>
                )}
              </Card>
            </div>

            {/* ── Right column: rankings + quick actions ── */}
            <div className="space-y-6">

              {/* Criteria sets count */}
              <Card className="p-5 flex items-start gap-4">
                <ListChecks className="w-5 h-5 mt-0.5 text-violet-600" />
                <div>
                  <p className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 leading-none">
                    {totalCriteria}
                  </p>
                  <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">Criteria set{totalCriteria !== 1 ? 's' : ''}</p>
                </div>
              </Card>

              {/* Top rankings */}
              <Card className="p-5">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                    Top ranked
                    {firstCriteriaSet && (
                      <span className="ml-1.5 font-normal text-zinc-400 dark:text-zinc-500 text-xs truncate">
                        · {firstCriteriaSet.name}
                      </span>
                    )}
                  </h2>
                  <Link
                    href="/judge/rankings"
                    className="text-xs text-violet-600 hover:text-violet-700 dark:text-violet-400 dark:hover:text-violet-300 transition-colors"
                  >
                    Full table
                  </Link>
                </div>

                {!firstCriteriaSet ? (
                  <p className="text-sm text-zinc-400 dark:text-zinc-500 py-4 text-center">
                    No criteria sets yet.
                  </p>
                ) : topRanked.length === 0 ? (
                  <p className="text-sm text-zinc-400 dark:text-zinc-500 py-4 text-center">
                    No scores yet.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {topRanked.map((entry) => (
                      <div key={entry.project_id} className="flex items-center gap-2">
                        <span className="text-xs font-bold text-zinc-300 dark:text-zinc-600 w-5 text-right shrink-0">
                          {entry.rank}
                        </span>
                        <p className="text-sm text-zinc-700 dark:text-zinc-300 flex-1 truncate">
                          {entry.project_name}
                        </p>
                        {entry.overall_score != null && (
                          <ScoreBadge score={entry.overall_score} />
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </Card>

              {/* Quick actions */}
              <div>
                <h2 className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-2">
                  Quick actions
                </h2>
                <div className="space-y-2">
                  <QuickAction
                    href="/projects/new"
                    icon={<Plus className="w-4 h-4" />}
                    label="Add project"
                    description="Submit a GitHub repository"
                  />
                  <QuickAction
                    href="/projects/new"
                    icon={<Upload className="w-4 h-4" />}
                    label="Bulk upload"
                    description="Import from CSV or TXT file"
                  />
                  <QuickAction
                    href="/judge/score"
                    icon={<Zap className="w-4 h-4" />}
                    label="Run scoring"
                    description="Score projects with an AI agent"
                  />
                  <QuickAction
                    href="/judge/rankings"
                    icon={<Trophy className="w-4 h-4" />}
                    label="View rankings"
                    description="See the full leaderboard"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
