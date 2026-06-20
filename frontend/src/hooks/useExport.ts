import { useState, useCallback } from 'react'
import toast from 'react-hot-toast'
import { exportApi } from '@/services/api'
import type { AnalyticsRequest, ExportFormat, SQLDialect, TableSchema, TemplateInfo, DataQualityConfig } from '@/types'

interface UseExportState {
  isExporting: boolean
  format: ExportFormat | null
}

export function useExport() {
  const [state, setState] = useState<UseExportState>({ isExporting: false, format: null })

  const exportTable = useCallback(
    async (table: TableSchema, format: ExportFormat, dialect?: SQLDialect) => {
      setState({ isExporting: true, format })
      const toastId = toast.loading(`Preparing ${format.toUpperCase()} export…`)
      try {
        switch (format) {
          case 'csv':
            await exportApi.csv(table)
            break
          case 'json':
            await exportApi.json(table)
            break
          case 'sql':
            await exportApi.sql(table, dialect ?? 'postgresql')
            break
          case 'excel':
            await exportApi.excel(table)
            break
        }
        toast.success(`${table.name}.${format} downloaded successfully!`, { id: toastId })
      } catch (err: any) {
        if (err.name === 'AbortError') {
          toast.dismiss(toastId)
          setState({ isExporting: false, format: null })
          return
        }
        const message = err instanceof Error ? err.message : 'Export failed'
        toast.error(message, { id: toastId })
      } finally {
        setState({ isExporting: false, format: null })
      }
    },
    []
  )

  const exportAnalytics = useCallback(
    async (request: AnalyticsRequest, format: 'csv' | 'json') => {
      setState({ isExporting: true, format })
      const toastId = toast.loading(`Preparing ${format.toUpperCase()} export…`)
      try {
        if (format === 'csv') await exportApi.analyticsCSV(request)
        else await exportApi.analyticsJSON(request)
        toast.success('Analytics dataset downloaded!', { id: toastId })
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Export failed'
        toast.error(message, { id: toastId })
      } finally {
        setState({ isExporting: false, format: null })
      }
    },
    []
  )

  const exportRelationalTemplate = useCallback(
    async (template: TemplateInfo, format: ExportFormat, rowCount: number, quality: DataQualityConfig, dialect?: SQLDialect) => {
      setState({ isExporting: true, format })
      const toastId = toast.loading(`Preparing ${format.toUpperCase()} export for ${template.name}…`)
      try {
        if (!template.tables) throw new Error("Template has no tables")
        
        const baseRowCount = template.tables[0]?.row_count || 100
        const scale = rowCount / baseRowCount

        const request = {
          tables: template.tables.map(t => ({
            ...t,
            fields: t.fields || [],
            row_count: Math.max(1, Math.floor((t.row_count || 100) * scale)),
            quality
          })),
          relationships: template.relationships || []
        }
        
        switch(format) {
          case 'csv': await exportApi.relationalCSV(request, `${template.id}_csv.zip`); break;
          case 'json': await exportApi.relationalJSON(request, `${template.id}_json.zip`); break;
          case 'excel': await exportApi.relationalExcel(request, `${template.id}.xlsx`); break;
          case 'sql': await exportApi.relationalSQL(request, dialect ?? 'postgresql', `${template.id}.sql`); break;
        }
        
        toast.success(`${template.name} exported successfully!`, { id: toastId })
      } catch (err: any) {
        if (err.name === 'AbortError') {
          toast.dismiss(toastId)
          setState({ isExporting: false, format: null })
          return
        }
        const message = err instanceof Error ? err.message : 'Export failed'
        toast.error(message, { id: toastId })
      } finally {
        setState({ isExporting: false, format: null })
      }
    },
    []
  )

  return { ...state, exportTable, exportAnalytics, exportRelationalTemplate }
}
