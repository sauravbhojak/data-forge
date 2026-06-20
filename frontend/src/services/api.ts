import axios from 'axios'
import type {
  AnalyticsRequest,
  ERDRequest,
  ERDResponse,
  GenerationResponse,
  PreviewResponse,
  RelationalSchemaRequest,
  SQLDialect,
  SQLResponse,
  SQLSchemaRequest,
  TableSchema,
  TemplateInfo,
} from '@/types'

// ── Axios instance ────────────────────────────────────────────────────────────

const BASE_URL = import.meta.env.VITE_API_URL ?? '/api'

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120_000, // 2 min for large generations
})

// ── Response / error interceptors ─────────────────────────────────────────────

apiClient.interceptors.response.use(
  (res) => res,
  (error) => {
    const message =
      error?.response?.data?.error?.message ??
      error?.response?.data?.detail ??
      error.message ??
      'An unexpected error occurred'
    return Promise.reject(new Error(message))
  }
)

// ── API functions ─────────────────────────────────────────────────────────────

export const api = {
  // Health
  health: () => apiClient.get<{ status: string }>('/health').then((r) => r.data),

  // Templates
  getTemplates: () => apiClient.get<TemplateInfo[]>('/templates').then((r) => r.data),

  // Preview
  preview: (table: TableSchema) =>
    apiClient
      .post<PreviewResponse>('/preview', { table })
      .then((r) => r.data),

  // Generate (metadata only)
  generate: (table: TableSchema) =>
    apiClient
      .post<GenerationResponse>('/generate', { table })
      .then((r) => r.data),

  // Analytics preview
  analyticsPreview: (request: AnalyticsRequest) =>
    apiClient
      .post<{ dataset_type: string; columns: string[]; rows: Record<string, unknown>[]; preview_count: number }>(
        '/analytics/preview',
        request
      )
      .then((r) => r.data),

  // SQL Schema
  generateSchema: (request: SQLSchemaRequest) =>
    apiClient.post<SQLResponse>('/generate-schema', request).then((r) => r.data),

  // ERD
  generateERD: (request: ERDRequest) =>
    apiClient.post<ERDResponse>('/generate-erd', request).then((r) => r.data),

  // Relational preview
  generateRelations: (request: RelationalSchemaRequest) =>
    apiClient
      .post<{ tables: string[]; preview: Record<string, Record<string, unknown>[]>; row_counts: Record<string, number> }>(
        '/generate-relations',
        request
      )
      .then((r) => r.data),
}

// ── Download helpers ──────────────────────────────────────────────────────────

export async function downloadFile(
  endpoint: string,
  body: unknown,
  filename: string,
  mimeType: string
): Promise<void> {
  // Request notification permission if not already granted/denied
  if ('Notification' in window && Notification.permission === 'default') {
    await Notification.requestPermission()
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const errorText = await response.text()
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Export Failed', { body: `Failed to export ${filename}` })
    }
    throw new Error(`Export failed: ${errorText}`)
  }

  // 1. Try File System Access API (Streams directly to disk, Zero RAM bloat)
  if ('showSaveFilePicker' in window && response.body) {
    try {
      // @ts-ignore - TS might not have types for this by default
      const handle = await window.showSaveFilePicker({
        suggestedName: filename,
        types: [
          {
            description: 'Exported File',
            accept: { [mimeType]: [`.${filename.split('.').pop()}`] },
          },
        ],
      })
      const writable = await handle.createWritable()
      await response.body.pipeTo(writable)
      
      // Notify the user that it finished successfully
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Export Complete', { body: `${filename} has been successfully saved.` })
      }
      return
    } catch (err: any) {
      if (err.name === 'AbortError') throw err // User clicked cancel
      console.warn('File System Access API failed, falling back to blob buffering', err)
    }
  }

  // 2. Fallback for older browsers (Buffers entirely in RAM)
  const blob = await response.blob()
  const url = URL.createObjectURL(new Blob([blob], { type: mimeType }))
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  // Notify the user that it finished successfully
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification('Export Complete', { body: `${filename} is ready for download.` })
  }
}

export const exportApi = {
  csv: (table: TableSchema) =>
    downloadFile('/export/csv', { table }, `${table.name}.csv`, 'text/csv'),

  json: (table: TableSchema) =>
    downloadFile('/export/json', { table }, `${table.name}.json`, 'application/json'),

  sql: (table: TableSchema, dialect: SQLDialect = 'postgresql') =>
    downloadFile(
      `/export/sql?dialect=${dialect}`,
      { table },
      `${table.name}.sql`,
      'application/sql'
    ),

  excel: (table: TableSchema) =>
    downloadFile(
      '/export/excel',
      { table },
      `${table.name}.xlsx`,
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ),

  analyticsCSV: (request: AnalyticsRequest) =>
    downloadFile(
      '/export/analytics/csv',
      request,
      `${request.dataset_type}_analytics.csv`,
      'text/csv'
    ),

  analyticsJSON: (request: AnalyticsRequest) =>
    downloadFile(
      '/export/analytics/json',
      request,
      `${request.dataset_type}_analytics.json`,
      'application/json'
    ),

  relationalCSV: (request: RelationalSchemaRequest, filename: string) =>
    downloadFile('/export/relational/csv', request, filename, 'application/zip'),

  relationalJSON: (request: RelationalSchemaRequest, filename: string) =>
    downloadFile('/export/relational/json', request, filename, 'application/zip'),

  relationalExcel: (request: RelationalSchemaRequest, filename: string) =>
    downloadFile(
      '/export/relational/excel',
      request,
      filename,
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ),

  relationalSQL: (request: RelationalSchemaRequest, dialect: SQLDialect, filename: string) =>
    downloadFile(
      `/export/relational/sql?dialect=${dialect}`,
      request,
      filename,
      'application/sql'
    ),
}
