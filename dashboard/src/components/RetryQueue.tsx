import type { RetryEntry } from '../types'
import StatusBadge from './StatusBadge'
import { fmtDuration } from '../utils'

interface Props {
  entries: RetryEntry[]
}

export default function RetryQueue({ entries }: Props) {
  if (entries.length === 0) {
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-800 p-5">
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
          Retry Queue
        </h2>
        <p className="italic text-slate-500">No retries queued</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800 p-5">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
        Retry Queue
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 text-left text-xs uppercase text-slate-400">
              <th className="px-3 py-2">Issue</th>
              <th className="px-3 py-2">Attempt</th>
              <th className="px-3 py-2">Retry In</th>
              <th className="px-3 py-2">Last Error</th>
              <th className="px-3 py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((e) => (
              <tr key={e.issue_id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                <td className="px-3 py-2">
                  <span className="font-medium text-slate-200">{e.issue_identifier}</span>
                  <span className="ml-2 text-slate-400">{e.issue_title}</span>
                </td>
                <td className="px-3 py-2">#{e.attempt}</td>
                <td className="px-3 py-2">{fmtDuration(e.retry_in_seconds)}</td>
                <td className="max-w-xs truncate px-3 py-2 text-slate-400">
                  {e.last_error}
                </td>
                <td className="px-3 py-2">
                  <StatusBadge status="retry" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
