import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Film } from 'lucide-react'
import { api, type ExecutionStatus } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export function ExecutionDetail() {
  const { id } = useParams<{ id: string }>()
  const [status, setStatus] = useState<ExecutionStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    const n = parseInt(id, 10)
    if (Number.isNaN(n)) return
    api
      .status(n)
      .then(setStatus)
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    if (!id || !status) return
    if (status.status === 'in_progress' || status.status === 'pending') {
      const t = setInterval(() => {
        api.status(parseInt(id, 10)).then(setStatus)
      }, 2000)
      return () => clearInterval(t)
    }
  }, [id, status?.status])

  if (!id || loading) {
    return (
      <div className="space-y-8">
        <p className="text-zinc-400">Loading...</p>
      </div>
    )
  }

  if (!status) {
    return (
      <div className="space-y-8">
        <p className="text-red-500">Execution not found</p>
        <Link to="/history">
          <Button variant="outline" className="border-zinc-700">
            Back to History
          </Button>
        </Link>
      </div>
    )
  }

  const hasVideo = status.output_path && status.status === 'completed'

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <Link to="/history">
          <Button variant="ghost" size="sm" className="text-zinc-400">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
        </Link>
      </div>

      <div>
        <h1 className="text-2xl font-bold tracking-tight">Execution #{id}</h1>
        <p className="text-zinc-400">{status.topic || 'No topic'}</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-zinc-800 bg-zinc-900/50">
          <CardHeader>
            <CardTitle>Status</CardTitle>
            <CardDescription>Current state and cost</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge
                variant={
                  status.status === 'completed'
                    ? 'success'
                    : status.status === 'failed'
                      ? 'destructive'
                      : 'secondary'
                }
              >
                {status.status}
              </Badge>
              {status.current_stage && (
                <span className="text-sm text-zinc-400">Stage: {status.current_stage}</span>
              )}
            </div>
            <div>
              <span className="text-sm text-zinc-500">Cost: </span>
              <span className="font-mono">${status.cost.toFixed(2)}</span>
            </div>
            {status.error_message && (
              <div className="rounded-lg bg-red-500/10 p-3 text-sm text-red-400">
                {status.error_message}
              </div>
            )}
          </CardContent>
        </Card>

        {hasVideo && (
          <Card className="border-zinc-800 bg-zinc-900/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Film className="h-4 w-4" />
                Video Preview
              </CardTitle>
              <CardDescription>Generated output</CardDescription>
            </CardHeader>
            <CardContent>
              <video
                src={api.videoUrl(status.execution_id)}
                controls
                className="w-full rounded-lg bg-black"
              >
                Your browser does not support video playback.
              </video>
            </CardContent>
          </Card>
        )}
      </div>

      {status.status === 'in_progress' && (
        <Card className="border-zinc-800 bg-zinc-900/50">
          <CardHeader>
            <CardTitle>Live Progress</CardTitle>
            <CardDescription>Connect to Generate page for WebSocket updates</CardDescription>
          </CardHeader>
          <CardContent>
            <Link to={`/generate`}>
              <Button variant="outline" className="border-zinc-700">
                Go to Generate
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
