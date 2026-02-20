import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle, XCircle, Zap, Film, Activity } from 'lucide-react'
import { api, type HealthResult, type Execution } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'

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
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-zinc-400">System overview and quick actions</p>
      </div>

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="border-zinc-800 bg-zinc-900/50">
              <CardHeader className="pb-3">
                <Skeleton className="h-5 w-24" />
                <Skeleton className="mt-2 h-4 w-32" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {/* Health card */}
            <Card className="border-zinc-800 bg-zinc-900/50">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Activity className="h-4 w-4 text-emerald-500" />
                  System Health
                </CardTitle>
                <CardDescription>
                  {passed}/{total} checks passed
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(checks).map(([name, { pass }]) => (
                    <Badge key={name} variant={pass ? 'success' : 'destructive'}>
                      {pass ? (
                        <CheckCircle className="mr-1 h-3 w-3" />
                      ) : (
                        <XCircle className="mr-1 h-3 w-3" />
                      )}
                      {name.replace(/_/g, ' ')}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Quick generate card */}
            <Card className="border-zinc-800 bg-zinc-900/50">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Zap className="h-4 w-4 text-amber-500" />
                  Quick Generate
                </CardTitle>
                <CardDescription>Create a new YouTube Short</CardDescription>
              </CardHeader>
              <CardContent>
                <Link to="/generate">
                  <Button className="w-full bg-red-600 hover:bg-red-700 text-white">
                    <Zap className="mr-2 h-4 w-4" />
                    New Short
                  </Button>
                </Link>
              </CardContent>
            </Card>

            {/* Recent card */}
            <Card className="border-zinc-800 bg-zinc-900/50 sm:col-span-2 lg:col-span-1">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center justify-between text-base">
                  <span className="flex items-center gap-2">
                    <Film className="h-4 w-4 text-red-500" />
                    Recent
                  </span>
                  <Link to="/history" className="text-xs text-zinc-400 hover:text-zinc-200">
                    View all
                  </Link>
                </CardTitle>
                <CardDescription>Latest executions</CardDescription>
              </CardHeader>
              <CardContent>
                {recent.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-6 text-center">
                    <Film className="mb-3 h-10 w-10 text-zinc-700" />
                    <p className="text-sm text-zinc-500">No executions yet</p>
                    <p className="mt-1 text-xs text-zinc-600">
                      Generate your first short to see it here
                    </p>
                  </div>
                ) : (
                  <ul className="space-y-1">
                    {recent.map((e) => (
                      <li key={e.id}>
                        <Link
                          to={`/execution/${e.id}`}
                          className="flex items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors hover:bg-zinc-800/60"
                        >
                          <span className="truncate text-zinc-200">
                            <span className="font-mono text-zinc-500">#{e.id}</span>{' '}
                            {e.topic || 'Untitled'}
                          </span>
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
            <Card className="border-amber-500/30 bg-amber-500/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-amber-400">
                  <XCircle className="h-5 w-5" />
                  Health Check Issues
                </CardTitle>
                <CardDescription className="text-amber-400/70">
                  Some required checks failed. Review and fix before generating.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="overflow-auto rounded-lg border border-zinc-800 bg-zinc-900 p-4 text-xs text-zinc-300">
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
