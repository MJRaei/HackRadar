'use client'

import { useEffect, useRef } from 'react'
import { Button } from './Button'

interface ConfirmDialogProps {
  isOpen: boolean
  title: string
  message: string
  confirmLabel?: string
  onConfirm: () => void
  onCancel: () => void
  loading?: boolean
}

export function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmLabel = 'Delete',
  onConfirm,
  onCancel,
  loading,
}: ConfirmDialogProps) {
  const ref = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    if (isOpen) {
      ref.current?.showModal()
    } else {
      ref.current?.close()
    }
  }, [isOpen])

  return (
    <dialog
      ref={ref}
      onCancel={onCancel}
      className="rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-xl p-0 max-w-sm w-full backdrop:bg-zinc-950/40 backdrop:backdrop-blur-sm"
      style={{ margin: 'auto' }}
    >
      <div className="p-6">
        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 mb-2">{title}</h2>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">{message}</p>
      </div>
      <div className="flex justify-end gap-2 px-6 pb-6">
        <Button variant="outline" size="sm" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
        <Button
          variant="primary"
          size="sm"
          loading={loading}
          onClick={onConfirm}
          className="bg-red-600 hover:bg-red-700"
        >
          {confirmLabel}
        </Button>
      </div>
    </dialog>
  )
}
