import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Film } from 'lucide-react'
import { api, type Execution } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'

const PAGE_SIZE = 10

export function History() {
  const [executions, setExecutions] = useState<Execution[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    api
      .history(PAGE_SIZE, page * PAGE_SIZE)
      .then(({ executions: ex, total: t }) => {
        setExecutions(ex)
        setTotal(t)
      })
      .finally(() => setLoading(false))
  }, [page])

  const totalPages = Math.ceil(total / PAGE_SIZE)

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">History</h1>
        <p className="mt-1 text-zinc-400">All past generation runs</p>
      </div>

      <Card className="border-zinc-800 bg-zinc-900/50">
        <CardHeader>
          <CardTitle>Executions</CardTitle>
          <CardDescription>{total} total</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : executions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Film className="mb-4 h-12 w-12 text-zinc-700" />
              <p className="text-lg font-medium text-zinc-400">No executions yet</p>
              <p className="mt-1 text-sm text-zinc-500">
                Start generating shorts to see them here
              </p>
              <Link to="/generate" className="mt-4">
                <Button className="bg-red-600 hover:bg-red-700 text-white">Generate First Short</Button>
              </Link>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-zinc-800 text-left">
                      <th className="pb-3 pr-4 text-xs font-semibold uppercase tracking-wider text-zinc-500">ID</th>
                      <th className="pb-3 pr-4 text-xs font-semibold uppercase tracking-wider text-zinc-500">Topic</th>
                      <th className="pb-3 pr-4 text-xs font-semibold uppercase tracking-wider text-zinc-500">Status</th>
                      <th className="pb-3 pr-4 text-xs font-semibold uppercase tracking-wider text-zinc-500">Stage</th>
                      <th className="pb-3 pr-4 text-xs font-semibold uppercase tracking-wider text-zinc-500">Cost</th>
                      <th className="pb-3 text-xs font-semibold uppercase tracking-wider text-zinc-500"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/50">
                    {executions.map((e) => (
                      <tr key={e.id} className="transition-colors hover:bg-zinc-800/30">
                        <td className="py-3.5 pr-4 font-mono text-zinc-400">{e.id}</td>
                        <td className="py-3.5 pr-4 truncate max-w-[240px] text-zinc-200">
                          {e.topic || <span className="text-zinc-500">—</span>}
                        </td>
                        <td className="py-3.5 pr-4">
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
                        </td>
                        <td className="py-3.5 pr-4 text-zinc-500">{e.current_stage || '—'}</td>
                        <td className="py-3.5 pr-4 font-mono text-zinc-400">
                          {e.cost_total != null ? `$${e.cost_total.toFixed(2)}` : '—'}
                        </td>
                        <td className="py-3.5">
                          <Link to={`/execution/${e.id}`}>
                            <Button variant="ghost" size="sm" className="text-zinc-400 hover:text-white">
                              View
                            </Button>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {totalPages > 1 && (
                <div className="mt-4 flex items-center justify-between border-t border-zinc-800 pt-4">
                  <p className="text-sm text-zinc-500">
                    Page {page + 1} of {totalPages}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.max(0, p - 1))}
                      disabled={page === 0}
                      className="border-zinc-700"
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                      disabled={page >= totalPages - 1}
                      className="border-zinc-700"
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
