import { cn } from '@/lib/utils'

interface ProgressProps {
  value?: number
  className?: string
}

function Progress({ value = 0, className }: ProgressProps) {
  return (
    <div
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={100}
      className={cn('h-2 w-full overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-800', className)}
    >
      <div
        className="h-full bg-zinc-900 transition-all duration-300 dark:bg-zinc-50"
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  )
}

export { Progress }
