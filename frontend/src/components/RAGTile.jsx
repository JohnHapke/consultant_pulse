import { ragColors, RAG_COLORS } from '../utils/rag'
import { ragTrend } from '../utils/delta'

const TREND_ARROW = {
  worsened: { symbol: '↓', color: RAG_COLORS.red.text },
  improved:  { symbol: '↑', color: RAG_COLORS.green.text },
}

export function RAGTile({ consultant, index, prevRag }) {
  const { name, workload, blocker, call_needed, rag } = consultant
  const firstName = name.split(' ')[0]
  const colors = ragColors(rag)
  const isRed = rag === 'red'
  const trend = prevRag ? ragTrend(rag, prevRag) : null
  const arrow = trend && trend !== 'same' ? TREND_ARROW[trend] : null

  return (
    <div
      className={`relative flex flex-col p-3 border cursor-default tile-animate ${isRed ? 'rag-pulse' : ''}`}
      style={{
        animationDelay: `${index * 30}ms`,
        background: colors.bg,
        borderColor: colors.border,
        borderLeftWidth: '3px',
        borderLeftColor: colors.text,
      }}
    >
      {/* Trend arrow — top-right corner */}
      {arrow && (
        <span className="absolute top-1.5 right-2 font-condensed text-xs font-700"
          style={{ color: arrow.color, lineHeight: 1 }}>
          {arrow.symbol}
        </span>
      )}

      {/* Name */}
      <div className="font-condensed text-sm font-600 leading-none truncate" style={{ color: colors.text }}>
        {firstName}
      </div>

      {/* Status label */}
      <div className="font-condensed text-xs font-700 mt-1 uppercase tracking-wider"
        style={{ color: colors.text, letterSpacing: '0.12em', opacity: 0.85 }}>
        {colors.label}
      </div>

      {/* Workload */}
      <div className="flex items-baseline gap-0.5 mt-2">
        <span className="font-mono text-sm font-600" style={{ color: 'var(--text-accent)' }}>
          {workload}
        </span>
        <span className="font-condensed text-xs" style={{ color: 'var(--text-muted)' }}>/5</span>
      </div>

      {/* Flags */}
      <div className="flex gap-1 mt-2">
        {blocker && (
          <span className="font-condensed text-xs px-1 font-600 uppercase"
            style={{ background: 'var(--rag-red-border)', color: 'var(--rag-red)', letterSpacing: '0.06em' }}>
            BLK
          </span>
        )}
        {call_needed && (
          <span className="font-condensed text-xs px-1 font-600 uppercase"
            style={{ background: 'var(--rag-amber-border)', color: 'var(--rag-amber)', letterSpacing: '0.06em' }}>
            CALL
          </span>
        )}
      </div>
    </div>
  )
}
