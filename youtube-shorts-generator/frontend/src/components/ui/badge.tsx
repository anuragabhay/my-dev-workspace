import { type HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'secondary' | 'success' | 'destructive' | 'outline'
}

function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        {
          default: 'bg-zinc-900 text-zinc-50 dark:bg-zinc-50 dark:text-zinc-900',
          secondary: 'bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100',
          success: 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400',
          destructive: 'bg-red-500/20 text-red-600 dark:text-red-400',
          outline: 'border border-zinc-300 dark:border-zinc-700',
        }[variant],
        className
      )}
      {...props}
    />
  )
}

export { Badge }
