interface Props {
  status: 'running' | 'success' | 'failed' | 'retry' | string
}

const styles: Record<string, string> = {
  running: 'bg-blue-700 text-blue-100',
  success: 'bg-green-700 text-green-100',
  failed: 'bg-red-700 text-red-100',
  retry: 'bg-amber-700 text-amber-100',
}

export default function StatusBadge({ status }: Props) {
  const cls = styles[status] ?? 'bg-slate-600 text-slate-200'
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${cls}`}>
      {status}
    </span>
  )
}
