import { useEffect, useState } from 'react'

/**
 * Loads all pulse files of a given view (weekly/monthly) from public/data.
 * Returns time-series per consultant plus aggregated-level series, oldest-first.
 *
 * Each point on a consultant series includes rag + workload; monthly adds
 * engagement, motivation, delivery, skill_alignment, task_challenge and — when
 * a lead report exists — reliability, proactivity, skill_fit, project_status.
 */
export function useHistory(files, view) {
  const [state, setState] = useState({ loading: true, error: null, data: null })
  const key = (files ?? []).join('|')

  useEffect(() => {
    if (!files || files.length === 0) {
      setState({ loading: false, error: null, data: null })
      return
    }

    let cancelled = false
    setState({ loading: true, error: null, data: null })

    Promise.all(
      files.map(f =>
        fetch(`/data/${f}`).then(r => {
          if (!r.ok) throw new Error(`${f} not found (HTTP ${r.status})`)
          return r.json()
        })
      )
    )
      .then(all => {
        if (cancelled) return
        setState({ loading: false, error: null, data: buildHistory(all, view) })
      })
      .catch(e => {
        if (cancelled) return
        setState({ loading: false, error: e.message, data: null })
      })

    return () => { cancelled = true }
  }, [key, view])

  return state
}

function buildHistory(payloads, view) {
  for (const p of payloads) {
    if (!p.week && !p.month) {
      throw new Error('Pulse payload missing both "week" and "month" fields')
    }
  }

  // Relies on zero-padded week numbers (W01..W53) and months (01..12) for string sort.
  const sorted = [...payloads].sort((a, b) => {
    const ka = a.week ?? a.month
    const kb = b.week ?? b.month
    return ka.localeCompare(kb)
  })

  const periods = sorted.map(p => ({
    period: p.week ?? p.month,
    generated_at: p.generated_at,
    aggregated: p.aggregated,
  }))

  const seriesByConsultant = {}

  for (const p of sorted) {
    const label = p.week ?? p.month
    const leadIndex = view === 'monthly' && p.lead_reports
      ? Object.fromEntries(p.lead_reports.map(l => [l.id, l]))
      : {}

    for (const c of p.consultants) {
      if (!seriesByConsultant[c.id]) {
        seriesByConsultant[c.id] = { id: c.id, name: c.name, points: [] }
      }
      const point = {
        period: label,
        rag: c.rag,
        workload: c.workload,
      }
      if (view === 'monthly') {
        point.engagement = c.engagement
        point.motivation = c.motivation
        point.delivery = c.delivery
        point.skill_alignment = c.skill_alignment
        point.task_challenge = c.task_challenge
        const lead = leadIndex[c.id]
        if (lead) {
          point.reliability = lead.reliability
          point.proactivity = lead.proactivity
          point.skill_fit = lead.skill_fit
          point.project_status = lead.project_status
        }
      }
      seriesByConsultant[c.id].points.push(point)
    }
  }

  return { periods, seriesByConsultant }
}
