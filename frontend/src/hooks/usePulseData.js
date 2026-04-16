import { useState, useEffect } from 'react'

export function usePulseData(file) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!file) { setLoading(false); setData(null); return }
    setLoading(true)
    setError(null)
    fetch(`/data/${file}`)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(d => { setData(d); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [file])

  return { data, loading, error }
}
