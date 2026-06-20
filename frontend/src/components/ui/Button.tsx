import { forwardRef, ButtonHTMLAttributes } from 'react'
import clsx from 'clsx'
import { Spinner } from './Spinner'

type Variant = 'brand' | 'ghost' | 'danger' | 'success'
type Size = 'sm' | 'md' | 'lg'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  loading?: boolean
  icon?: React.ReactNode
  iconRight?: React.ReactNode
}

const variantStyles: Record<Variant, string> = {
  brand: 'btn-brand',
  ghost: 'btn-ghost',
  danger: 'btn-danger',
  success:
    'inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold ' +
    'bg-green-600/20 text-green-400 border border-green-500/20 transition-all duration-150 ' +
    'hover:bg-green-600/30 hover:text-green-300 active:scale-[0.98] ' +
    'disabled:opacity-50 disabled:cursor-not-allowed',
}

const sizeStyles: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'brand',
      size = 'md',
      loading = false,
      icon,
      iconRight,
      children,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={clsx(variantStyles[variant], sizeStyles[size], className)}
        {...props}
      >
        {loading ? <Spinner size="sm" /> : icon}
        {children}
        {!loading && iconRight}
      </button>
    )
  }
)

Button.displayName = 'Button'
