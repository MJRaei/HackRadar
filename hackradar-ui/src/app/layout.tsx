import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Toaster } from 'sonner'
import { QueryProvider } from '@/providers/QueryProvider'
import { Sidebar } from '@/components/layout/Sidebar'
import './globals.css'

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata: Metadata = {
  title: 'HackRadar',
  description: 'Hackathon project judging with RAG-powered scoring',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100`}>
        <QueryProvider>
          <Sidebar />
          <main className="ml-56 min-h-screen p-8">
            <div className="max-w-5xl">{children}</div>
          </main>
          <Toaster position="bottom-right" richColors />
        </QueryProvider>
      </body>
    </html>
  )
}
