import { useEffect, useState } from 'react'
import { Save, X } from 'lucide-react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

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
    return (
      <div className="space-y-8">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Configuration</h1>
        <p className="mt-1 text-zinc-400">View and edit pipeline settings</p>
      </div>

      <Card className="border-zinc-800 bg-zinc-900/50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>config.yaml</CardTitle>
              <CardDescription className="mt-1">
                API keys and secrets are never exposed. Changes are written to disk.
              </CardDescription>
            </div>
            {!editMode && (
              <Button onClick={() => setEditMode(true)} variant="outline" className="border-zinc-700">
                Edit
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {editMode ? (
            <>
              <textarea
                value={editJson}
                onChange={(e) => setEditJson(e.target.value)}
                className="h-96 w-full rounded-lg border border-zinc-700 bg-zinc-950 p-4 font-mono text-sm text-zinc-300 focus:border-zinc-500 focus:outline-none focus:ring-1 focus:ring-zinc-500"
                spellCheck={false}
              />
              {error && (
                <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                  {error}
                </div>
              )}
              <div className="flex gap-2">
                <Button onClick={handleSave} disabled={saving} className="bg-red-600 hover:bg-red-700 text-white">
                  <Save className="mr-2 h-4 w-4" />
                  {saving ? 'Saving...' : 'Save Changes'}
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
                  <X className="mr-2 h-4 w-4" />
                  Cancel
                </Button>
              </div>
            </>
          ) : (
            <pre className="overflow-auto rounded-lg border border-zinc-800 bg-zinc-950 p-4 text-sm text-zinc-300">
              {JSON.stringify(config, null, 2)}
            </pre>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
