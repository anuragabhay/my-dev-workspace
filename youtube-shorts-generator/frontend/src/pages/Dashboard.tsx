import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle, XCircle, Zap, Film } from 'lucide-react'
import { api, type HealthResult, type Execution } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export function Dashboard() {
  const [health, setHealth] = useState<HealthResult | null>(null)
  const [recent, setRecent] = useState<Execution[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.health(), api.history(5, 0)])
      .then(([h, { executions }]) => {
        setHealth(h)
        setRecent(executions)
      })
      .catch(() => setHealth({ ok: false, checks: {} }))
      .finally(() => setLoading(false))
  }, [])

  const checks = health?.checks ?? {}
  const passed = Object.values(checks).filter((c) => c.pass).length
  const total = Object.keys(checks).length

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-zinc-400">System health and quick actions</p>
      </div>

      {loading ? (
        <div className="text-zinc-400">Loading...</div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Card className="border-zinc-800 bg-zinc-900/50">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <CheckCircle className="h-4 w-4 text-emerald-500" />
                  Health
                </CardTitle>
                <CardDescription>
                  {passed}/{total} checks passed
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-1.5">
                  {Object.entries(checks).map(([name, { pass }]) => (
                    <Badge
                      key={name}
                      variant={pass ? 'success' : 'destructive'}
                      className="capitalize"
                    >
                      {name.replace(/_/g, ' ')}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
            <Card className="border-zinc-800 bg-zinc-900/50">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Zap className="h-4 w-4 text-amber-500" />
                  Quick Generate
                </CardTitle>
                <CardDescription>Start a new video generation</CardDescription>
              </CardHeader>
              <CardContent>
                <Link to="/generate">
                  <Button className="w-full">New Short</Button>
                </Link>
              </CardContent>
            </Card>
            <Card className="border-zinc-800 bg-zinc-900/50 sm:col-span-2 lg:col-span-1">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Film className="h-4 w-4 text-red-500" />
                  Recent
                </CardTitle>
                <CardDescription>Latest executions</CardDescription>
              </CardHeader>
              <CardContent>
                {recent.length === 0 ? (
                  <p className="text-sm text-zinc-500">No executions yet</p>
                ) : (
                  <ul className="space-y-2">
                    {recent.map((e) => (
                      <li key={e.id}>
                        <Link
                          to={`/execution/${e.id}`}
                          className="flex items-center justify-between rounded-lg px-2 py-1.5 text-sm hover:bg-zinc-800/50"
                        >
                          <span className="truncate">#{e.id} {e.topic || 'Untitled'}</span>
                          <Badge
                            variant={
                              e.status === 'completed'
                                ? 'success'
                                : e.status === 'failed'
                                  ? 'destructive'
                                  : 'secondary'
                            }
                          >
                            {e.status}
                          </Badge>
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          </div>

          {health && !health.ok && (
            <Card className="border-amber-500/50 bg-amber-500/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-amber-500">
                  <XCircle className="h-4 w-4" />
                  Health Check Failed
                </CardTitle>
                <CardDescription>
                  Some required checks failed. Fix the issues before generating.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="overflow-auto rounded-lg bg-zinc-900 p-4 text-xs">
                  {JSON.stringify(health.checks, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
