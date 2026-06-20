import { memo, useState, useCallback } from 'react'
import { Copy, Check, Code2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import toast from 'react-hot-toast'

interface SQLViewerProps {
  sql: string
  title?: string
  maxHeight?: number | string
}

function highlightSQL(sql: string): string {
  const keywords = [
    'CREATE', 'TABLE', 'ALTER', 'ADD', 'CONSTRAINT', 'FOREIGN', 'KEY', 'REFERENCES',
    'INDEX', 'ON', 'INSERT', 'INTO', 'VALUES', 'NOT', 'NULL', 'DEFAULT', 'UNIQUE',
    'PRIMARY', 'INT', 'INTEGER', 'VARCHAR', 'TEXT', 'BOOLEAN', 'DATE', 'TIMESTAMP',
    'DATETIME', 'NUMERIC', 'DECIMAL', 'DOUBLE', 'FLOAT', 'REAL', 'CHAR', 'BIGINT',
    'SMALLINT', 'JSONB', 'JSON', 'UUID', 'INET', 'MACADDR', 'PRECISION', 'BIT',
    'UNIQUEIDENTIFIER', 'NVARCHAR', 'DATETIME2', 'TINYINT',
  ]

  return sql
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/'[^']*'/g, (m) => `<span class="sql-string">${m}</span>`)
    .replace(/--[^\n]*/g, (m) => `<span class="sql-comment">${m}</span>`)
    .replace(
      new RegExp(`\\b(${keywords.join('|')})\\b`, 'g'),
      (m) => `<span class="sql-keyword">${m}</span>`
    )
    .replace(/\b(\d+\.?\d*)\b/g, (m) => `<span class="sql-number">${m}</span>`)
}

export const SQLViewer = memo(function SQLViewer({ sql, title, maxHeight = 400 }: SQLViewerProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(sql)
      setCopied(true)
      toast.success('SQL copied to clipboard!')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      toast.error('Failed to copy')
    }
  }, [sql])

  const highlighted = highlightSQL(sql)

  return (
    <div className="flex flex-col rounded-xl border border-white/5 bg-surface-900 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/5 px-4 py-3">
        <div className="flex items-center gap-2">
          <Code2 className="h-4 w-4 text-brand-400" />
          <span className="text-sm font-medium text-slate-300">{title ?? 'SQL'}</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleCopy}
          icon={copied ? <Check className="h-4 w-4 text-green-400" /> : <Copy className="h-4 w-4" />}
          id="copy-sql-btn"
        >
          {copied ? 'Copied!' : 'Copy'}
        </Button>
      </div>

      {/* Code */}
      <pre
        className="overflow-auto p-4 text-sm leading-relaxed sql-code"
        style={{ maxHeight }}
        dangerouslySetInnerHTML={{ __html: highlighted }}
      />
    </div>
  )
})
