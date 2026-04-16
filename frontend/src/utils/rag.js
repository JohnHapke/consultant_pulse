export const RAG_COLORS = {
  red:   { text: '#E53E3E', bg: '#1A0808', border: '#7F1D1D', label: 'RED' },
  amber: { text: '#D97706', bg: '#1A1000', border: '#78350F', label: 'AMB' },
  green: { text: '#16A34A', bg: '#071A0D', border: '#14532D', label: 'GRN' },
}

export function ragColors(status) {
  return RAG_COLORS[status] ?? RAG_COLORS.green
}

export function scoreColor(value, inverted = false) {
  if (value === null || value === undefined) return '#3E3E48'
  const v = inverted ? 6 - value : value
  if (v >= 4) return '#16A34A'
  if (v >= 3) return '#D97706'
  return '#E53E3E'
}

export function fmtScore(value) {
  if (value === null || value === undefined) return '—'
  return value.toFixed(1)
}
