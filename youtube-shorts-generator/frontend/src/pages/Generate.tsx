import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, Zap } from 'lucide-react'
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
        <h1 className="text-3xl font-bold tracking-tight">Generate Short</h1>
        <p className="mt-1 text-zinc-400">Create a new YouTube Short from a topic</p>
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
              />
            </div>
            {error && (
              <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                {error}
              </div>
            )}
            <Button type="submit" disabled={loading} className="bg-red-600 hover:bg-red-700 text-white">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Zap className="mr-2 h-4 w-4" />
                  Start Generation
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {executionId && (
        <Card className="border-zinc-800 bg-zinc-900/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Pipeline Progress
              {connected && (
                <span className="flex h-2.5 w-2.5 items-center justify-center">
                  <span className="absolute h-2.5 w-2.5 animate-ping rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative h-2 w-2 rounded-full bg-emerald-500" />
                </span>
              )}
            </CardTitle>
            <CardDescription>
              Execution #{executionId} — real-time updates via WebSocket
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-400">Progress</span>
                <span className="font-mono text-zinc-300">{Math.round(percent)}%</span>
              </div>
              <Progress value={percent} />
            </div>
            <div className="max-h-48 space-y-1 overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-950 p-3 font-mono text-xs">
              {events.length === 0 ? (
                <span className="text-zinc-600">Waiting for pipeline events...</span>
              ) : (
                events.map((ev, i) => (
                  <div key={i} className="text-zinc-400">
                    <span className="text-amber-500">[{ev.agent}]</span>{' '}
                    <span className="text-zinc-500">{ev.step}:</span> {ev.log}
                  </div>
                ))
              )}
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
