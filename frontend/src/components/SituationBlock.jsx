/**
 * Top-level summary — answers "Do I need to act?" in 5 seconds.
 * Plain language, no jargon. Action items only appear when there's something to do.
 */

const LEVEL_STYLES = {
  red:   { color: 'var(--rag-red)',   border: 'var(--rag-red-border)',   bg: 'var(--rag-red-bg)'   },
  amber: { color: 'var(--rag-amber)', border: 'var(--rag-amber-border)', bg: 'var(--rag-amber-bg)' },
}

function ActionItem({ level, text, ids }) {
  const s = LEVEL_STYLES[level]
  return (
    <div className="flex items-start gap-3 py-2 border-b last:border-b-0"
      style={{ borderColor: 'var(--border)' }}>
      <div className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" style={{ background: s.color }} />
      <div className="flex-1">
        <span className="font-sans text-sm" style={{ color: 'var(--text-primary)' }}>{text}</span>
        {ids.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {ids.map(label => (
              <span key={label} className="font-sans text-xs px-1.5 py-0.5 border"
                style={{ color: s.color, borderColor: s.border, background: s.bg }}>
                {label}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function TrendLine({ ragChanges, isMonthly }) {
  if (!ragChanges) return null
  const { worsened, improved } = ragChanges
  if (worsened === 0 && improved === 0) return (
    <div className="flex items-center gap-1 mt-2">
      <span className="font-condensed text-xs" style={{ color: 'var(--text-muted)' }}>
        No status changes vs. previous {isMonthly ? 'month' : 'week'}
      </span>
    </div>
  )
  return (
    <div className="flex items-center gap-3 mt-2">
      {worsened > 0 && (
        <span className="font-condensed text-xs" style={{ color: '#E53E3E' }}>
          ↓ {worsened} worsened
        </span>
      )}
      {improved > 0 && (
        <span className="font-condensed text-xs" style={{ color: '#16A34A' }}>
          ↑ {improved} improved
        </span>
      )}
      <span className="font-condensed text-xs" style={{ color: 'var(--text-muted)' }}>
        vs. previous {isMonthly ? 'month' : 'week'}
      </span>
    </div>
  )
}

export function SituationBlock({
  aggregated,
  nameMap = {},
  blockers = [],
  callsRequested = [],
  risks = [],
  missingConsultants = [],
  missingLeads = [],
  isMonthly = false,
  ragChanges = null,
}) {
  const resolve = (ids) => ids.map(id => nameMap[id] ?? id)
  const n = aggregated.expected_count

  const actions = [
    aggregated.rag_red > 0 && {
      level: 'red',
      text: `${aggregated.rag_red} of ${n} consultants flagged RED — immediate follow-up needed`,
      ids: [],
    },
    blockers.length > 0 && {
      level: 'red',
      text: `${blockers.length} active blocker${blockers.length > 1 ? 's' : ''}`,
      ids: resolve(blockers),
    },
    callsRequested.length > 0 && {
      level: 'amber',
      text: `${callsRequested.length} consultant${callsRequested.length > 1 ? 's' : ''} requested a call`,
      ids: resolve(callsRequested),
    },
    risks.length > 0 && {
      level: 'amber',
      text: `${risks.length} project risk${risks.length > 1 ? 's' : ''} reported by project leads`,
      ids: resolve(risks),
    },
    missingConsultants.length > 0 && {
      level: 'amber',
      text: `${missingConsultants.length} consultant${missingConsultants.length > 1 ? 's' : ''} did not submit this ${isMonthly ? 'month' : 'week'}`,
      ids: resolve(missingConsultants),
    },
    missingLeads.length > 0 && {
      level: 'amber',
      text: `${missingLeads.length} project lead report${missingLeads.length > 1 ? 's' : ''} still missing`,
      ids: resolve(missingLeads),
    },
  ].filter(Boolean)

  const allClear = actions.length === 0
  const responseOk = aggregated.response_count === aggregated.expected_count
  const leadResponseOk = !isMonthly || aggregated.lead_response_count === aggregated.expected_count

  return (
    <section className="px-6 py-5" style={{ borderBottom: '1px solid var(--border)', background: 'var(--bg-surface)' }}>
      <div className="flex items-start gap-8">

        {/* Left: overall status */}
        <div className="flex-shrink-0 min-w-[180px]">
          <div className="font-condensed text-xs uppercase tracking-widest mb-2"
            style={{ color: 'var(--text-muted)', letterSpacing: '0.2em' }}>
            Situation
          </div>
          {allClear ? (
            <div>
              <div className="font-condensed text-2xl" style={{ color: 'var(--rag-green)', fontWeight: 600 }}>
                All clear
              </div>
              <div className="font-sans text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                No action required
              </div>
            </div>
          ) : (
            <div>
              <div className="font-condensed text-2xl" style={{ color: 'var(--rag-red)', fontWeight: 600 }}>
                {actions.length} item{actions.length > 1 ? 's' : ''} to review
              </div>
              <div className="font-sans text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                Action required
              </div>
            </div>
          )}

          {/* Response status */}
          <div className="mt-4 flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full"
                style={{ background: responseOk ? 'var(--rag-green)' : 'var(--rag-amber)' }} />
              <span className="font-sans text-xs" style={{ color: 'var(--text-secondary)' }}>
                {aggregated.response_count}/{aggregated.expected_count} consultants submitted
              </span>
            </div>
            {isMonthly && (
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full"
                  style={{ background: leadResponseOk ? 'var(--rag-green)' : 'var(--rag-amber)' }} />
                <span className="font-sans text-xs" style={{ color: 'var(--text-secondary)' }}>
                  {aggregated.lead_response_count}/{aggregated.expected_count} project lead reports received
                </span>
              </div>
            )}
          </div>

          <TrendLine ragChanges={ragChanges} isMonthly={isMonthly} />
        </div>

        {/* Divider */}
        <div className="w-px self-stretch" style={{ background: 'var(--border)' }} />

        {/* Right: action items */}
        <div className="flex-1 min-w-0">
          {allClear ? (
            <div className="flex items-center gap-3 h-full py-2">
              <div className="font-sans text-sm" style={{ color: 'var(--text-muted)' }}>
                {aggregated.rag_green} consultants green · {aggregated.rag_amber} amber · avg workload {aggregated.avg_workload.toFixed(1)}/5
              </div>
            </div>
          ) : (
            <div>
              {actions.map((a, i) => (
                <ActionItem key={i} {...a} />
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
