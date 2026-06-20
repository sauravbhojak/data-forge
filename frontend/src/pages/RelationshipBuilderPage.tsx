import { useState, useCallback, useMemo, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { Plus, Trash2, GitBranch, Play, Network } from 'lucide-react'
import { Card, CardBody, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { SchemaBuilder } from '@/components/SchemaBuilder'
import { DataGrid } from '@/components/DataGrid'
import { useGenerateRelations } from '@/hooks/useGeneration'
import type { FieldDefinition, RelationshipDefinition, RelationshipType, TableSchema, TemplateInfo } from '@/types'
import { ROW_COUNT_OPTIONS, formatRowCount } from '@/types'

const ROW_OPTIONS = ROW_COUNT_OPTIONS.slice(0, 5).map((n) => ({ value: String(n), label: `${formatRowCount(n)} rows` }))

const REL_TYPE_OPTIONS = [
  { value: 'one_to_many', label: 'One → Many' },
  { value: 'one_to_one', label: 'One → One' },
  { value: 'many_to_one', label: 'Many → One' },
]

interface TableState {
  id: string
  name: string
  rowCount: number
  fields: FieldDefinition[]
}

const DEFAULT_TABLE = (n: number): TableState => ({
  id: crypto.randomUUID(),
  name: `table_${n}`,
  rowCount: 100,
  fields: [
    { name: 'id', field_type: 'uuid', unique: true, nullable: false },
    { name: 'name', field_type: 'full_name', nullable: false },
  ],
})

export default function RelationshipBuilderPage() {
  const location = useLocation()
  const [tables, setTables] = useState<TableState[]>([DEFAULT_TABLE(1), DEFAULT_TABLE(2)])
  const [relationships, setRelationships] = useState<RelationshipDefinition[]>([])
  const [selectedTable, setSelectedTable] = useState<string | null>(tables[0]?.id ?? null)
  const [newRel, setNewRel] = useState<Partial<RelationshipDefinition>>({ relationship_type: 'one_to_many' })
  const [previewTable, setPreviewTable] = useState<string | null>(null)

  useEffect(() => {
    const template = location.state?.template as TemplateInfo | undefined
    if (template?.template_type === 'relational' && template.tables) {
      const newTables = template.tables.map((t) => ({
        id: crypto.randomUUID(),
        name: t.name,
        rowCount: t.row_count,
        fields: t.fields || [],
      }))
      setTables(newTables)
      setRelationships(template.relationships || [])
      setSelectedTable(newTables[0]?.id ?? null)
      
      // Clear the location state to prevent re-triggering on subsequent renders
      window.history.replaceState(null, '')
    }
  }, [location.state])

  const relMutation = useGenerateRelations()

  const addTable = useCallback(() => {
    const t = DEFAULT_TABLE(tables.length + 1)
    setTables((prev) => [...prev, t])
  }, [tables.length])

  const removeTable = useCallback((id: string) => {
    setTables((prev) => prev.filter((t) => t.id !== id))
    setRelationships((prev) => prev.filter((r) => {
      const t = tables.find((tt) => tt.id === id)
      return !t || (r.parent_table !== t.name && r.child_table !== t.name)
    }))
  }, [tables])

  const updateTable = useCallback((id: string, patch: Partial<TableState>) => {
    setTables((prev) => prev.map((t) => t.id === id ? { ...t, ...patch } : t))
  }, [])

  const addRelationship = useCallback(() => {
    if (!newRel.parent_table || !newRel.child_table || !newRel.parent_field || !newRel.child_field) return
    const rel: RelationshipDefinition = {
      parent_table: newRel.parent_table!,
      parent_field: newRel.parent_field!,
      child_table: newRel.child_table!,
      child_field: newRel.child_field!,
      relationship_type: (newRel.relationship_type as RelationshipType) ?? 'one_to_many',
    }
    setRelationships((prev) => [...prev, rel])
    setNewRel({ relationship_type: 'one_to_many' })
  }, [newRel])

  const tableOptions = tables.map((t) => ({ value: t.name, label: t.name }))

  const selectedTableState = tables.find((t) => t.id === selectedTable)

  const handleGenerate = useCallback(() => {
    const schemaRequest = {
      tables: tables.map((t) => ({
        name: t.name,
        fields: t.fields,
        row_count: t.rowCount,
      })),
      relationships,
    }
    relMutation.mutate(schemaRequest)
    setPreviewTable(tables[0]?.name ?? null)
  }, [tables, relationships, relMutation])

  const previewData = relMutation.data

  return (
    <div className="flex flex-col gap-6 p-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Relationship Builder</h1>
        <p className="text-slate-500 mt-1">Generate multi-table datasets with referential integrity.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        {/* Table list */}
        <div className="xl:col-span-1 flex flex-col gap-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-slate-300">Tables ({tables.length})</h2>
                <Button variant="ghost" size="sm" icon={<Plus className="h-4 w-4" />} onClick={addTable} id="add-table-btn">
                  Add Table
                </Button>
              </div>
            </CardHeader>
            <CardBody className="flex flex-col gap-2">
              {tables.map((t) => (
                <div
                  key={t.id}
                  className={`flex items-center justify-between rounded-lg border px-3 py-2 cursor-pointer transition-all ${
                    selectedTable === t.id ? 'border-brand-500/40 bg-brand-500/10' : 'border-white/5 hover:border-white/15'
                  }`}
                  onClick={() => setSelectedTable(t.id)}
                >
                  <div>
                    <p className="text-sm font-medium text-slate-200">{t.name}</p>
                    <p className="text-xs text-slate-500">{t.fields.length} fields · {formatRowCount(t.rowCount)} rows</p>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); removeTable(t.id) }}
                    disabled={tables.length <= 2}
                    className="text-slate-600 hover:text-red-400 disabled:opacity-30 transition"
                    aria-label={`Remove table ${t.name}`}
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </CardBody>
          </Card>

          {/* Relationships */}
          <Card>
            <CardHeader>
              <h2 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                <GitBranch className="h-4 w-4 text-brand-400" /> Relationships
              </h2>
            </CardHeader>
            <CardBody className="flex flex-col gap-4">
              {/* Add relationship form */}
              <div className="grid grid-cols-2 gap-2">
                <Select
                  label="Parent Table"
                  options={tableOptions}
                  value={newRel.parent_table ?? ''}
                  onChange={(e) => setNewRel((r) => ({ ...r, parent_table: e.target.value }))}
                />
                <Input
                  label="Parent Field"
                  value={newRel.parent_field ?? ''}
                  placeholder="id"
                  onChange={(e) => setNewRel((r) => ({ ...r, parent_field: e.target.value }))}
                />
                <Select
                  label="Child Table"
                  options={tableOptions}
                  value={newRel.child_table ?? ''}
                  onChange={(e) => setNewRel((r) => ({ ...r, child_table: e.target.value }))}
                />
                <Input
                  label="Child FK Field"
                  value={newRel.child_field ?? ''}
                  placeholder="parent_id"
                  onChange={(e) => setNewRel((r) => ({ ...r, child_field: e.target.value }))}
                />
                <div className="col-span-2">
                  <Select
                    label="Relationship Type"
                    options={REL_TYPE_OPTIONS}
                    value={newRel.relationship_type ?? 'one_to_many'}
                    onChange={(e) => setNewRel((r) => ({ ...r, relationship_type: e.target.value as RelationshipType }))}
                  />
                </div>
              </div>
              <Button variant="ghost" size="sm" icon={<Plus className="h-4 w-4" />} onClick={addRelationship} id="add-rel-btn">
                Add Relationship
              </Button>

              {/* Existing relationships */}
              {relationships.map((rel, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg border border-white/5 px-3 py-2 text-xs">
                  <span className="text-slate-300 font-mono">{rel.parent_table}.{rel.parent_field}</span>
                  <Badge variant="brand">{rel.relationship_type.replace(/_/g, ':')}</Badge>
                  <span className="text-slate-300 font-mono">{rel.child_table}.{rel.child_field}</span>
                  <button onClick={() => setRelationships((prev) => prev.filter((_, idx) => idx !== i))} className="text-slate-600 hover:text-red-400 transition">
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))}
            </CardBody>
          </Card>

          <Button onClick={handleGenerate} loading={relMutation.isPending} icon={<Play className="h-4 w-4" />} id="generate-relations-btn">
            Generate Data
          </Button>
        </div>

        {/* Schema editor + preview */}
        <div className="xl:col-span-2 flex flex-col gap-4">
          {selectedTableState && (
            <Card>
              <CardHeader>
                <div className="flex items-center gap-4">
                  <input
                    className="form-input flex-1 font-mono"
                    value={selectedTableState.name}
                    onChange={(e) => updateTable(selectedTableState.id, { name: e.target.value })}
                    aria-label="Table name"
                  />
                  <Select
                    options={ROW_OPTIONS}
                    value={String(selectedTableState.rowCount)}
                    onChange={(e) => updateTable(selectedTableState.id, { rowCount: Number(e.target.value) })}
                    aria-label="Row count"
                  />
                </div>
              </CardHeader>
              <CardBody>
                <SchemaBuilder
                  fields={selectedTableState.fields}
                  onChange={(fields) => updateTable(selectedTableState.id, { fields })}
                />
              </CardBody>
            </Card>
          )}

          {/* Preview */}
          {previewData && (
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  {previewData.tables.map((t) => (
                    <button
                      key={t}
                      onClick={() => setPreviewTable(t)}
                      className={`rounded-md px-3 py-1 text-xs font-medium transition ${
                        previewTable === t ? 'bg-brand-500/20 text-brand-300' : 'text-slate-500 hover:text-slate-300'
                      }`}
                    >
                      {t} <span className="text-slate-600">({previewData.row_counts[t]})</span>
                    </button>
                  ))}
                </div>
              </CardHeader>
              <CardBody className="p-0">
                {previewTable && previewData.preview[previewTable] && (
                  <DataGrid
                    columns={Object.keys(previewData.preview[previewTable][0] ?? {})}
                    rows={previewData.preview[previewTable]}
                    height={350}
                  />
                )}
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
