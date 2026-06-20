import { useCallback, useMemo } from 'react'
import { Plus, Wand2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { FieldRow } from '@/components/FieldRow'
import type { FieldDefinition } from '@/types'

interface SchemaBuilderProps {
  fields: FieldDefinition[]
  onChange: (fields: FieldDefinition[]) => void
  maxFields?: number
}

const DEFAULT_FIELD: Omit<FieldDefinition, 'name'> = {
  field_type: 'text',
  nullable: false,
  unique: false,
  sequential: false,
}

export function SchemaBuilder({ fields, onChange, maxFields = 100 }: SchemaBuilderProps) {
  const addField = useCallback(() => {
    if (fields.length >= maxFields) return
    const newField: FieldDefinition = {
      ...DEFAULT_FIELD,
      name: `field_${fields.length + 1}`,
    }
    onChange([...fields, newField])
  }, [fields, onChange, maxFields])

  const removeField = useCallback(
    (index: number) => {
      onChange(fields.filter((_, i) => i !== index))
    },
    [fields, onChange]
  )

  const updateField = useCallback(
    (index: number, updated: FieldDefinition) => {
      const next = [...fields]
      next[index] = updated
      onChange(next)
    },
    [fields, onChange]
  )

  const moveUp = useCallback(
    (index: number) => {
      if (index === 0) return
      const next = [...fields]
      ;[next[index - 1], next[index]] = [next[index], next[index - 1]]
      onChange(next)
    },
    [fields, onChange]
  )

  const moveDown = useCallback(
    (index: number) => {
      if (index === fields.length - 1) return
      const next = [...fields]
      ;[next[index], next[index + 1]] = [next[index + 1], next[index]]
      onChange(next)
    },
    [fields, onChange]
  )

  const fieldCount = fields.length

  return (
    <div className="flex flex-col gap-3">
      {/* Header row */}
      <div className="grid grid-cols-12 gap-2 px-3 text-xs font-medium text-slate-500 uppercase tracking-wide">
        <div className="col-span-1">#</div>
        <div className="col-span-2">Name</div>
        <div className="col-span-2">Type</div>
        <div className="col-span-2">Range</div>
        <div className="col-span-2">Options</div>
        <div className="col-span-2">Default / Wrap</div>
        <div className="col-span-1" />
      </div>

      {/* Field rows */}
      {fields.length === 0 ? (
        <div className="rounded-lg border border-dashed border-white/10 p-10 text-center">
          <Wand2 className="mx-auto mb-3 h-8 w-8 text-slate-600" />
          <p className="text-sm text-slate-500">
            No fields yet. Add a field to start building your schema.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {fields.map((field, idx) => (
            <FieldRow
              key={idx}
              field={field}
              index={idx}
              total={fieldCount}
              onChange={updateField}
              onRemove={removeField}
              onMoveUp={moveUp}
              onMoveDown={moveDown}
            />
          ))}
        </div>
      )}

      {/* Add field button */}
      <div className="flex items-center justify-between pt-1">
        <Button
          variant="ghost"
          size="sm"
          icon={<Plus className="h-4 w-4" />}
          onClick={addField}
          disabled={fieldCount >= maxFields}
          id="add-field-btn"
        >
          Add Field
        </Button>
        <span className="text-xs text-slate-600">
          {fieldCount} / {maxFields} fields
        </span>
      </div>
    </div>
  )
}
