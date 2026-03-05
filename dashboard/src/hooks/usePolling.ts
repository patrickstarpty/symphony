import { useEffect, useRef, useState, useCallback } from 'react'

/**
 * Poll a fetcher function at a fixed interval.
 * Returns { data, error, loading, refresh }.
 */
export function usePolling<T>(
  fetcher: () => Promise<T>,
  intervalMs: number = 3000,
) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const mountedRef = useRef(true)

  const doFetch = useCallback(async () => {
    try {
      const result = await fetcher()
      if (mountedRef.current) {
        setData(result)
        setError(null)
        setLoading(false)
      }
    } catch (err: unknown) {
      if (mountedRef.current) {
        setError(err instanceof Error ? err.message : String(err))
        setLoading(false)
      }
    }
  }, [fetcher])

  // Manual refresh
  const refresh = useCallback(() => {
    setLoading(true)
    doFetch()
  }, [doFetch])

  useEffect(() => {
    mountedRef.current = true
    doFetch()
    timerRef.current = setInterval(doFetch, intervalMs)
    return () => {
      mountedRef.current = false
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [doFetch, intervalMs])

  return { data, error, loading, refresh }
}
