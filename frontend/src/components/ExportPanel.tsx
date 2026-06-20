import { useState } from 'react'
import { Download, FileText, Braces, Database, Table2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { useExport } from '@/hooks/useExport'
import type { ExportFormat, SQLDialect, TableSchema, TemplateInfo, DataQualityConfig } from '@/types'
import clsx from 'clsx'

interface ExportPanelProps {
  table?: TableSchema | null
  template?: TemplateInfo | null
  rowCount?: number
  quality?: DataQualityConfig
  compact?: boolean
}

const FORMAT_OPTIONS: { format: ExportFormat; label: string; icon: React.ReactNode; description: string }[] = [
  { format: 'csv', label: 'CSV', icon: <Table2 className="h-5 w-5" />, description: 'Universal spreadsheet format' },
  { format: 'json', label: 'JSON', icon: <Braces className="h-5 w-5" />, description: 'JavaScript Object Notation' },
  { format: 'sql', label: 'SQL', icon: <Database className="h-5 w-5" />, description: 'INSERT INTO statements' },
  { format: 'excel', label: 'Excel', icon: <FileText className="h-5 w-5" />, description: '.xlsx spreadsheet' },
]

const DIALECT_OPTIONS = [
  { value: 'postgresql', label: 'PostgreSQL' },
  { value: 'mysql', label: 'MySQL' },
  { value: 'sqlite', label: 'SQLite' },
  { value: 'sqlserver', label: 'SQL Server' },
]

export function ExportPanel({ table, template, rowCount, quality, compact = false }: ExportPanelProps) {
  const [dialect, setDialect] = useState<SQLDialect>('postgresql')
  const { isExporting, format: exportingFormat, exportTable, exportRelationalTemplate } = useExport()

  const handleExport = (format: ExportFormat) => {
    if (template && template.template_type === 'relational') {
      exportRelationalTemplate(
        template,
        format,
        rowCount ?? template.tables?.[0]?.row_count ?? 100,
        quality ?? { null_rate: 0, duplicate_rate: 0, outlier_rate: 0 },
        format === 'sql' ? dialect : undefined
      )
    } else if (table) {
      exportTable(table, format, format === 'sql' ? dialect : undefined)
    }
  }

  if (!table && !template) {
    return (
      <div className="rounded-xl border border-dashed border-white/10 p-8 text-center">
        <Download className="mx-auto mb-2 h-8 w-8 text-slate-600" />
        <p className="text-sm text-slate-500">Configure a schema to enable exports</p>
      </div>
    )
  }

  if (compact) {
    return (
      <div className="flex flex-wrap items-center gap-2">
        {FORMAT_OPTIONS.map(({ format, label, icon }) => (
          <Button
            key={format}
            variant="ghost"
            size="sm"
            icon={icon}
            loading={isExporting && exportingFormat === format}
            disabled={isExporting}
            onClick={() => handleExport(format)}
            id={`export-${format}-btn`}
          >
            {label}
          </Button>
        ))}
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      {/* SQL Dialect selector */}
      <div className="flex items-center gap-3">
        <span className="text-sm text-slate-400">SQL Dialect:</span>
        <div className="w-40">
          <Select
            options={DIALECT_OPTIONS}
            value={dialect}
            onChange={(e) => setDialect(e.target.value as SQLDialect)}
            aria-label="SQL dialect"
          />
        </div>
      </div>

      {/* Format grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {FORMAT_OPTIONS.map(({ format, label, icon, description }) => {
          const loading = isExporting && exportingFormat === format
          return (
            <button
              key={format}
              disabled={isExporting}
              onClick={() => handleExport(format)}
              id={`export-${format}-card-btn`}
              className={clsx(
                'group relative flex flex-col items-center gap-3 rounded-xl border p-5 text-center transition-all duration-200',
                'border-white/5 bg-surface-900/50 hover:border-brand-500/40 hover:bg-brand-500/5',
                isExporting && exportingFormat !== format && 'opacity-50',
                loading && 'border-brand-500/40 bg-brand-500/5'
              )}
            >
              <div className={clsx(
                'rounded-xl p-3 transition-colors',
                loading ? 'bg-brand-500/20 text-brand-300' : 'bg-white/5 text-slate-400 group-hover:bg-brand-500/15 group-hover:text-brand-300'
              )}>
                {loading ? (
                  <div className="h-5 w-5 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
                ) : icon}
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-200">{label}</p>
                <p className="text-xs text-slate-500">{description}</p>
              </div>
            </button>
          )
        })}
      </div>

      <p className="text-xs text-slate-600 text-center">
        {template?.template_type === 'relational' 
          ? `${template.tables?.length || 0} tables · ${template.relationships?.length || 0} relationships · ${template.name}`
          : table ? `${table.row_count.toLocaleString()} rows · ${table.fields.length} fields · ${table.name}` : ''}
      </p>
    </div>
  )
}
