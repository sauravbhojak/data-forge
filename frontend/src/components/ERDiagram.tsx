import { useEffect, useRef, useState, memo } from 'react'
import { ZoomIn, ZoomOut, RotateCcw, Download } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'

interface ERDiagramProps {
  mermaidText: string
  height?: number | string
}

export const ERDiagram = memo(function ERDiagram({ mermaidText, height = 500 }: ERDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [zoom, setZoom] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!mermaidText || !containerRef.current) return

    let cancelled = false
    setLoading(true)
    setError(null)

    import('mermaid').then(({ default: mermaid }) => {
      mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        darkMode: true,
        themeVariables: {
          primaryColor: '#4338ca',
          primaryTextColor: '#e2e8f0',
          primaryBorderColor: '#6366f1',
          lineColor: '#6366f1',
          secondaryColor: '#1e293b',
          tertiaryColor: '#0f172a',
          background: '#0f172a',
          mainBkg: '#1e293b',
          nodeBorder: '#6366f1',
          clusterBkg: '#1e293b',
          titleColor: '#e2e8f0',
          edgeLabelBackground: '#1e293b',
        },
        er: { diagramPadding: 20, layoutDirection: 'TB', minEntityWidth: 100 },
      })

      const id = `erd-${Date.now()}`
      mermaid
        .render(id, mermaidText)
        .then(({ svg }) => {
          if (!cancelled && containerRef.current) {
            containerRef.current.innerHTML = svg
            setLoading(false)
          }
        })
        .catch((err: Error) => {
          if (!cancelled) {
            setError(err.message ?? 'Failed to render diagram')
            setLoading(false)
          }
        })
    })

    return () => { cancelled = true }
  }, [mermaidText])

  const downloadSVG = () => {
    if (!containerRef.current) return
    const svgEl = containerRef.current.querySelector('svg')
    if (!svgEl) return
    const blob = new Blob([svgEl.outerHTML], { type: 'image/svg+xml' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'er-diagram.svg'
    a.click()
  }

  return (
    <div className="flex flex-col gap-3">
      {/* Toolbar */}
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" onClick={() => setZoom((z) => Math.min(z + 0.1, 3))} icon={<ZoomIn className="h-4 w-4" />}>
          Zoom In
        </Button>
        <Button variant="ghost" size="sm" onClick={() => setZoom((z) => Math.max(z - 0.1, 0.3))} icon={<ZoomOut className="h-4 w-4" />}>
          Zoom Out
        </Button>
        <Button variant="ghost" size="sm" onClick={() => setZoom(1)} icon={<RotateCcw className="h-4 w-4" />}>
          Reset
        </Button>
        <span className="text-xs text-slate-500">{Math.round(zoom * 100)}%</span>
        <div className="flex-1" />
        <Button variant="ghost" size="sm" onClick={downloadSVG} icon={<Download className="h-4 w-4" />}>
          Save SVG
        </Button>
      </div>

      {/* Diagram canvas */}
      <div
        className="overflow-auto rounded-xl border border-white/5 bg-surface-900"
        style={{ height }}
      >
        {loading && (
          <div className="flex h-full items-center justify-center">
            <Spinner size="lg" />
          </div>
        )}
        {error && (
          <div className="flex h-full items-center justify-center p-8 text-center">
            <div>
              <p className="text-sm text-red-400 font-medium">Failed to render diagram</p>
              <p className="mt-1 text-xs text-slate-500">{error}</p>
            </div>
          </div>
        )}
        <div
          ref={containerRef}
          className="mermaid-container p-6 transition-transform origin-top-left"
          style={{ transform: `scale(${zoom})` }}
        />
      </div>
    </div>
  )
})
