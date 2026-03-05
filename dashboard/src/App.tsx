import { useCallback } from 'react'
import { fetchState, triggerRefresh } from './api'
import { usePolling } from './hooks/usePolling'
import OverviewStats from './components/OverviewStats'
import RunningTable from './components/RunningTable'
import RetryQueue from './components/RetryQueue'
import RecentSessions from './components/RecentSessions'
import ConfigCard from './components/ConfigCard'

export default function App() {
  const fetcher = useCallback(() => fetchState(), [])
  const { data, error, loading, refresh } = usePolling(fetcher, 3000)

  const handleRefresh = async () => {
    await triggerRefresh()
    refresh()
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-sky-400">&#9835; Symphony</h1>
          <p className="text-sm text-slate-400">Coding Agent Orchestrator</p>
        </div>
        <button
          onClick={handleRefresh}
          className="rounded-lg border border-slate-600 bg-slate-800 px-4 py-2 text-sm text-slate-200 transition hover:bg-slate-700"
        >
          &#8634; Refresh
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-800 bg-red-900/40 px-4 py-3 text-sm text-red-300">
          Failed to fetch state: {error}
        </div>
      )}

      {/* Loading */}
      {loading && !data && (
        <div className="py-20 text-center text-slate-400">Loading...</div>
      )}

      {/* Main content */}
      {data && (
        <div className="flex flex-col gap-4">
          <OverviewStats
            aggregate={data.metrics.aggregate}
            uptime={data.metrics.uptime_seconds}
            runningCount={data.running.length}
            retryCount={data.retry_queue.length}
          />
          <RunningTable sessions={data.running} />
          <RetryQueue entries={data.retry_queue} />
          <RecentSessions sessions={data.metrics.recent_sessions} />
          <ConfigCard config={data.config} />
        </div>
      )}
    </div>
  )
}
