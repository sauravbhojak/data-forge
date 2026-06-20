import { memo, useCallback } from 'react'
import { Trash2, ChevronUp, ChevronDown } from 'lucide-react'
import clsx from 'clsx'
import type { FieldDefinition, FieldType } from '@/types'
import { FIELD_TYPES, FIELD_TYPE_LABELS, NUMERIC_FIELD_TYPES } from '@/types'

interface FieldRowProps {
  field: FieldDefinition
  index: number
  total: number
  onChange: (index: number, updated: FieldDefinition) => void
  onRemove: (index: number) => void
  onMoveUp: (index: number) => void
  onMoveDown: (index: number) => void
}

const FIELD_TYPE_OPTIONS = FIELD_TYPES.map((ft) => ({
  value: ft,
  label: FIELD_TYPE_LABELS[ft],
})).sort((a, b) => a.label.localeCompare(b.label))

export const FieldRow = memo(function FieldRow({
  field,
  index,
  total,
  onChange,
  onRemove,
  onMoveUp,
  onMoveDown,
}: FieldRowProps) {
  const isNumeric = NUMERIC_FIELD_TYPES.includes(field.field_type)

  const update = useCallback(
    (patch: Partial<FieldDefinition>) => {
      onChange(index, { ...field, ...patch })
    },
    [field, index, onChange]
  )

  return (
    <div className="group relative grid grid-cols-12 gap-2 rounded-lg border border-white/5 bg-surface-900/40 p-3 transition-colors hover:border-white/10 hover:bg-surface-900/60">
      {/* Drag handles */}
      <div className="col-span-1 flex flex-col items-center gap-0.5 pt-1">
        <span className="text-xs font-mono text-slate-600 select-none">{index + 1}</span>
        <button
          onClick={() => onMoveUp(index)}
          disabled={index === 0}
          className="rounded p-0.5 text-slate-600 hover:text-slate-400 disabled:opacity-30 disabled:cursor-not-allowed transition"
          aria-label="Move field up"
        >
          <ChevronUp className="h-3 w-3" />
        </button>
        <button
          onClick={() => onMoveDown(index)}
          disabled={index === total - 1}
          className="rounded p-0.5 text-slate-600 hover:text-slate-400 disabled:opacity-30 disabled:cursor-not-allowed transition"
          aria-label="Move field down"
        >
          <ChevronDown className="h-3 w-3" />
        </button>
      </div>

      {/* Field Name */}
      <div className="col-span-2">
        <label className="form-label">Field Name</label>
        <input
          className="form-input text-xs"
          value={field.name}
          placeholder="field_name"
          pattern="[a-zA-Z_][a-zA-Z0-9_]*"
          onChange={(e) => update({ name: e.target.value })}
          aria-label="Field name"
        />
      </div>

      {/* Field Type */}
      <div className="col-span-2">
        <label className="form-label">Type</label>
        <div className="relative">
          <select
            className="form-select text-xs pr-6"
            value={field.field_type}
            onChange={(e) => update({ field_type: e.target.value as FieldType })}
            aria-label="Field type"
          >
            {FIELD_TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Min / Max */}
      <div className="col-span-2 grid grid-cols-2 gap-1">
        <div>
          <label className="form-label">Min</label>
          <input
            type="number"
            className={clsx('form-input text-xs', !isNumeric && 'opacity-40 cursor-not-allowed')}
            value={field.min_value ?? ''}
            disabled={!isNumeric}
            placeholder="—"
            onChange={(e) => update({ min_value: e.target.value ? Number(e.target.value) : null })}
            aria-label="Minimum value"
          />
        </div>
        <div>
          <label className="form-label">Max</label>
          <input
            type="number"
            className={clsx('form-input text-xs', !isNumeric && 'opacity-40 cursor-not-allowed')}
            value={field.max_value ?? ''}
            disabled={!isNumeric}
            placeholder="—"
            onChange={(e) => update({ max_value: e.target.value ? Number(e.target.value) : null })}
            aria-label="Maximum value"
          />
        </div>
      </div>

      {/* Nullable / Unique / Sequential */}
      <div className="col-span-2 flex flex-col gap-2 pt-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            className="h-3.5 w-3.5 rounded border-white/20 bg-surface-900 accent-brand-500"
            checked={field.nullable ?? false}
            onChange={(e) => update({ nullable: e.target.checked })}
          />
          <span className="text-xs text-slate-400">Nullable</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            className="h-3.5 w-3.5 rounded border-white/20 bg-surface-900 accent-brand-500"
            checked={field.unique ?? false}
            onChange={(e) => update({ unique: e.target.checked })}
          />
          <span className="text-xs text-slate-400">Unique</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            className="h-3.5 w-3.5 rounded border-white/20 bg-surface-900 accent-brand-500"
            checked={field.sequential ?? false}
            onChange={(e) => update({ sequential: e.target.checked })}
          />
          <span className="text-xs text-slate-400">Sequential</span>
        </label>
      </div>

      {/* Default / Prefix / Suffix */}
      <div className="col-span-2 grid grid-cols-3 gap-1">
        <div>
          <label className="form-label">Default</label>
          <input
            className="form-input text-xs"
            value={field.default != null ? String(field.default) : ''}
            placeholder="—"
            onChange={(e) => update({ default: e.target.value || null })}
            aria-label="Default value"
          />
        </div>
        <div>
          <label className="form-label">Prefix</label>
          <input
            className="form-input text-xs"
            value={field.prefix ?? ''}
            placeholder="—"
            onChange={(e) => update({ prefix: e.target.value || null })}
            aria-label="Prefix"
          />
        </div>
        <div>
          <label className="form-label">Suffix</label>
          <input
            className="form-input text-xs"
            value={field.suffix ?? ''}
            placeholder="—"
            onChange={(e) => update({ suffix: e.target.value || null })}
            aria-label="Suffix"
          />
        </div>
      </div>

      {/* Remove */}
      <div className="col-span-1 flex items-start justify-end pt-6">
        <button
          onClick={() => onRemove(index)}
          className="rounded-lg p-1.5 text-slate-600 opacity-0 transition group-hover:opacity-100 hover:bg-red-500/20 hover:text-red-400"
          aria-label={`Remove field ${field.name}`}
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
})
