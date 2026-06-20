import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Play, Download, Database, Network } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Card, CardBody, CardHeader } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { TemplateCard } from '@/components/TemplateCard'
import { DataGrid } from '@/components/DataGrid'
import { MetricsBar } from '@/components/MetricsBar'
import { ExportPanel } from '@/components/ExportPanel'
import { api } from '@/services/api'
import { usePreview } from '@/hooks/useGeneration'
import { ROW_COUNT_OPTIONS, formatRowCount } from '@/types'
import type { DataQualityConfig, TableSchema } from '@/types'

const ROW_OPTIONS = ROW_COUNT_OPTIONS.map((n) => ({ value: String(n), label: `${formatRowCount(n)} rows` }))

const NULL_RATE_OPTIONS = [
  { value: '0', label: 'No nulls' },
  { value: '0.05', label: '5% nulls' },
  { value: '0.1', label: '10% nulls' },
  { value: '0.2', label: '20% nulls' },
]

const DUP_RATE_OPTIONS = [
  { value: '0', label: 'No duplicates' },
  { value: '0.05', label: '5% duplicates' },
  { value: '0.1', label: '10% duplicates' },
  { value: '0.2', label: '20% duplicates' },
]

const OUTLIER_RATE_OPTIONS = [
  { value: '0', label: 'No outliers' },
  { value: '0.02', label: '2% outliers' },
  { value: '0.05', label: '5% outliers' },
  { value: '0.1', label: '10% outliers' },
]

export default function TemplateGenerator() {
  const navigate = useNavigate()
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const [rowCount, setRowCount] = useState(1000)
  const [quality, setQuality] = useState<DataQualityConfig>({ null_rate: 0, duplicate_rate: 0, outlier_rate: 0 })

  const { data: templates, isLoading: templatesLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: api.getTemplates,
    staleTime: Infinity,
  })

  const previewMutation = usePreview()

  const currentSchema = useMemo<TableSchema | null>(() => {
    if (!selectedTemplate || !templates) return null
    const t = templates.find((t) => t.id === selectedTemplate)
    if (!t) return null
    return {
      name: t.id,
      fields: t.fields,
      row_count: rowCount,
      quality,
    }
  }, [selectedTemplate, templates, rowCount, quality])

  const handlePreview = () => {
    if (!selectedTemplate || !templates) return
    const t = templates.find((tmpl) => tmpl.id === selectedTemplate)
    if (!t) return
    const schema: TableSchema = {
      name: t.id,
      fields: t.fields,
      row_count: rowCount,
      quality,
    }
    previewMutation.mutate(schema)
  }

  const preview = previewMutation.data

  const selectedTemplateData = useMemo(() => {
    return templates?.find((t) => t.id === selectedTemplate)
  }, [templates, selectedTemplate])

  const isRelational = selectedTemplateData?.template_type === 'relational'

  return (
    <div className="flex flex-col gap-6 p-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Template Generator</h1>
        <p className="text-slate-500 mt-1">Choose a pre-built template and generate realistic data instantly.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left: Template selector */}
        <div className="lg:col-span-1 flex flex-col gap-4">
          <Card>
            <CardHeader>
              <h2 className="text-sm font-semibold text-slate-300">Select Template</h2>
            </CardHeader>
            <CardBody className="flex flex-col gap-3">
              {templatesLoading ? (
                <div className="flex justify-center py-8"><Spinner /></div>
              ) : (
                templates?.map((t) => (
                  <TemplateCard
                    key={t.id}
                    template={t}
                    selected={selectedTemplate === t.id}
                    onSelect={setSelectedTemplate}
                  />
                ))
              )}
            </CardBody>
          </Card>
        </div>

        {/* Right: Config + Preview */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          {/* Config */}
          <Card>
            <CardHeader>
              <h2 className="text-sm font-semibold text-slate-300">Generation Config</h2>
            </CardHeader>
            <CardBody className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <Select
                label="Row Count"
                options={ROW_OPTIONS}
                value={String(rowCount)}
                onChange={(e) => setRowCount(Number(e.target.value))}
                id="row-count-select"
              />
              <Select
                label="Null Rate"
                options={NULL_RATE_OPTIONS}
                value={String(quality.null_rate ?? 0)}
                onChange={(e) => setQuality((q) => ({ ...q, null_rate: Number(e.target.value) }))}
                id="null-rate-select"
              />
              <Select
                label="Duplicate Rate"
                options={DUP_RATE_OPTIONS}
                value={String(quality.duplicate_rate ?? 0)}
                onChange={(e) => setQuality((q) => ({ ...q, duplicate_rate: Number(e.target.value) }))}
                id="duplicate-rate-select"
              />
              <Select
                label="Outlier Rate"
                options={OUTLIER_RATE_OPTIONS}
                value={String(quality.outlier_rate ?? 0)}
                onChange={(e) => setQuality((q) => ({ ...q, outlier_rate: Number(e.target.value) }))}
                id="outlier-rate-select"
              />
            </CardBody>
          </Card>

          {isRelational ? (
            <Card className="border-brand-500/30 bg-brand-500/5 mt-0 lg:mt-0">
              <CardBody className="flex flex-col items-center justify-center py-16 text-center">
                <div className="rounded-full bg-brand-500/10 p-4 mb-6">
                  <Database className="h-10 w-10 text-brand-400" />
                </div>
                <h3 className="text-xl font-bold text-slate-100 mb-3">Relational Template Selected</h3>
                <p className="text-slate-400 max-w-md mb-8 leading-relaxed">
                  This template contains <strong className="text-slate-200">{selectedTemplateData?.table_count || selectedTemplateData?.tables?.length || 0} tables</strong> and <strong className="text-slate-200">{selectedTemplateData?.relationship_count || selectedTemplateData?.relationships?.length || 0} foreign key relationships</strong>. 
                  <br className="hidden sm:block" />
                  You can export this dataset directly below, or open it in the Relationship Builder to preview and edit the schema.
                </p>
                
                <div className="w-full max-w-2xl text-left bg-surface-900/80 rounded-xl p-6 border border-white/5 mb-6">
                  <h2 className="text-sm font-semibold text-slate-300 flex items-center gap-2 mb-4 justify-center">
                    <Download className="h-4 w-4 text-brand-400" /> Export Relational Dataset
                  </h2>
                  <ExportPanel template={selectedTemplateData} rowCount={rowCount} quality={quality} />
                </div>

                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => navigate('/relationships', { state: { template: selectedTemplateData } })}
                  icon={<Network className="h-4 w-4" />}
                >
                  Edit in Relationship Builder
                </Button>
              </CardBody>
            </Card>
          ) : (
            <>
              {/* Actions */}
              <div className="flex gap-3">
                <Button
                  onClick={handlePreview}
                  loading={previewMutation.isPending}
                  disabled={!selectedTemplate}
                  icon={<Play className="h-4 w-4" />}
                  id="preview-btn"
                >
                  Preview Data
                </Button>
              </div>

              {/* Metrics */}
              {preview?.metrics && <MetricsBar metrics={preview.metrics} />}

              {/* Preview grid */}
              {preview && (
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <h2 className="text-sm font-semibold text-slate-300">
                        Preview — first {preview.preview_count} rows
                      </h2>
                      <span className="text-xs text-slate-500">{preview.columns.length} columns</span>
                    </div>
                  </CardHeader>
                  <CardBody className="p-0">
                    <DataGrid columns={preview.columns} rows={preview.rows} height={380} />
                  </CardBody>
                </Card>
              )}

              {/* Export */}
              {selectedTemplate && (
                <Card>
                  <CardHeader>
                    <h2 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                      <Download className="h-4 w-4 text-brand-400" /> Export Dataset
                    </h2>
                  </CardHeader>
                  <CardBody>
                    <ExportPanel table={currentSchema} template={selectedTemplateData} rowCount={rowCount} quality={quality} />
                  </CardBody>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
