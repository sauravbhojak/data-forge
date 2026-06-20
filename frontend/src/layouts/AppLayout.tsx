import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Table2,
  Wand2,
  GitBranch,
  Network,
  BarChart3,
  Download,
  Settings,
  ChevronLeft,
  ChevronRight,
  Database,
  Menu,
} from 'lucide-react'
import clsx from 'clsx'

interface NavItem {
  path: string
  label: string
  icon: React.ReactNode
  description: string
}

const NAV_ITEMS: NavItem[] = [
  { path: '/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="h-5 w-5" />, description: 'Overview & quick start' },
  { path: '/templates', label: 'Templates', icon: <Table2 className="h-5 w-5" />, description: 'Pre-built datasets' },
  { path: '/schema', label: 'Schema Builder', icon: <Wand2 className="h-5 w-5" />, description: 'Custom table schemas' },
  { path: '/relationships', label: 'Relationships', icon: <GitBranch className="h-5 w-5" />, description: 'Multi-table FK data' },
  { path: '/erd', label: 'ER Diagram', icon: <Network className="h-5 w-5" />, description: 'Entity-relationship diagrams' },
  { path: '/analytics', label: 'Analytics Data', icon: <BarChart3 className="h-5 w-5" />, description: 'Time-series datasets' },
  { path: '/exports', label: 'Exports', icon: <Download className="h-5 w-5" />, description: 'Download center' },
  { path: '/settings', label: 'Settings', icon: <Settings className="h-5 w-5" />, description: 'Configuration' },
]

interface AppLayoutProps {
  children: React.ReactNode
}

export default function AppLayout({ children }: AppLayoutProps) {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  const currentPage = NAV_ITEMS.find((n) => location.pathname.startsWith(n.path))

  return (
    <div className="flex h-screen overflow-hidden bg-surface-900">
      {/* ── Mobile overlay ──────────────────────────────────────────────── */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* ── Sidebar ─────────────────────────────────────────────────────── */}
      <aside
        className={clsx(
          'fixed inset-y-0 left-0 z-50 flex flex-col border-r border-white/5 bg-surface-950 transition-all duration-300',
          collapsed ? 'w-16' : 'w-64',
          mobileOpen ? 'translate-x-0' : '-translate-x-full',
          'lg:relative lg:translate-x-0'
        )}
      >
        {/* Logo */}
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-white/5 px-4">
          {!collapsed && (
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-violet-600 shadow-brand-md">
                <Database className="h-4 w-4 text-white" />
              </div>
              <div>
                <span className="text-sm font-bold tracking-tight text-slate-100">DataForge</span>
                <p className="text-xs text-slate-500">Data Generator</p>
              </div>
            </div>
          )}
          {collapsed && (
            <div className="mx-auto flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-violet-600">
              <Database className="h-4 w-4 text-white" />
            </div>
          )}
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-4 px-2">
          <ul className="flex flex-col gap-1">
            {NAV_ITEMS.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) =>
                    clsx(
                      'group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-all duration-150',
                      isActive
                        ? 'bg-brand-500/15 text-brand-300 border border-brand-500/20'
                        : 'text-slate-400 hover:bg-white/5 hover:text-slate-200',
                      collapsed && 'justify-center px-2'
                    )
                  }
                  title={collapsed ? item.label : undefined}
                >
                  <span className="shrink-0">{item.icon}</span>
                  {!collapsed && <span className="truncate font-medium">{item.label}</span>}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* Bottom actions */}
        <div className="border-t border-white/5 p-3 flex flex-col gap-2">
          {/* Collapse toggle (desktop) */}
          <button
            onClick={() => setCollapsed((c) => !c)}
            className={clsx(
              'hidden lg:flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-500 transition hover:bg-white/5 hover:text-slate-300',
              collapsed && 'justify-center px-2'
            )}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? (
              <ChevronRight className="h-5 w-5" />
            ) : (
              <>
                <ChevronLeft className="h-5 w-5 shrink-0" />
                <span>Collapse</span>
              </>
            )}
          </button>
        </div>
      </aside>

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-white/5 bg-surface-900/80 backdrop-blur-sm px-6">
          {/* Mobile menu button */}
          <button
            className="lg:hidden rounded-lg p-2 text-slate-400 hover:bg-white/5 hover:text-white"
            onClick={() => setMobileOpen(true)}
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5" />
          </button>

          {/* Breadcrumb */}
          <div className="hidden lg:flex items-center gap-2 text-sm">
            <span className="text-slate-600">DataForge</span>
            <span className="text-slate-700">/</span>
            <span className="text-slate-300 font-medium">{currentPage?.label ?? 'Dashboard'}</span>
          </div>

          {/* Right actions */}
          <div className="flex items-center gap-2 ml-auto">
            <div className="flex items-center gap-1.5 rounded-full bg-green-500/10 border border-green-500/20 px-3 py-1">
              <span className="status-dot bg-green-500 animate-pulse-slow" />
              <span className="text-xs font-medium text-green-400">API Connected</span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <div className="page-enter h-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
