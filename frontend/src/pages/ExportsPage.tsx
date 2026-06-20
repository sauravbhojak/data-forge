import { Download, FileText, Braces, Database, Table2, Info } from 'lucide-react'
import { Card, CardBody, CardHeader } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

const FORMATS = [
  {
    id: 'csv',
    name: 'CSV',
    icon: <Table2 className="h-8 w-8" />,
    color: 'from-emerald-500 to-teal-600',
    description: 'Comma-separated values. Compatible with Excel, pandas, R, Tableau, Power BI, and all major tools.',
    recommended: true,
    maxRows: '1,000,000',
    useCase: ['Excel / Google Sheets', 'Pandas DataFrame', 'Tableau / Power BI', 'ETL pipelines'],
  },
  {
    id: 'json',
    name: 'JSON',
    icon: <Braces className="h-8 w-8" />,
    color: 'from-sky-500 to-blue-600',
    description: 'JavaScript Object Notation. Perfect for APIs, NoSQL seeding, and JavaScript/TypeScript projects.',
    recommended: false,
    maxRows: '1,000,000',
    useCase: ['REST API mocking', 'MongoDB seeding', 'JavaScript apps', 'Postman tests'],
  },
  {
    id: 'sql',
    name: 'SQL',
    icon: <Database className="h-8 w-8" />,
    color: 'from-violet-500 to-purple-600',
    description: 'SQL INSERT INTO statements. Supports PostgreSQL, MySQL, SQLite, and SQL Server dialects.',
    recommended: false,
    maxRows: '500,000',
    useCase: ['Database seeding', 'SQL practice', 'Migration testing', 'CI/CD test data'],
  },
  {
    id: 'excel',
    name: 'Excel',
    icon: <FileText className="h-8 w-8" />,
    color: 'from-orange-500 to-amber-600',
    description: 'Native .xlsx spreadsheet. Styled headers, automatic column sizing, compatible with Microsoft Excel.',
    recommended: false,
    maxRows: '100,000',
    useCase: ['Business reports', 'HR data', 'Manual review', 'Non-technical users'],
  },
]

export default function ExportsPage() {
  return (
    <div className="flex flex-col gap-8 p-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Export Center</h1>
        <p className="text-slate-500 mt-1">All export formats and their capabilities. Generate data from Templates or Schema Builder, then export here.</p>
      </div>

      {/* Format cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {FORMATS.map((fmt) => (
          <Card key={fmt.id} className="flex flex-col gap-0 overflow-hidden">
            <div className={`bg-gradient-to-br ${fmt.color} p-6 flex items-center gap-3`}>
              <span className="text-white">{fmt.icon}</span>
              <div>
                <p className="text-xl font-bold text-white">{fmt.name}</p>
                {fmt.recommended && <Badge variant="success" className="mt-1">Recommended</Badge>}
              </div>
            </div>
            <CardBody className="flex flex-col gap-4">
              <p className="text-sm text-slate-400 leading-relaxed">{fmt.description}</p>
              <div>
                <p className="form-label">Max Rows</p>
                <p className="text-lg font-bold font-mono text-slate-200">{fmt.maxRows}</p>
              </div>
              <div>
                <p className="form-label mb-2">Best For</p>
                <ul className="flex flex-col gap-1">
                  {fmt.useCase.map((u) => (
                    <li key={u} className="flex items-center gap-2 text-xs text-slate-400">
                      <span className="h-1.5 w-1.5 rounded-full bg-brand-500 shrink-0" />
                      {u}
                    </li>
                  ))}
                </ul>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      {/* Info */}
      <Card>
        <CardBody className="flex gap-4">
          <Info className="h-5 w-5 text-brand-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-slate-300">How to Export</p>
            <p className="text-sm text-slate-500 mt-1 leading-relaxed">
              Navigate to <strong className="text-slate-300">Templates</strong> or{' '}
              <strong className="text-slate-300">Schema Builder</strong>, configure your dataset,
              preview the data, and then click the export button for your desired format.
              CSV, JSON, and SQL exports stream directly from the server — even 1M rows won't freeze your browser.
              Excel exports are limited to 100K rows due to browser memory constraints.
            </p>
          </div>
        </CardBody>
      </Card>

      {/* Streaming info */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[
          { label: 'Streaming Exports', value: 'CSV · JSON · SQL', desc: 'Zero memory loading — server streams directly to your browser' },
          { label: 'Max Export Size', value: '1M rows', desc: 'Tested up to 1 million rows without server-side memory issues' },
          { label: 'Formats', value: '4', desc: 'CSV, JSON, SQL (4 dialects), and Excel' },
        ].map((item) => (
          <div key={item.label} className="glass-card p-5">
            <p className="text-xs text-slate-500 uppercase tracking-wide">{item.label}</p>
            <p className="mt-1 text-2xl font-bold font-mono gradient-text">{item.value}</p>
            <p className="mt-1 text-xs text-slate-500">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
