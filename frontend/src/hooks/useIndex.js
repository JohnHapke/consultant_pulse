import { useState, useEffect } from 'react'

/**
 * Fetches /data/index.json to resolve current and historical pulse files.
 * index.json is written by the Python pipeline after each run.
 */
export function useIndex() {
  const [index, setIndex] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/index.json`)
      .then(r => {
        if (!r.ok) throw new Error(`index.json not found (HTTP ${r.status})`)
        return r.json()
      })
      .then(d => { setIndex(d); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [])

  return { index, loading, error }
}
