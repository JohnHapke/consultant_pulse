import { RAGTile } from './RAGTile'

export function RAGGrid({ consultants, prevLookup }) {
  const sorted = [...consultants].sort((a, b) => {
    const order = { red: 0, amber: 1, green: 2 }
    return order[a.rag] - order[b.rag]
  })

  return (
    <section className="p-6" style={{ borderBottom: '1px solid var(--border)' }}>
      <div className="flex items-center gap-3 mb-4">
        <span className="font-condensed text-xs uppercase tracking-widest font-600"
          style={{ color: 'var(--text-muted)', letterSpacing: '0.2em' }}>
          Consultant Status
        </span>
        <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
        <span className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
          {consultants.length} consultants
        </span>
      </div>

      <div className="grid gap-2" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(96px, 1fr))' }}>
        {sorted.map((c, i) => (
          <RAGTile key={c.id} consultant={c} index={i}
            prevRag={prevLookup?.[c.id]?.rag ?? null} />
        ))}
      </div>
    </section>
  )
}
