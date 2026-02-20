import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import { useWebSocket } from '@/hooks/useWebSocket'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'

export function Generate() {
  const [topic, setTopic] = useState('')
  const [executionId, setExecutionId] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const { events, connected } = useWebSocket(executionId, !!executionId && loading)

  const percent = events.length > 0 ? events[events.length - 1].percent : 0

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const { execution_id } = await api.generate(topic || undefined)
      setExecutionId(execution_id)
      setLoading(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start')
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Generate Short</h1>
        <p className="text-zinc-400">Create a new YouTube Short from a topic</p>
      </div>

      <Card className="border-zinc-800 bg-zinc-900/50">
        <CardHeader>
          <CardTitle>New Generation</CardTitle>
          <CardDescription>Enter a topic or leave blank for auto-research</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-medium text-zinc-300">Topic</label>
              <Input
                placeholder="e.g. Benefits of morning meditation"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                disabled={loading}
                className="border-zinc-700 bg-zinc-900"
              />
            </div>
            {error && (
              <p className="text-sm text-red-500">{error}</p>
            )}
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Starting...
                </>
              ) : (
                'Start Generation'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {executionId && (
        <Card className="border-zinc-800 bg-zinc-900/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Progress
              {connected && (
                <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" />
              )}
            </CardTitle>
            <CardDescription>
              Execution #{executionId} — real-time updates
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Progress value={percent} />
            <div className="max-h-48 space-y-1 overflow-y-auto rounded-lg bg-zinc-900/50 p-3 font-mono text-xs">
              {events.map((ev, i) => (
                <div key={i} className="text-zinc-400">
                  <span className="text-amber-500">{ev.agent}</span> {ev.step}: {ev.log}
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => navigate(`/execution/${executionId}`)}
                className="border-zinc-700"
              >
                View Details
              </Button>
              <Button
                variant="secondary"
                onClick={() => {
                  setExecutionId(null)
                  setLoading(false)
                  setTopic('')
                }}
                className="bg-zinc-800"
              >
                New Generation
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
