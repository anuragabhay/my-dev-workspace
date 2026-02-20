import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Film, AlertTriangle } from 'lucide-react'
import { api, type ExecutionStatus } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'

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
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-6 lg:grid-cols-2">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
      </div>
    )
  }

  if (!status) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <AlertTriangle className="mb-4 h-12 w-12 text-zinc-600" />
        <p className="text-lg font-medium text-zinc-400">Execution not found</p>
        <p className="mt-1 text-sm text-zinc-500">ID #{id} does not exist</p>
        <Link to="/history" className="mt-6">
          <Button variant="outline" className="border-zinc-700">
            <ArrowLeft className="mr-2 h-4 w-4" />
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
          <Button variant="ghost" size="sm" className="text-zinc-400 hover:text-white">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
        </Link>
      </div>

      <div>
        <h1 className="text-3xl font-bold tracking-tight">Execution #{id}</h1>
        <p className="mt-1 text-zinc-400">{status.topic || 'No topic specified'}</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-zinc-800 bg-zinc-900/50">
          <CardHeader>
            <CardTitle>Status</CardTitle>
            <CardDescription>Current state and cost breakdown</CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="flex items-center gap-3">
              <Badge
                variant={
                  status.status === 'completed'
                    ? 'success'
                    : status.status === 'failed'
                      ? 'destructive'
                      : 'secondary'
                }
                className="text-sm px-3 py-1"
              >
                {status.status}
              </Badge>
              {status.current_stage && (
                <span className="rounded-md bg-zinc-800 px-2 py-1 text-xs text-zinc-400">
                  Stage: {status.current_stage}
                </span>
              )}
            </div>
            <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-4">
              <span className="text-sm text-zinc-500">Total Cost</span>
              <p className="mt-1 text-2xl font-bold font-mono">${status.cost.toFixed(2)}</p>
            </div>
            {status.error_message && (
              <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
                <p className="font-medium">Error</p>
                <p className="mt-1 text-red-400/80">{status.error_message}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {hasVideo && (
          <Card className="border-zinc-800 bg-zinc-900/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Film className="h-4 w-4 text-red-500" />
                Video Preview
              </CardTitle>
              <CardDescription>Generated output</CardDescription>
            </CardHeader>
            <CardContent>
              <video
                src={api.videoUrl(status.execution_id)}
                controls
                className="w-full rounded-lg border border-zinc-800 bg-black"
              >
                Your browser does not support video playback.
              </video>
            </CardContent>
          </Card>
        )}
      </div>

      {status.status === 'in_progress' && (
        <Card className="border-amber-500/30 bg-amber-500/5">
          <CardHeader>
            <CardTitle className="text-amber-400">Pipeline Running</CardTitle>
            <CardDescription className="text-amber-400/70">
              Go to the Generate page for real-time WebSocket progress
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/generate">
              <Button className="bg-amber-600 hover:bg-amber-700 text-white">
                View Live Progress
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
