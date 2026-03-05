/** Type definitions matching the Symphony REST API responses. */

export interface Config {
  name: string
  poll_seconds: number
  max_concurrent_agents: number
  max_turns: number
  max_retries: number
  agent_model: string
  tracker_kind: string
}

export interface RunningSession {
  issue_id: string
  issue_identifier: string
  issue_title: string
  issue_state: string
  workspace_path: string
  session_id: string
  started_at: number
  last_event_at: number
  duration_seconds: number
  stall_seconds: number
  turns: number
}

export interface RetryEntry {
  issue_id: string
  issue_identifier: string
  issue_title: string
  attempt: number
  next_retry_at: number
  retry_in_seconds: number
  last_error: string
}

export interface SessionMetrics {
  session_id: string
  issue_id: string
  issue_identifier: string
  issue_title: string
  started_at: number
  finished_at: number | null
  duration_seconds: number
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  turns: number
  status: 'running' | 'success' | 'failed'
  error: string
}

export interface AggregateMetrics {
  total_sessions: number
  successful_sessions: number
  failed_sessions: number
  running_sessions: number
  total_prompt_tokens: number
  total_completion_tokens: number
  total_tokens: number
  total_runtime_seconds: number
  rate_limit_events: number
}

export interface MetricsSnapshot {
  uptime_seconds: number
  aggregate: AggregateMetrics
  running_sessions: SessionMetrics[]
  recent_sessions: SessionMetrics[]
}

export interface OrchestratorState {
  config: Config
  running: RunningSession[]
  retry_queue: RetryEntry[]
  completed_count: number
  failed_count: number
  completed_ids: string[]
  failed_ids: string[]
  metrics: MetricsSnapshot
}

export interface HealthResponse {
  status: string
  uptime_seconds: number
  orchestrator_running: boolean
  running_sessions: number
}
