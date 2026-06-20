import { useState, useMemo, useCallback } from 'react'
import { Play, Download, Code2, RefreshCw } from 'lucide-react'
import { Card, CardBody, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { SchemaBuilder } from '@/components/SchemaBuilder'
import { DataGrid } from '@/components/DataGrid'
import { MetricsBar } from '@/components/MetricsBar'
import { SQLViewer } from '@/components/SQLViewer'
import { ExportPanel } from '@/components/ExportPanel'
import { usePreview, useGenerateSchema } from '@/hooks/useGeneration'
import type { FieldDefinition, SQLDialect, TableSchema } from '@/types'
import { ROW_COUNT_OPTIONS, formatRowCount } from '@/types'

const ROW_OPTIONS = ROW_COUNT_OPTIONS.map((n) => ({ value: String(n), label: `${formatRowCount(n)} rows` }))

const DIALECT_OPTIONS: { value: SQLDialect; label: string }[] = [
  { value: 'postgresql', label: 'PostgreSQL' },
  { value: 'mysql', label: 'MySQL' },
  { value: 'sqlite', label: 'SQLite' },
  { value: 'sqlserver', label: 'SQL Server' },
]

const INITIAL_FIELDS: FieldDefinition[] = [
  { name: 'id', field_type: 'uuid', unique: true, nullable: false },
  { name: 'full_name', field_type: 'full_name', nullable: false },
  { name: 'email', field_type: 'email', unique: true, nullable: false },
  { name: 'age', field_type: 'age', min_value: 18, max_value: 80, nullable: false },
]

type ActiveTab = 'preview' | 'sql' | 'export'

export default function CustomSchemaBuilder() {
  const [tableName, setTableName] = useState('my_table')
  const [rowCount, setRowCount] = useState(50)
  const [fields, setFields] = useState<FieldDefinition[]>(INITIAL_FIELDS)
  const [dialect, setDialect] = useState<SQLDialect>('postgresql')
  const [activeTab, setActiveTab] = useState<ActiveTab>('preview')

  const previewMutation = usePreview()
  const schemaMutation = useGenerateSchema()

  const schema = useMemo<TableSchema>(
    () => ({ name: tableName || 'my_table', fields, row_count: rowCount }),
    [tableName, fields, rowCount]
  )

  const handlePreview = useCallback(() => {
    previewMutation.mutate(schema)
    setActiveTab('preview')
  }, [schema, previewMutation])

  const handleGenerateSQL = useCallback(() => {
    schemaMutation.mutate({ tables: [schema], dialect, include_inserts: true, sample_rows: 5 })
    setActiveTab('sql')
  }, [schema, dialect, schemaMutation])

  const preview = previewMutation.data
  const sqlData = schemaMutation.data

  const TABS = [
    { id: 'preview' as ActiveTab, label: 'Preview', icon: <Play className="h-4 w-4" /> },
    { id: 'sql' as ActiveTab, label: 'SQL DDL', icon: <Code2 className="h-4 w-4" /> },
    { id: 'export' as ActiveTab, label: 'Export', icon: <Download className="h-4 w-4" /> },
  ]

  return (
    <div className="flex flex-col gap-6 p-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Custom Schema Builder</h1>
        <p className="text-slate-500 mt-1">Define your own table schema with any combination of 40+ field types.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-5">
        {/* Schema panel */}
        <div className="xl:col-span-3 flex flex-col gap-4">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <label className="form-label">Table Name</label>
                  <input
                    className="form-input"
                    value={tableName}
                    onChange={(e) => setTableName(e.target.value.replace(/[^a-zA-Z0-9_]/g, '_'))}
                    placeholder="my_table"
                    pattern="[a-zA-Z_][a-zA-Z0-9_]*"
                    id="table-name-input"
                  />
                </div>
                <div className="w-40">
                  <Select
                    label="Row Count"
                    options={ROW_OPTIONS}
                    value={String(rowCount)}
                    onChange={(e) => setRowCount(Number(e.target.value))}
                    id="custom-row-count"
                  />
                </div>
              </div>
            </CardHeader>
            <CardBody>
              <SchemaBuilder fields={fields} onChange={setFields} />
            </CardBody>
          </Card>

          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            <Button
              onClick={handlePreview}
              loading={previewMutation.isPending}
              disabled={fields.length === 0}
              icon={<Play className="h-4 w-4" />}
              id="custom-preview-btn"
            >
              Preview
            </Button>
            <Select
              options={DIALECT_OPTIONS}
              value={dialect}
              onChange={(e) => setDialect(e.target.value as SQLDialect)}
              aria-label="SQL dialect"
            />
            <Button
              variant="ghost"
              onClick={handleGenerateSQL}
              loading={schemaMutation.isPending}
              disabled={fields.length === 0}
              icon={<Code2 className="h-4 w-4" />}
              id="generate-sql-btn"
            >
              Generate SQL
            </Button>
            <Button
              variant="ghost"
              size="sm"
              icon={<RefreshCw className="h-4 w-4" />}
              onClick={() => { previewMutation.reset(); schemaMutation.reset() }}
              id="reset-btn"
            >
              Reset
            </Button>
          </div>

          {/* Metrics */}
          {preview?.metrics && <MetricsBar metrics={preview.metrics} />}
        </div>

        {/* Right: Results panel */}
        <div className="xl:col-span-2 flex flex-col gap-4">
          {/* Tab bar */}
          <div className="flex rounded-lg border border-white/5 bg-surface-900/50 p-1">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                id={`tab-${tab.id}`}
                className={`flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-2 text-xs font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-brand-500/20 text-brand-300 shadow-brand-sm'
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          {activeTab === 'preview' && (
            <DataGrid
              columns={preview?.columns ?? []}
              rows={preview?.rows ?? []}
              height={500}
              loading={previewMutation.isPending}
            />
          )}

          {activeTab === 'sql' && (
            <div className="flex flex-col gap-3">
              {sqlData?.ddl && (
                <SQLViewer sql={sqlData.ddl} title={`DDL — ${dialect}`} maxHeight={250} />
              )}
              {sqlData?.insert_statements && (
                <SQLViewer sql={sqlData.insert_statements} title="Sample Inserts" maxHeight={250} />
              )}
              {!sqlData && !schemaMutation.isPending && (
                <div className="rounded-xl border border-dashed border-white/10 p-10 text-center">
                  <Code2 className="mx-auto mb-2 h-8 w-8 text-slate-600" />
                  <p className="text-sm text-slate-500">Click "Generate SQL" to see the DDL</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'export' && (
            <Card>
              <CardBody>
                <ExportPanel table={fields.length > 0 ? schema : null} />
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
