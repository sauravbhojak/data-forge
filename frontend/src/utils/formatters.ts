/**
 * Format a number with locale-appropriate thousands separators.
 */
export function formatNumber(n: number): string {
  return new Intl.NumberFormat('en-US').format(n)
}

/**
 * Format milliseconds into a human-readable duration string.
 */
export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms.toFixed(0)} ms`
  return `${(ms / 1000).toFixed(2)} s`
}

/**
 * Format bytes as MB with 2 decimal places.
 */
export function formatMemory(mb: number): string {
  return `${mb.toFixed(2)} MB`
}

/**
 * Truncate a string to maxLength with ellipsis.
 */
export function truncate(str: string, maxLength: number): string {
  return str.length > maxLength ? `${str.slice(0, maxLength)}…` : str
}

/**
 * Convert snake_case or camelCase to Title Case.
 */
export function toTitleCase(str: string): string {
  return str
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .replace(/^\w/, (c) => c.toUpperCase())
    .trim()
}

/**
 * Generate a safe, unique field key for React list rendering.
 */
export function fieldKey(tableName: string, fieldName: string): string {
  return `${tableName}.${fieldName}`
}

/**
 * Format a row count option as a human-readable string.
 */
export function formatRowCount(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(0)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`
  return String(n)
}

/**
 * Clamp a number between min and max.
 */
export function clamp(val: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, val))
}
