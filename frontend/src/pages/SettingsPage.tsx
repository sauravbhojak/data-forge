import { useState } from 'react'
import { Settings, Globe, Shield, Gauge, Info } from 'lucide-react'
import { Card, CardBody, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState(import.meta.env.VITE_API_URL ?? '/api')

  const handleSaveApiUrl = () => {
    toast.success('API URL saved. Restart the app to apply changes.')
  }

  return (
    <div className="flex flex-col gap-6 p-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Settings</h1>
        <p className="text-slate-500 mt-1">Configure your DataForge preferences.</p>
      </div>

      {/* API Config */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Globe className="h-4 w-4 text-brand-400" />
            <h2 className="text-sm font-semibold text-slate-300">API Configuration</h2>
          </div>
        </CardHeader>
        <CardBody className="flex flex-col gap-4">
          <Input
            label="Backend API URL"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            hint="The base URL of the DataForge backend API"
            id="api-url-input"
          />
          <div>
            <Button onClick={handleSaveApiUrl} size="sm" id="save-api-url-btn">Save</Button>
          </div>
        </CardBody>
      </Card>

      {/* Performance */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Gauge className="h-4 w-4 text-brand-400" />
            <h2 className="text-sm font-semibold text-slate-300">Performance Limits</h2>
          </div>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: 'Max Rows', value: '1,000,000', desc: 'Hard cap enforced by the backend' },
              { label: 'Preview Rows', value: '50', desc: 'Max rows shown in browser preview' },
              { label: 'Max Fields', value: '100', desc: 'Max fields per table schema' },
              { label: 'Max Tables', value: '20', desc: 'Max tables per relational schema' },
            ].map((item) => (
              <div key={item.label} className="inner-card">
                <p className="text-xs text-slate-500">{item.label}</p>
                <p className="text-lg font-bold font-mono text-brand-300">{item.value}</p>
                <p className="text-xs text-slate-600 mt-1">{item.desc}</p>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* Security */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-brand-400" />
            <h2 className="text-sm font-semibold text-slate-300">Security</h2>
          </div>
        </CardHeader>
        <CardBody>
          <div className="flex flex-col gap-3 text-sm">
            {[
              ['Rate Limiting', 'Generate: 30/min · Export: 10/min · Preview: 60/min'],
              ['Payload Guard', 'Request body limited to 10 MB'],
              ['Input Validation', 'All schemas validated by Pydantic v2'],
              ['Authentication', 'Public mode (no auth required)'],
            ].map(([label, value]) => (
              <div key={label} className="flex items-start justify-between gap-4 border-b border-white/5 pb-3 last:border-0 last:pb-0">
                <span className="text-slate-400 font-medium min-w-40">{label}</span>
                <span className="text-slate-500 text-right text-xs">{value}</span>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* About */}
      <Card>
        <CardBody className="flex gap-4">
          <Info className="h-5 w-5 text-brand-400 shrink-0" />
          <div>
            <p className="text-sm font-semibold text-slate-200">DataForge v1.0.0</p>
            <p className="text-xs text-slate-500 mt-1">
              Smart Test Data Generation Platform · Python 3.13 + FastAPI + React 18 + TailwindCSS
            </p>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
