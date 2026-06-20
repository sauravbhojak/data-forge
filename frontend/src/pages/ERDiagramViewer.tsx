import { useState, useCallback } from 'react'
import { Plus, Trash2, Play, Network } from 'lucide-react'
import { Card, CardBody, CardHeader } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { ERDiagram } from '@/components/ERDiagram'
import { useGenerateERD } from '@/hooks/useGeneration'
import type { FieldDefinition, RelationshipDefinition, RelationshipType, TableSchema } from '@/types'
import { SchemaBuilder } from '@/components/SchemaBuilder'

const REL_TYPE_OPTIONS = [
  { value: 'one_to_many', label: 'One → Many' },
  { value: 'one_to_one', label: 'One → One' },
  { value: 'many_to_one', label: 'Many → One' },
]

interface TableState { id: string; name: string; fields: FieldDefinition[] }

const DEFAULT_TABLES: TableState[] = [
  {
    id: '1',
    name: 'Department',
    fields: [
      { name: 'dept_id', field_type: 'uuid', unique: true },
      { name: 'dept_name', field_type: 'department' },
    ],
  },
  {
    id: '2',
    name: 'Employee',
    fields: [
      { name: 'emp_id', field_type: 'uuid', unique: true },
      { name: 'name', field_type: 'full_name' },
      { name: 'email', field_type: 'email', unique: true },
      { name: 'dept_id', field_type: 'uuid' },
      { name: 'salary', field_type: 'salary' },
    ],
  },
]

const DEFAULT_RELS: RelationshipDefinition[] = [
  { parent_table: 'Department', parent_field: 'dept_id', child_table: 'Employee', child_field: 'dept_id', relationship_type: 'one_to_many' },
]

export default function ERDiagramViewer() {
  const [tables, setTables] = useState<TableState[]>(DEFAULT_TABLES)
  const [relationships, setRelationships] = useState<RelationshipDefinition[]>(DEFAULT_RELS)
  const [newRel, setNewRel] = useState<Partial<RelationshipDefinition>>({ relationship_type: 'one_to_many' })
  const [selected, setSelected] = useState<string>('1')

  const erdMutation = useGenerateERD()

  const tableOptions = tables.map((t) => ({ value: t.name, label: t.name }))

  const handleGenerate = useCallback(() => {
    const req = {
      tables: tables.map((t) => ({ name: t.name, fields: t.fields, row_count: 10 } as TableSchema)),
      relationships,
    }
    erdMutation.mutate(req)
  }, [tables, relationships, erdMutation])

  const addTable = () => {
    const t: TableState = { id: crypto.randomUUID(), name: `Table${tables.length + 1}`, fields: [{ name: 'id', field_type: 'uuid', unique: true }] }
    setTables((prev) => [...prev, t])
  }

  const addRel = () => {
    if (!newRel.parent_table || !newRel.child_table || !newRel.parent_field || !newRel.child_field) return
    setRelationships((prev) => [...prev, newRel as RelationshipDefinition])
    setNewRel({ relationship_type: 'one_to_many' })
  }

  const selectedTable = tables.find((t) => t.id === selected)

  return (
    <div className="flex flex-col gap-6 p-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">ER Diagram Viewer</h1>
        <p className="text-slate-500 mt-1">Visualize your schema as a Mermaid entity-relationship diagram.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        {/* Config panel */}
        <div className="xl:col-span-1 flex flex-col gap-4">
          {/* Tables */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-slate-300">Tables</h2>
                <Button variant="ghost" size="sm" icon={<Plus className="h-4 w-4" />} onClick={addTable} id="erd-add-table-btn">Add</Button>
              </div>
            </CardHeader>
            <CardBody className="flex flex-col gap-2">
              {tables.map((t) => (
                <div
                  key={t.id}
                  className={`flex items-center justify-between rounded-lg border px-3 py-2 cursor-pointer transition-all ${selected === t.id ? 'border-brand-500/40 bg-brand-500/10' : 'border-white/5 hover:border-white/15'}`}
                  onClick={() => setSelected(t.id)}
                >
                  <div>
                    <p className="text-sm font-medium text-slate-200">{t.name}</p>
                    <p className="text-xs text-slate-500">{t.fields.length} fields</p>
                  </div>
                  <button onClick={(e) => { e.stopPropagation(); setTables((p) => p.filter((tt) => tt.id !== t.id)) }} disabled={tables.length <= 1} className="text-slate-600 hover:text-red-400 disabled:opacity-30">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </CardBody>
          </Card>

          {/* Field editor for selected table */}
          {selectedTable && (
            <Card>
              <CardHeader><h2 className="text-sm font-semibold text-slate-300">{selectedTable.name} Fields</h2></CardHeader>
              <CardBody>
                <SchemaBuilder
                  fields={selectedTable.fields}
                  onChange={(fields) => setTables((prev) => prev.map((t) => t.id === selected ? { ...t, fields } : t))}
                />
              </CardBody>
            </Card>
          )}

          {/* Relationships */}
          <Card>
            <CardHeader><h2 className="text-sm font-semibold text-slate-300">Relationships</h2></CardHeader>
            <CardBody className="flex flex-col gap-3">
              <div className="grid grid-cols-2 gap-2">
                <Select label="Parent" options={tableOptions} value={newRel.parent_table ?? ''} onChange={(e) => setNewRel((r) => ({ ...r, parent_table: e.target.value }))} />
                <input className="form-input text-xs" placeholder="parent field" value={newRel.parent_field ?? ''} onChange={(e) => setNewRel((r) => ({ ...r, parent_field: e.target.value }))} />
                <Select label="Child" options={tableOptions} value={newRel.child_table ?? ''} onChange={(e) => setNewRel((r) => ({ ...r, child_table: e.target.value }))} />
                <input className="form-input text-xs" placeholder="FK field" value={newRel.child_field ?? ''} onChange={(e) => setNewRel((r) => ({ ...r, child_field: e.target.value }))} />
                <div className="col-span-2"><Select options={REL_TYPE_OPTIONS} value={newRel.relationship_type ?? 'one_to_many'} onChange={(e) => setNewRel((r) => ({ ...r, relationship_type: e.target.value as RelationshipType }))} /></div>
              </div>
              <Button variant="ghost" size="sm" icon={<Plus className="h-4 w-4" />} onClick={addRel} id="erd-add-rel-btn">Add Relationship</Button>
              {relationships.map((r, i) => (
                <div key={i} className="flex items-center justify-between text-xs text-slate-400 border border-white/5 rounded-lg px-3 py-2">
                  <span className="font-mono">{r.parent_table} → {r.child_table}</span>
                  <button onClick={() => setRelationships((p) => p.filter((_, idx) => idx !== i))} className="text-slate-600 hover:text-red-400"><Trash2 className="h-3.5 w-3.5" /></button>
                </div>
              ))}
            </CardBody>
          </Card>

          <Button onClick={handleGenerate} loading={erdMutation.isPending} icon={<Network className="h-4 w-4" />} id="generate-erd-btn">Generate ER Diagram</Button>
        </div>

        {/* Diagram */}
        <div className="xl:col-span-2">
          <Card className="h-full">
            <CardHeader><h2 className="text-sm font-semibold text-slate-300">Entity-Relationship Diagram</h2></CardHeader>
            <CardBody>
              {erdMutation.data ? (
                <ERDiagram mermaidText={erdMutation.data.mermaid} height={550} />
              ) : (
                <div className="flex h-80 items-center justify-center text-center">
                  <div>
                    <Network className="mx-auto mb-3 h-12 w-12 text-slate-700" />
                    <p className="text-slate-500">Click "Generate ER Diagram" to visualize your schema</p>
                  </div>
                </div>
              )}
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  )
}
