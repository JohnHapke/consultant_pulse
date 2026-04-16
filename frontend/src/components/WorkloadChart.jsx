import { ragColors } from '../utils/rag'
import { scoreDelta, fmtDelta, deltaColor } from '../utils/delta'

export function WorkloadChart({ consultants, prevLookup }) {
  const sorted = [...consultants].sort((a, b) => b.workload - a.workload)

  return (
    <section className="p-6" style={{ borderBottom: '1px solid var(--border)' }}>
      <div className="flex items-center gap-3 mb-5">
        <span className="font-condensed text-xs uppercase tracking-widest"
          style={{ color: 'var(--text-muted)', letterSpacing: '0.2em', fontWeight: 600 }}>
          Workload Distribution
        </span>
        <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
        <span className="font-condensed text-xs" style={{ color: 'var(--text-muted)' }}>
          1 = low capacity · 5 = overloaded
        </span>
      </div>

      <div className="flex flex-col gap-1.5">
        {sorted.map((c, i) => {
          const colors = ragColors(c.rag)
          const pct = (c.workload / 5) * 100
          const prevWl = prevLookup?.[c.id]?.workload ?? null
          const delta = scoreDelta(c.workload, prevWl)
          const deltaStr = fmtDelta(delta)
          const dColor = deltaColor(delta, true) // inverted: higher workload = worse

          return (
            <div key={c.id} className="flex items-center gap-3 fade-up"
              style={{ animationDelay: `${i * 25}ms` }}>

              <div className="font-condensed text-xs w-24 text-right flex-shrink-0 truncate"
                style={{ color: colors.text, fontWeight: 600 }}>
                {c.name}
              </div>

              <div className="flex-1 h-5 relative" style={{ background: 'var(--bg-elevated)' }}>
                {[20, 40, 60, 80].map(p => (
                  <div key={p} className="absolute top-0 h-full w-px"
                    style={{ left: `${p}%`, background: 'var(--border)' }} />
                ))}
                <div
                  className="absolute top-0 left-0 h-full bar-fill"
                  style={{
                    width: `${pct}%`,
                    background: colors.text,
                    opacity: 0.75,
                    animationDelay: `${i * 25 + 100}ms`,
                  }}
                />
                <div className="absolute inset-0 flex items-center px-2">
                  <span className="font-mono text-xs"
                    style={{ color: pct > 30 ? 'var(--bg-base)' : colors.text, fontWeight: 600 }}>
                    {c.workload}
                  </span>
                </div>
              </div>

              {/* Delta */}
              <div className="w-8 text-right flex-shrink-0">
                {deltaStr && (
                  <span className="font-mono text-xs" style={{ color: dColor, fontWeight: 600 }}>
                    {deltaStr}
                  </span>
                )}
              </div>

              {/* Weekly flags only */}
              <div className="flex gap-1 w-16 flex-shrink-0">
                {c.blocker && (
                  <span className="font-condensed text-xs px-1"
                    style={{ background: 'var(--rag-red-border)', color: 'var(--rag-red)', fontWeight: 600 }}>
                    BLK
                  </span>
                )}
                {c.call_needed && (
                  <span className="font-condensed text-xs px-1"
                    style={{ background: 'var(--rag-amber-border)', color: 'var(--rag-amber)', fontWeight: 600 }}>
                    CALL
                  </span>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <div className="flex mt-2 ml-28">
        {[1, 2, 3, 4, 5].map(n => (
          <div key={n} className="flex-1 text-center font-mono text-xs"
            style={{ color: 'var(--text-muted)' }}>
            {n}
          </div>
        ))}
      </div>
    </section>
  )
}
