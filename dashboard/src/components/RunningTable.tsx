import type { RunningSession } from '../types'
import StatusBadge from './StatusBadge'
import { fmtDuration } from '../utils'

interface Props {
  sessions: RunningSession[]
}

export default function RunningTable({ sessions }: Props) {
  if (sessions.length === 0) {
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-800 p-5">
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
          Running Sessions
        </h2>
        <p className="italic text-slate-500">No active sessions</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800 p-5">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
        Running Sessions
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 text-left text-xs uppercase text-slate-400">
              <th className="px-3 py-2">Issue</th>
              <th className="px-3 py-2">Session</th>
              <th className="px-3 py-2">Duration</th>
              <th className="px-3 py-2">Turns</th>
              <th className="px-3 py-2">Stall</th>
              <th className="px-3 py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((s) => (
              <tr key={s.session_id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                <td className="px-3 py-2">
                  <span className="font-medium text-slate-200">{s.issue_identifier}</span>
                  <span className="ml-2 text-slate-400">{s.issue_title}</span>
                </td>
                <td className="px-3 py-2 font-mono text-xs text-slate-400">
                  {s.session_id.slice(0, 8)}
                </td>
                <td className="px-3 py-2">{fmtDuration(s.duration_seconds)}</td>
                <td className="px-3 py-2">{s.turns}</td>
                <td className="px-3 py-2 text-slate-400">{fmtDuration(s.stall_seconds)}</td>
                <td className="px-3 py-2">
                  <StatusBadge status="running" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
