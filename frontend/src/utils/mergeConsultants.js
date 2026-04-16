/**
 * Merges monthly consultant self-assessments with PL lead reports by ID.
 * Returns one object per consultant with lead data embedded (or null if absent).
 */
export function mergeConsultants(consultants, leadReports) {
  const leadIndex = Object.fromEntries(leadReports.map(l => [l.id, l]))
  return consultants.map(c => ({
    ...c,
    lead: leadIndex[c.id] ?? null,
  }))
}
