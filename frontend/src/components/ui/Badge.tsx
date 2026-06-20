import clsx from 'clsx'

type BadgeVariant = 'default' | 'brand' | 'success' | 'warning' | 'danger' | 'info'

interface BadgeProps {
  variant?: BadgeVariant
  children: React.ReactNode
  className?: string
}

const variantStyles: Record<BadgeVariant, string> = {
  default: 'bg-white/10 text-slate-300',
  brand: 'bg-brand-500/20 text-brand-300 border border-brand-500/20',
  success: 'bg-green-500/15 text-green-400 border border-green-500/20',
  warning: 'bg-amber-500/15 text-amber-400 border border-amber-500/20',
  danger: 'bg-red-500/15 text-red-400 border border-red-500/20',
  info: 'bg-sky-500/15 text-sky-400 border border-sky-500/20',
}

export function Badge({ variant = 'default', children, className }: BadgeProps) {
  return (
    <span className={clsx('badge', variantStyles[variant], className)}>
      {children}
    </span>
  )
}
