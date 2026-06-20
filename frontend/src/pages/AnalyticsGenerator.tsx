import { useState } from 'react'
import { BarChart3, Play, Download } from 'lucide-react'
import { Card, CardBody, CardHeader } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { DataGrid } from '@/components/DataGrid'
import { useExport } from '@/hooks/useExport'
import { useAnalyticsPreview } from '@/hooks/useGeneration'
import type { AnalyticsDatasetType, AnalyticsRequest } from '@/types'
import { ROW_COUNT_OPTIONS, formatRowCount } from '@/types'

const ROW_OPTIONS = ROW_COUNT_OPTIONS.map((n) => ({ value: String(n), label: `${formatRowCount(n)} rows` }))

const DATASET_TYPES: {
  id: AnalyticsDatasetType
  name: string
  description: string
  fields: string[]
  color: string
}[] = [
  {
    id: 'revenue',
    name: 'Revenue Dataset',
    description: 'Correlated revenue, profit, expenses, and customer count time-series.',
    fields: ['date', 'revenue', 'profit', 'expenses', 'customer_count'],
    color: 'from-emerald-500 to-teal-600',
  },
  {
    id: 'website',
    name: 'Website Analytics',
    description: 'Users, sessions, bounce rate, conversion rate, and revenue.',
    fields: ['date', 'users', 'sessions', 'bounce_rate', 'conversion_rate', 'revenue'],
    color: 'from-sky-500 to-cyan-600',
  },
  {
    id: 'iot',
    name: 'IoT Sensor Data',
    description: 'Temperature, humidity, pressure time-series with device IDs.',
    fields: ['timestamp', 'device_id', 'temperature', 'humidity', 'pressure'],
    color: 'from-violet-500 to-fuchsia-600',
  },
  {
    id: 'vpn',
    name: 'VPN Analytics',
    description: 'Active users, bandwidth, latency, and packet loss by country.',
    fields: ['date', 'country', 'active_users', 'bandwidth_usage_gb', 'latency_ms', 'packet_loss_pct'],
    color: 'from-orange-500 to-red-600',
  },
]

export default function AnalyticsGenerator() {
  const [selected, setSelected] = useState<AnalyticsDatasetType>('revenue')
  const [rowCount, setRowCount] = useState(365)
  const [trendStrength, setTrendStrength] = useState(1.0)
  const [noiseLevel, setNoiseLevel] = useState(0.1)

  const previewMutation = useAnalyticsPreview()
  const { isExporting, exportAnalytics } = useExport()

  const request: AnalyticsRequest = { dataset_type: selected, row_count: rowCount, trend_strength: trendStrength, noise_level: noiseLevel }

  const preview = previewMutation.data

  return (
    <div className="flex flex-col gap-6 p-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Analytics Dataset Generator</h1>
        <p className="text-slate-500 mt-1">Generate correlated, realistic time-series analytics datasets with configurable trends.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        {/* Dataset type selector */}
        <div className="lg:col-span-1 flex flex-col gap-3">
          <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wide">Dataset Type</h2>
          {DATASET_TYPES.map((dt) => (
            <button
              key={dt.id}
              onClick={() => setSelected(dt.id)}
              id={`analytics-${dt.id}`}
              className={`group flex flex-col gap-2 rounded-xl border p-4 text-left transition-all ${
                selected === dt.id
                  ? 'border-brand-500/60 bg-brand-500/10'
                  : 'border-white/5 bg-surface-800/30 hover:border-white/15'
              }`}
            >
              <div className={`inline-flex rounded-lg bg-gradient-to-br ${dt.color} px-2 py-1`}>
                <span className="text-xs font-bold text-white uppercase tracking-wide">{dt.id}</span>
              </div>
              <p className="text-sm font-semibold text-slate-200">{dt.name}</p>
              <p className="text-xs text-slate-500">{dt.description}</p>
              <div className="flex flex-wrap gap-1">
                {dt.fields.map((f) => (
                  <span key={f} className="rounded bg-white/5 px-1.5 py-0.5 text-xs font-mono text-slate-500">{f}</span>
                ))}
              </div>
            </button>
          ))}
        </div>

        {/* Config + preview */}
        <div className="lg:col-span-3 flex flex-col gap-4">
          {/* Config */}
          <Card>
            <CardHeader><h2 className="text-sm font-semibold text-slate-300">Generation Parameters</h2></CardHeader>
            <CardBody className="grid grid-cols-3 gap-4">
              <Select
                label="Row Count"
                options={ROW_OPTIONS}
                value={String(rowCount)}
                onChange={(e) => setRowCount(Number(e.target.value))}
                id="analytics-row-count"
              />
              <div>
                <label className="form-label">Trend Strength ({trendStrength.toFixed(1)})</label>
                <input
                  type="range"
                  min="0"
                  max="5"
                  step="0.1"
                  value={trendStrength}
                  className="w-full accent-brand-500"
                  onChange={(e) => setTrendStrength(Number(e.target.value))}
                  aria-label="Trend strength"
                />
                <div className="flex justify-between text-xs text-slate-600 mt-1"><span>Flat</span><span>Strong</span></div>
              </div>
              <div>
                <label className="form-label">Noise Level ({noiseLevel.toFixed(2)})</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={noiseLevel}
                  className="w-full accent-brand-500"
                  onChange={(e) => setNoiseLevel(Number(e.target.value))}
                  aria-label="Noise level"
                />
                <div className="flex justify-between text-xs text-slate-600 mt-1"><span>Smooth</span><span>Noisy</span></div>
              </div>
            </CardBody>
          </Card>

          {/* Actions */}
          <div className="flex gap-3">
            <Button
              onClick={() => previewMutation.mutate(request)}
              loading={previewMutation.isPending}
              icon={<Play className="h-4 w-4" />}
              id="analytics-preview-btn"
            >
              Preview Data
            </Button>
            <Button
              variant="ghost"
              loading={isExporting}
              disabled={isExporting}
              icon={<Download className="h-4 w-4" />}
              onClick={() => exportAnalytics(request, 'csv')}
              id="analytics-export-csv-btn"
            >
              Export CSV
            </Button>
            <Button
              variant="ghost"
              loading={isExporting}
              disabled={isExporting}
              icon={<Download className="h-4 w-4" />}
              onClick={() => exportAnalytics(request, 'json')}
              id="analytics-export-json-btn"
            >
              Export JSON
            </Button>
          </div>

          {/* Preview grid */}
          {preview ? (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-slate-300">Preview ({preview.preview_count} rows)</h2>
                  <Badge variant="brand">{selected}</Badge>
                </div>
              </CardHeader>
              <CardBody className="p-0">
                <DataGrid columns={preview.columns} rows={preview.rows} height={400} />
              </CardBody>
            </Card>
          ) : (
            <div className="flex h-60 items-center justify-center rounded-xl border border-dashed border-white/10 bg-surface-900/30">
              <div className="text-center">
                <BarChart3 className="mx-auto mb-3 h-10 w-10 text-slate-700" />
                <p className="text-slate-500">Click "Preview Data" to see sample rows</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
