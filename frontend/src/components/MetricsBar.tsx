import { memo } from 'react'
import { Zap, Cpu, Table2, Clock } from 'lucide-react'
import type { GenerationMetrics } from '@/types'
import { formatDuration, formatMemory, formatNumber } from '@/utils/formatters'

interface MetricsBarProps {
  metrics: GenerationMetrics
  className?: string
}

export const MetricsBar = memo(function MetricsBar({ metrics, className }: MetricsBarProps) {
  return (
    <div className={`flex flex-wrap gap-4 rounded-xl border border-brand-500/20 bg-brand-500/5 px-5 py-3 ${className ?? ''}`}>
      <MetricItem
        icon={<Table2 className="h-4 w-4 text-brand-400" />}
        label="Rows"
        value={formatNumber(metrics.row_count)}
      />
      <MetricItem
        icon={<Table2 className="h-4 w-4 text-violet-400" />}
        label="Fields"
        value={String(metrics.field_count)}
      />
      <MetricItem
        icon={<Clock className="h-4 w-4 text-green-400" />}
        label="Generation Time"
        value={formatDuration(metrics.generation_time_ms)}
      />
      <MetricItem
        icon={<Cpu className="h-4 w-4 text-amber-400" />}
        label="Memory Delta"
        value={formatMemory(metrics.memory_delta_mb)}
      />
    </div>
  )
})

function MetricItem({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-2">
      {icon}
      <div>
        <p className="text-xs text-slate-500">{label}</p>
        <p className="text-sm font-semibold font-mono text-slate-200">{value}</p>
      </div>
    </div>
  )
}
