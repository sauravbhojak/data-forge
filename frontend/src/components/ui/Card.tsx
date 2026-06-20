import clsx from 'clsx'
import { HTMLAttributes } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean
  glow?: boolean
}

export function Card({ hover = false, glow = false, className, children, ...props }: CardProps) {
  return (
    <div
      className={clsx(
        'glass-card',
        hover && 'transition-all duration-200 hover:border-brand-500/30 hover:shadow-brand-sm cursor-pointer',
        glow && 'shadow-brand-glow',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {}

export function CardHeader({ className, children, ...props }: CardHeaderProps) {
  return (
    <div className={clsx('border-b border-white/5 px-5 py-4', className)} {...props}>
      {children}
    </div>
  )
}

interface CardBodyProps extends HTMLAttributes<HTMLDivElement> {}

export function CardBody({ className, children, ...props }: CardBodyProps) {
  return (
    <div className={clsx('p-5', className)} {...props}>
      {children}
    </div>
  )
}
