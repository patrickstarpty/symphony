import type { AggregateMetrics } from '../types'
import { fmtNumber, fmtDuration } from '../utils'

interface Props {
  aggregate: AggregateMetrics
  uptime: number
  runningCount: number
  retryCount: number
}

interface StatCardProps {
  label: string
  value: string | number
  color?: string
}

function StatCard({ label, value, color = 'text-sky-400' }: StatCardProps) {
  return (
    <div className="text-center">
      <div className={`text-3xl font-bold ${color}`}>{value}</div>
      <div className="mt-1 text-xs text-slate-400">{label}</div>
    </div>
  )
}

export default function OverviewStats({ aggregate, uptime, runningCount, retryCount }: Props) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800 p-5">
      <h2 className="mb-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
        Overview
      </h2>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <StatCard label="Running" value={runningCount} color="text-blue-400" />
        <StatCard label="Completed" value={aggregate.successful_sessions} color="text-green-400" />
        <StatCard label="Failed" value={aggregate.failed_sessions} color="text-red-400" />
        <StatCard label="Retrying" value={retryCount} color="text-amber-400" />
        <StatCard label="Total Tokens" value={fmtNumber(aggregate.total_tokens)} />
        <StatCard label="Uptime" value={fmtDuration(uptime)} color="text-slate-300" />
      </div>
    </div>
  )
}
