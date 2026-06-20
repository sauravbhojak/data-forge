import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from '@/layouts/AppLayout'
import { Spinner } from '@/components/ui/Spinner'

// ── Lazy-loaded pages (code splitting) ───────────────────────────────────────
const Dashboard = lazy(() => import('@/pages/Dashboard'))
const TemplateGenerator = lazy(() => import('@/pages/TemplateGenerator'))
const CustomSchemaBuilder = lazy(() => import('@/pages/CustomSchemaBuilder'))
const RelationshipBuilderPage = lazy(() => import('@/pages/RelationshipBuilderPage'))
const ERDiagramViewer = lazy(() => import('@/pages/ERDiagramViewer'))
const AnalyticsGenerator = lazy(() => import('@/pages/AnalyticsGenerator'))
const ExportsPage = lazy(() => import('@/pages/ExportsPage'))
const SettingsPage = lazy(() => import('@/pages/SettingsPage'))

function PageLoader() {
  return (
    <div className="flex h-full min-h-[400px] items-center justify-center">
      <Spinner size="lg" />
    </div>
  )
}

export default function App() {
  return (
    <AppLayout>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/templates" element={<TemplateGenerator />} />
          <Route path="/schema" element={<CustomSchemaBuilder />} />
          <Route path="/relationships" element={<RelationshipBuilderPage />} />
          <Route path="/erd" element={<ERDiagramViewer />} />
          <Route path="/analytics" element={<AnalyticsGenerator />} />
          <Route path="/exports" element={<ExportsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Suspense>
    </AppLayout>
  )
}
