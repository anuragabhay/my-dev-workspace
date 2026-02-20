import { useEffect, useRef, useState, useCallback } from 'react'

export interface ProgressEvent {
  agent: string
  step: string
  percent: number
  log: string
}

export function useWebSocket(executionId: number | null, enabled: boolean) {
  const [events, setEvents] = useState<ProgressEvent[]>([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  const connect = useCallback(() => {
    if (!executionId || !enabled) return
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${location.host}/ws/progress/${executionId}`)
    wsRef.current = ws
    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data) as ProgressEvent
        setEvents((prev) => [...prev, data])
      } catch {
        // ignore
      }
    }
    ws.onerror = () => setConnected(false)
  }, [executionId, enabled])

  useEffect(() => {
    if (!executionId || !enabled) return
    setEvents([])
    connect()
    return () => {
      wsRef.current?.close()
      wsRef.current = null
      setConnected(false)
    }
  }, [executionId, enabled, connect])

  return { events, connected }
}
