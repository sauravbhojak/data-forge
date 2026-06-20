import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Table2, Wand2, GitBranch, BarChart3,
  ArrowRight, Sparkles, Database, Zap,
} from 'lucide-react'
import { Card, CardBody } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { api } from '@/services/api'
import { formatNumber } from '@/utils/formatters'

const STATS = [
  { label: 'Field Types', value: '40+', icon: <Wand2 className="h-5 w-5 text-brand-400" />, color: 'text-brand-300' },
  { label: 'Export Formats', value: '4', icon: <Table2 className="h-5 w-5 text-violet-400" />, color: 'text-violet-300' },
  { label: 'Max Rows', value: '1M', icon: <Database className="h-5 w-5 text-green-400" />, color: 'text-green-300' },
  { label: 'Templates', value: '6', icon: <Sparkles className="h-5 w-5 text-amber-400" />, color: 'text-amber-300' },
]

const QUICK_START = [
  {
    title: 'Template Generator',
    description: 'Generate data from pre-built templates like Employee, Sales, Hospital, and more.',
    path: '/templates',
    icon: <Table2 className="h-7 w-7" />,
    color: 'from-brand-500 to-violet-600',
    badge: 'Quick Start',
  },
  {
    title: 'Custom Schema Builder',
    description: 'Define your own table schema with 40+ field types, constraints, and distributions.',
    path: '/schema',
    icon: <Wand2 className="h-7 w-7" />,
    color: 'from-violet-500 to-fuchsia-600',
    badge: 'Flexible',
  },
  {
    title: 'Relationship Builder',
    description: 'Generate multi-table datasets with FK relationships and referential integrity.',
    path: '/relationships',
    icon: <GitBranch className="h-7 w-7" />,
    color: 'from-sky-500 to-cyan-600',
    badge: 'Advanced',
  },
  {
    title: 'Analytics Datasets',
    description: 'Generate correlated time-series data for Revenue, Website, IoT, and VPN analytics.',
    path: '/analytics',
    icon: <BarChart3 className="h-7 w-7" />,
    color: 'from-emerald-500 to-teal-600',
    badge: 'Time-Series',
  },
]

export default function Dashboard() {
  const navigate = useNavigate()

  const { data: templates, isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: api.getTemplates,
    staleTime: Infinity,
  })

  return (
    <div className="flex flex-col gap-8 p-6 max-w-7xl mx-auto">
      {/* Hero */}
      <div className="relative overflow-hidden rounded-2xl border border-white/5 bg-gradient-to-br from-brand-950/80 via-surface-900 to-violet-950/50 p-8">
        {/* Glow blobs */}
        <div className="pointer-events-none absolute -top-20 -left-20 h-64 w-64 rounded-full bg-brand-600/20 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-10 -right-10 h-48 w-48 rounded-full bg-violet-600/20 blur-3xl" />

        <div className="relative">
          <div className="mb-4 flex items-center gap-2">
            <Badge variant="brand">
              <Zap className="h-3 w-3" /> v1.0.0
            </Badge>
            <Badge variant="success">Production Ready</Badge>
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight">
            <span className="gradient-text">Smart Test Data</span>
            <br />
            <span className="text-slate-100">Generation Platform</span>
          </h1>
          <p className="mt-4 max-w-2xl text-slate-400 leading-relaxed">
            Generate realistic datasets for testing, development, SQL practice, dashboard creation,
            ETL validation, analytics, demo environments, and performance testing. Up to{' '}
            <span className="text-brand-300 font-semibold">1,000,000 rows</span> with streaming exports.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Button
              onClick={() => navigate('/templates')}
              icon={<Sparkles className="h-4 w-4" />}
              iconRight={<ArrowRight className="h-4 w-4" />}
              id="get-started-btn"
            >
              Get Started
            </Button>
            <Button variant="ghost" onClick={() => navigate('/schema')} id="build-schema-btn">
              Build Custom Schema
            </Button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {STATS.map((stat) => (
          <Card key={stat.label} className="p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-white/5 p-2.5">{stat.icon}</div>
              <div>
                <p className={`text-2xl font-bold font-mono ${stat.color}`}>{stat.value}</p>
                <p className="text-xs text-slate-500">{stat.label}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Quick Start Cards */}
      <div>
        <h2 className="section-header mb-4">Quick Start</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {QUICK_START.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              id={`quickstart-${item.path.slice(1)}`}
              className="group relative flex flex-col gap-4 overflow-hidden rounded-xl border border-white/5 bg-surface-800/40 p-5 text-left transition-all duration-200 hover:border-white/15 hover:bg-surface-800/60"
            >
              <div className={`inline-flex rounded-xl bg-gradient-to-br ${item.color} p-2.5 shadow-md`}>
                <span className="text-white">{item.icon}</span>
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-sm font-semibold text-slate-100">{item.title}</h3>
                  <Badge variant="default">{item.badge}</Badge>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">{item.description}</p>
              </div>
              <ArrowRight className="h-4 w-4 text-slate-600 transition-transform group-hover:translate-x-1 group-hover:text-brand-400" />
            </button>
          ))}
        </div>
      </div>

      {/* Templates overview */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="section-header">Pre-built Templates</h2>
          <Button variant="ghost" size="sm" onClick={() => navigate('/templates')} id="view-templates-btn">
            View all
          </Button>
        </div>
        {isLoading ? (
          <div className="flex justify-center p-8"><Spinner /></div>
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {templates?.map((t) => (
              <button
                key={t.id}
                onClick={() => navigate('/templates')}
                id={`dashboard-template-${t.id}`}
                className="glass-card p-4 text-left transition-all hover:border-brand-500/30 hover:shadow-brand-sm"
              >
                <p className="text-sm font-semibold text-slate-200">{t.name}</p>
                <p className="text-xs text-slate-500 mt-1">{t.field_count} fields</p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {t.tags.slice(0, 2).map((tag) => (
                    <Badge key={tag}>{tag}</Badge>
                  ))}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
