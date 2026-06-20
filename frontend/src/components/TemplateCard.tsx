import { memo } from 'react'
import { Users, Activity, TrendingUp, ShoppingCart, Shield, Briefcase, Database } from 'lucide-react'
import clsx from 'clsx'
import type { TemplateInfo } from '@/types'
import { Badge } from '@/components/ui/Badge'

interface TemplateCardProps {
  template: TemplateInfo
  selected?: boolean
  onSelect: (id: string) => void
}

const ICON_MAP: Record<string, React.ReactNode> = {
  users: <Users className="h-6 w-6" />,
  activity: <Activity className="h-6 w-6" />,
  'trending-up': <TrendingUp className="h-6 w-6" />,
  'shopping-cart': <ShoppingCart className="h-6 w-6" />,
  shield: <Shield className="h-6 w-6" />,
  briefcase: <Briefcase className="h-6 w-6" />,
  database: <Database className="h-6 w-6" />,
}

export const TemplateCard = memo(function TemplateCard({
  template,
  selected = false,
  onSelect,
}: TemplateCardProps) {
  return (
    <button
      onClick={() => onSelect(template.id)}
      id={`template-${template.id}`}
      className={clsx(
        'group relative flex flex-col gap-4 rounded-xl border p-5 text-left transition-all duration-200 w-full',
        selected
          ? 'border-brand-500/60 bg-brand-500/10 shadow-brand-md'
          : 'border-white/5 bg-surface-800/40 hover:border-brand-500/30 hover:bg-surface-800/60'
      )}
      aria-pressed={selected}
    >
      {/* Icon + Name */}
      <div className="flex items-start gap-3">
        <div className={clsx(
          'rounded-xl p-2.5 transition-colors',
          selected
            ? 'bg-brand-500/25 text-brand-300'
            : 'bg-white/5 text-slate-400 group-hover:bg-brand-500/15 group-hover:text-brand-300'
        )}>
          {ICON_MAP[template.icon] ?? <Users className="h-6 w-6" />}
        </div>
        <div>
          <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
            {template.name}
            {template.template_type === 'relational' && (
              <Badge variant="brand" className="text-[10px] px-1.5 py-0 h-4">Relational</Badge>
            )}
          </h3>
          {template.template_type === 'relational' ? (
            <p className="text-xs text-slate-500 mt-0.5">{template.table_count || template.tables?.length || 0} tables &bull; {template.relationship_count || template.relationships?.length || 0} relationships</p>
          ) : (
            <p className="text-xs text-slate-500 mt-0.5">{template.field_count || template.fields?.length || 0} fields</p>
          )}
        </div>
        {selected && (
          <div className="absolute right-4 top-4 h-2 w-2 rounded-full bg-brand-500 animate-pulse-slow" />
        )}
      </div>

      {/* Description */}
      <p className="text-xs text-slate-400 leading-relaxed">{template.description}</p>

      {/* Field list */}
      <div className="flex flex-wrap gap-1">
        {template.template_type === 'relational' ? (
          template.tables?.slice(0, 6).map((t) => (
            <span key={t.name} className="rounded-md bg-white/5 px-1.5 py-0.5 text-xs font-mono text-slate-500">
              {t.name}
            </span>
          ))
        ) : (
          template.field_names?.slice(0, 6).map((f) => (
            <span key={f} className="rounded-md bg-white/5 px-1.5 py-0.5 text-xs font-mono text-slate-500">
              {f}
            </span>
          ))
        )}
        {template.template_type === 'relational' && template.tables && template.tables.length > 6 && (
          <span className="text-xs text-slate-600">+{template.tables.length - 6} more</span>
        )}
        {template.template_type !== 'relational' && template.field_names && template.field_names.length > 6 && (
          <span className="text-xs text-slate-600">+{template.field_names.length - 6} more</span>
        )}
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-1">
        {template.tags.map((tag) => (
          <Badge key={tag} variant={selected ? 'brand' : 'default'}>{tag}</Badge>
        ))}
      </div>
    </button>
  )
})
