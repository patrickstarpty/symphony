/** API client for Symphony REST endpoints. */

import type { OrchestratorState, HealthResponse, SessionMetrics } from './types'

const BASE = '/api/v1'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init)
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

export function fetchState(): Promise<OrchestratorState> {
  return request<OrchestratorState>('/state')
}

export function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health')
}

export function fetchSession(sessionId: string): Promise<SessionMetrics> {
  return request<SessionMetrics>(`/sessions/${sessionId}`)
}

export function triggerRefresh(): Promise<{ status: string }> {
  return request<{ status: string }>('/refresh', { method: 'POST' })
}
