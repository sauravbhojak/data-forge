import { memo } from 'react'
import { Trash2 } from 'lucide-react'
import { Select } from '@/components/ui/Select'
import { Badge } from '@/components/ui/Badge'
import type { RelationshipDefinition, RelationshipType } from '@/types'

interface RelationshipBuilderProps {
  relationships: RelationshipDefinition[]
  tableNames: string[]
  onChange: (rels: RelationshipDefinition[]) => void
}

const REL_TYPE_OPTIONS = [
  { value: 'one_to_one', label: 'One → One' },
  { value: 'one_to_many', label: 'One → Many' },
  { value: 'many_to_one', label: 'Many → One' },
]

const REL_BADGE: Record<RelationshipType, 'brand' | 'info' | 'success'> = {
  one_to_one: 'success',
  one_to_many: 'brand',
  many_to_one: 'info',
}

export const RelationshipBuilder = memo(function RelationshipBuilder({
  relationships,
  tableNames,
  onChange,
}: RelationshipBuilderProps) {
  const tableOptions = tableNames.map((n) => ({ value: n, label: n }))

  const update = (i: number, patch: Partial<RelationshipDefinition>) => {
    const next = [...relationships]
    next[i] = { ...next[i], ...patch }
    onChange(next)
  }

  const remove = (i: number) => {
    onChange(relationships.filter((_, idx) => idx !== i))
  }

  if (relationships.length === 0) {
    return (
      <p className="text-sm text-slate-500 py-4 text-center">
        No relationships defined. Add tables first, then define FK relationships.
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      {relationships.map((rel, i) => (
        <div key={i} className="grid grid-cols-11 gap-2 items-end rounded-lg border border-white/5 p-3">
          <div className="col-span-3">
            <Select
              label="Parent Table"
              options={tableOptions}
              value={rel.parent_table}
              onChange={(e) => update(i, { parent_table: e.target.value })}
            />
          </div>
          <div className="col-span-2">
            <label className="form-label">Parent Field</label>
            <input
              className="form-input text-xs"
              value={rel.parent_field}
              onChange={(e) => update(i, { parent_field: e.target.value })}
              placeholder="id"
            />
          </div>
          <div className="col-span-2">
            <Select
              label="Cardinality"
              options={REL_TYPE_OPTIONS}
              value={rel.relationship_type}
              onChange={(e) => update(i, { relationship_type: e.target.value as RelationshipType })}
            />
          </div>
          <div className="col-span-2">
            <Select
              label="Child Table"
              options={tableOptions}
              value={rel.child_table}
              onChange={(e) => update(i, { child_table: e.target.value })}
            />
          </div>
          <div className="col-span-1">
            <label className="form-label">FK Field</label>
            <input
              className="form-input text-xs"
              value={rel.child_field}
              onChange={(e) => update(i, { child_field: e.target.value })}
              placeholder="parent_id"
            />
          </div>
          <div className="col-span-1 flex justify-end">
            <button
              onClick={() => remove(i)}
              className="rounded-lg p-1.5 text-slate-600 hover:bg-red-500/20 hover:text-red-400 transition"
              aria-label="Remove relationship"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  )
})
