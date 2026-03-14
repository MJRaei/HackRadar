'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { FolderKanban, ListChecks, Zap, Trophy, Tags, Moon, Sun, Radar } from 'lucide-react'
import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'

const navItems = [
  { href: '/projects', label: 'Projects', icon: FolderKanban },
  { href: '/criteria', label: 'Criteria', icon: ListChecks },
  { href: '/judge/score', label: 'Score', icon: Zap },
  { href: '/judge/rankings', label: 'Rankings', icon: Trophy },
  { href: '/judge/categorize', label: 'Categorize', icon: Tags },
]

export function Sidebar() {
  const pathname = usePathname()
  const [dark, setDark] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('theme')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const isDark = stored ? stored === 'dark' : prefersDark
    setDark(isDark)
    document.documentElement.classList.toggle('dark', isDark)
  }, [])

  function toggleTheme() {
    const next = !dark
    setDark(next)
    document.documentElement.classList.toggle('dark', next)
    localStorage.setItem('theme', next ? 'dark' : 'light')
  }

  return (
    <aside className="fixed inset-y-0 left-0 w-56 flex flex-col bg-zinc-50 dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 z-30">
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-5 border-b border-zinc-200 dark:border-zinc-800">
        <Radar className="w-5 h-5 text-violet-600" />
        <span className="font-semibold text-sm text-zinc-900 dark:text-zinc-100 tracking-tight">
          HackRadar
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-3 space-y-0.5">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + '/')
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors',
                active
                  ? 'bg-violet-50 dark:bg-violet-950 text-violet-700 dark:text-violet-300 font-medium'
                  : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 hover:text-zinc-900 dark:hover:text-zinc-100'
              )}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Theme toggle */}
      <div className="px-4 py-4 border-t border-zinc-200 dark:border-zinc-800">
        <button
          onClick={toggleTheme}
          className="flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 transition-colors"
        >
          {dark ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
          {dark ? 'Light mode' : 'Dark mode'}
        </button>
      </div>
    </aside>
  )
}
