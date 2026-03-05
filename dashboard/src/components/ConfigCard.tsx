import type { Config } from '../types'

interface Props {
  config: Config
}

export default function ConfigCard({ config }: Props) {
  const items = [
    { label: 'Project', value: config.name },
    { label: 'Model', value: config.agent_model },
    { label: 'Tracker', value: config.tracker_kind },
    { label: 'Poll Interval', value: `${config.poll_seconds}s` },
    { label: 'Max Concurrent', value: config.max_concurrent_agents },
    { label: 'Max Turns', value: config.max_turns },
    { label: 'Max Retries', value: config.max_retries },
  ]

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800 p-5">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
        Configuration
      </h2>
      <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-3 lg:grid-cols-4">
        {items.map(({ label, value }) => (
          <div key={label}>
            <span className="text-slate-400">{label}: </span>
            <span className="font-medium text-slate-200">{value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
