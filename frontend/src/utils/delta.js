/**
 * Delta utilities for trend comparison between periods.
 */

const RAG_ORDER = { red: 0, amber: 1, green: 2 }

/** Build id → item lookup from array of {id, ...} objects. */
export function buildLookup(items) {
  return Object.fromEntries((items ?? []).map(c => [c.id, c]))
}

/** 'improved' | 'worsened' | 'same' — null when no prev data. */
export function ragTrend(current, prev) {
  if (!prev || prev === current) return 'same'
  return RAG_ORDER[current] > RAG_ORDER[prev] ? 'improved' : 'worsened'
}

/** Current minus previous, rounded to 1 decimal. Null when prev missing. */
export function scoreDelta(current, prev) {
  if (current == null || prev == null) return null
  return Math.round((current - prev) * 10) / 10
}

/** '+0.4' | '-0.3' | '=' | null (when no prev). */
export function fmtDelta(delta) {
  if (delta === null || delta === undefined) return null
  if (delta === 0) return '='
  const sign = delta > 0 ? '+' : ''
  return Number.isInteger(delta) ? `${sign}${delta}` : `${sign}${delta.toFixed(1)}`
}

/**
 * Color for a delta value.
 * inverted=true means higher is worse (workload).
 */
export function deltaColor(delta, inverted = false) {
  if (delta === null || delta === undefined || delta === 0) return '#3E3E48'
  const better = inverted ? delta < 0 : delta > 0
  return better ? '#16A34A' : '#E53E3E'
}

/** Count RAG status changes across consultants vs. previous period. */
export function computeRagChanges(consultants, prevLookup) {
  if (!prevLookup) return null
  let worsened = 0, improved = 0
  for (const c of consultants) {
    const prev = prevLookup[c.id]
    if (!prev) continue
    const trend = ragTrend(c.rag, prev.rag)
    if (trend === 'worsened') worsened++
    if (trend === 'improved') improved++
  }
  return { worsened, improved }
}
