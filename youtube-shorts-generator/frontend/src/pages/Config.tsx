import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function Config() {
  const [config, setConfig] = useState<Record<string, unknown> | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editJson, setEditJson] = useState('')
  const [editMode, setEditMode] = useState(false)

  useEffect(() => {
    api.config
      .get()
      .then((c) => {
        setConfig(c)
        setEditJson(JSON.stringify(c, null, 2))
      })
      .catch(() => setConfig({}))
      .finally(() => setLoading(false))
  }, [])

  async function handleSave() {
    setError(null)
    setSaving(true)
    try {
      const parsed = JSON.parse(editJson) as Record<string, unknown>
      await api.config.put(parsed)
      setConfig(parsed)
      setEditMode(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Invalid JSON')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <p className="text-zinc-400">Loading...</p>
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Config</h1>
        <p className="text-zinc-400">View and edit non-secret configuration</p>
      </div>

      <Card className="border-zinc-800 bg-zinc-900/50">
        <CardHeader>
          <CardTitle>config.yaml (non-secret)</CardTitle>
          <CardDescription>
            API keys and secrets are not exposed. Changes are written to config.yaml.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {editMode ? (
            <>
              <textarea
                value={editJson}
                onChange={(e) => setEditJson(e.target.value)}
                className="h-96 w-full rounded-lg border border-zinc-700 bg-zinc-900 p-4 font-mono text-sm"
                spellCheck={false}
              />
              {error && <p className="text-sm text-red-500">{error}</p>}
              <div className="flex gap-2">
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? 'Saving...' : 'Save'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setEditMode(false)
                    setEditJson(JSON.stringify(config, null, 2))
                    setError(null)
                  }}
                  className="border-zinc-700"
                >
                  Cancel
                </Button>
              </div>
            </>
          ) : (
            <>
              <pre className="overflow-auto rounded-lg bg-zinc-900 p-4 text-sm">
                {JSON.stringify(config, null, 2)}
              </pre>
              <Button onClick={() => setEditMode(true)}>Edit</Button>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
