export interface HealthCheck {
  pass: boolean
  detail?: Record<string, unknown>
}

export interface HealthResult {
  ok: boolean
  checks: Record<string, HealthCheck>
}

export interface Execution {
  id: number
  status: string
  start_time: string | null
  end_time: string | null
  current_stage: string | null
  error_message: string | null
  cost_total: number | null
  topic?: string | null
}

export interface ExecutionStatus {
  execution_id: number
  status: string
  current_stage: string | null
  cost: number
  error_message: string | null
  output_path: string | null
  topic: string | null
}

export interface ConfigData {
  [key: string]: unknown
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init)
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(text || `${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  health: () => request<HealthResult>('/api/health'),

  history: (limit = 10, offset = 0, status?: string) => {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) })
    if (status) params.set('status', status)
    return request<{ executions: Execution[]; total: number }>(
      `/api/history?${params.toString()}`
    )
  },

  status: (id: number) => request<ExecutionStatus>(`/api/status/${id}`),

  generate: (topic?: string, configOverrides?: Record<string, unknown>) =>
    request<{ execution_id: number }>('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: topic ?? null, config_overrides: configOverrides ?? null }),
    }),

  config: {
    get: () => request<ConfigData>('/api/config'),
    put: (data: ConfigData) =>
      request<{ ok: boolean }>('/api/config', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config: data }),
      }),
  },

  videoUrl: (executionId: number) => `/api/video/${executionId}`,
}
