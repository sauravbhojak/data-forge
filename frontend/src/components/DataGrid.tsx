import { useMemo, memo } from 'react'
import { AgGridReact } from 'ag-grid-react'
import type { ColDef, GridOptions } from 'ag-grid-community'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'

interface DataGridProps {
  columns: string[]
  rows: Record<string, unknown>[]
  height?: number | string
  loading?: boolean
}

export const DataGrid = memo(function DataGrid({
  columns,
  rows,
  height = 500,
  loading = false,
}: DataGridProps) {
  const colDefs = useMemo<ColDef[]>(
    () =>
      columns.map((col) => ({
        field: col,
        headerName: col,
        sortable: true,
        filter: true,
        resizable: true,
        minWidth: 100,
        flex: 1,
        valueFormatter: (params) => {
          if (params.value === null || params.value === undefined) return 'NULL'
          if (typeof params.value === 'boolean') return params.value ? 'true' : 'false'
          if (typeof params.value === 'object') return JSON.stringify(params.value)
          return String(params.value)
        },
        cellStyle: (params) => {
          if (params.value === null || params.value === undefined) {
            return { color: '#475569', fontStyle: 'italic' }
          }
          if (typeof params.value === 'boolean') {
            return { color: params.value ? '#86efac' : '#fca5a5' }
          }
          if (typeof params.value === 'number') {
            return { color: '#fb923c', fontFamily: 'JetBrains Mono, monospace' }
          }
          return null
        },
      })),
    [columns]
  )

  const gridOptions: GridOptions = useMemo(
    () => ({
      animateRows: true,
      suppressMovableColumns: false,
      defaultColDef: {
        sortable: true,
        filter: true,
        resizable: true,
      },
      pagination: rows.length > 100,
      paginationPageSize: 100,
      rowBuffer: 20,
      suppressFieldDotNotation: true,
    }),
    [rows.length]
  )

  if (loading) {
    return (
      <div
        className="flex items-center justify-center rounded-xl border border-white/5 bg-surface-900"
        style={{ height }}
      >
        <div className="text-center">
          <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
          <p className="text-sm text-slate-500">Generating preview…</p>
        </div>
      </div>
    )
  }

  if (rows.length === 0) {
    return (
      <div
        className="flex items-center justify-center rounded-xl border border-dashed border-white/10 bg-surface-900"
        style={{ height }}
      >
        <p className="text-sm text-slate-500">No data to display</p>
      </div>
    )
  }

  return (
    <div
      className="ag-theme-alpine-dark w-full rounded-xl overflow-hidden border border-white/5"
      style={{ height }}
    >
      <AgGridReact
        rowData={rows}
        columnDefs={colDefs}
        gridOptions={gridOptions}
        suppressRowHoverHighlight={false}
      />
    </div>
  )
})
