import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import type { ProjectStatus } from './types'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

export function statusToVariant(
  status: ProjectStatus
): 'pending' | 'cloning' | 'indexing' | 'indexed' | 'failed' {
  return status
}

export function scoreToVariant(score: number): 'high' | 'mid' | 'low' {
  if (score >= 8) return 'high'
  if (score >= 5) return 'mid'
  return 'low'
}

export const TERMINAL_STATUSES = new Set<ProjectStatus>(['indexed', 'failed'])

export function isTerminal(status: ProjectStatus | undefined): boolean {
  return status ? TERMINAL_STATUSES.has(status) : false
}
