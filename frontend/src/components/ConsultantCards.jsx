import { useState } from 'react'
import { ragColors, scoreColor, RAG_COLORS } from '../utils/rag'
import { ragTrend, scoreDelta, fmtDelta, deltaColor } from '../utils/delta'

const SELF_FIELDS = [
  { key: 'engagement',      label: 'Engagement',     inverted: false },
  { key: 'motivation',      label: 'Motivation',      inverted: false },
  { key: 'delivery',        label: 'Delivery quality', inverted: false },
  { key: 'skill_alignment', label: 'Skill match',     inverted: false },
  { key: 'task_challenge',  label: 'Task challenge',  inverted: false },
  { key: 'workload',        label: 'Workload',         inverted: true  },
]

const LEAD_FIELDS = [
  { key: 'reliability',    label: 'Reliability',    inverted: false },
  { key: 'proactivity',    label: 'Proactivity',    inverted: false },
  { key: 'skill_fit',      label: 'Skill fit',       inverted: false },
  { key: 'project_status', label: 'Project health',  inverted: false },
]

function ScoreBar({ label, value, inverted, delta }) {
  const color = scoreColor(value, inverted)
  const pct = ((value - 1) / 4) * 100
  const deltaStr = fmtDelta(delta)
  const dColor = deltaColor(delta, inverted)
  return (
    <div className="flex items-center gap-3">
      <span className="font-sans text-xs w-28 flex-shrink-0" style={{ color: 'var(--text-secondary)' }}>
        {label}
      </span>
      <div className="flex-1 h-1.5 relative" style={{ background: 'var(--bg-base)' }}>
        <div className="absolute top-0 left-0 h-full" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="font-mono text-xs w-4 text-right flex-shrink-0" style={{ color, fontWeight: 600 }}>
        {value}
      </span>
      <span className="font-mono text-xs w-8 text-right flex-shrink-0" style={{ color: dColor, fontWeight: 600 }}>
        {deltaStr ?? ''}
      </span>
    </div>
  )
}

function StatusPill({ rag }) {
  const colors = ragColors(rag)
  const label = { red: 'Red', amber: 'Amber', green: 'Green' }[rag]
  return (
    <span className="font-condensed text-xs px-2 py-0.5 uppercase tracking-wider"
      style={{
        color: colors.text,
        background: colors.bg,
        border: `1px solid ${colors.border}`,
        letterSpacing: '0.1em',
        fontWeight: 600,
      }}>
      {label}
    </span>
  )
}

const TREND_BADGE = {
  worsened: { symbol: '↓', color: RAG_COLORS.red.text,   label: 'worsened' },
  improved:  { symbol: '↑', color: RAG_COLORS.green.text, label: 'improved' },
}

function ConsultantCard({ consultant, prevConsultant }) {
  const [open, setOpen] = useState(false)
  const { rag, workload, lead } = consultant
  const colors = ragColors(rag)
  const wlColor = scoreColor(workload, true)
  const trend = prevConsultant ? ragTrend(rag, prevConsultant.rag) : null
  const trendBadge = trend && trend !== 'same' ? TREND_BADGE[trend] : null

  return (
    <div className="border" style={{
      borderColor: open ? colors.border : 'var(--border)',
      background: 'var(--bg-surface)',
      borderLeftWidth: '3px',
      borderLeftColor: colors.text,
    }}>
      <button className="w-full flex items-center gap-4 px-4 py-3 text-left"
        onClick={() => setOpen(o => !o)}>

        <span className="font-condensed text-sm flex-shrink-0" style={{ color: colors.text, fontWeight: 600, minWidth: 120 }}>
          {consultant.name}
        </span>

        <StatusPill rag={rag} />

        {trendBadge && (
          <span className="font-condensed text-xs flex-shrink-0" style={{ color: trendBadge.color, fontWeight: 700 }}>
            {trendBadge.symbol} {trendBadge.label}
          </span>
        )}

        <div className="flex items-baseline gap-1 flex-shrink-0">
          <span className="font-condensed text-xs" style={{ color: 'var(--text-muted)' }}>WL</span>
          <span className="font-mono text-sm" style={{ color: wlColor, fontWeight: 600 }}>{workload}</span>
          <span className="font-condensed text-xs" style={{ color: 'var(--text-muted)' }}>/5</span>
        </div>

        <div className="flex items-center gap-3 flex-1 min-w-0">
          {SELF_FIELDS.filter(f => f.key !== 'workload').slice(0, 3).map(f => {
            const v = consultant[f.key]
            const c = scoreColor(v, f.inverted)
            return (
              <div key={f.key} className="flex items-baseline gap-1">
                <span className="font-condensed text-xs" style={{ color: 'var(--text-muted)' }}>
                  {f.label.split(' ')[0]}
                </span>
                <span className="font-mono text-xs" style={{ color: c, fontWeight: 600 }}>{v}</span>
              </div>
            )
          })}
        </div>

        {lead ? (
          <div className="flex items-center gap-1 flex-shrink-0">
            <span className="font-condensed text-xs" style={{ color: 'var(--text-muted)' }}>PL</span>
            <span className="font-mono text-xs"
              style={{ color: scoreColor(lead.project_status, false), fontWeight: 600 }}>
              {lead.project_status}
            </span>
            {lead.risks_present && (
              <span className="font-condensed text-xs px-1 ml-1"
                style={{ color: 'var(--rag-red)', background: 'var(--rag-red-bg)',
                  border: '1px solid var(--rag-red-border)' }}>
                Risk
              </span>
            )}
          </div>
        ) : (
          <span className="font-condensed text-xs flex-shrink-0" style={{ color: 'var(--rag-amber)' }}>
            No PL report
          </span>
        )}

        <span className="font-mono text-xs flex-shrink-0" style={{ color: 'var(--text-muted)' }}>
          {open ? '▲' : '▼'}
        </span>
      </button>

      {open && (
        <div className="px-4 pb-4 grid grid-cols-2 gap-8 border-t" style={{ borderColor: 'var(--border)' }}>
          <div className="pt-4">
            <div className="font-condensed text-xs uppercase tracking-widest mb-3"
              style={{ color: 'var(--text-muted)', letterSpacing: '0.15em' }}>
              Consultant perspective
            </div>
            <div className="flex flex-col gap-2.5">
              {SELF_FIELDS.map(f => (
                <ScoreBar key={f.key} label={f.label} value={consultant[f.key]} inverted={f.inverted}
                  delta={prevConsultant ? scoreDelta(consultant[f.key], prevConsultant[f.key]) : null} />
              ))}
            </div>
            {consultant.manager_needs && (
              <div className="mt-3">
                <div className="font-condensed text-xs uppercase tracking-wider mb-1"
                  style={{ color: 'var(--text-muted)', letterSpacing: '0.1em' }}>
                  Needs from manager
                </div>
                <p className="font-sans text-sm italic leading-snug"
                  style={{ color: 'var(--text-secondary)' }}>
                  "{consultant.manager_needs}"
                </p>
              </div>
            )}
          </div>

          <div className="pt-4">
            <div className="font-condensed text-xs uppercase tracking-widest mb-3"
              style={{ color: 'var(--text-muted)', letterSpacing: '0.15em' }}>
              Project lead perspective
            </div>
            {lead ? (
              <div className="flex flex-col gap-2.5">
                {LEAD_FIELDS.map(f => (
                  <ScoreBar key={f.key} label={f.label} value={lead[f.key]} inverted={f.inverted}
                    delta={prevConsultant?.lead ? scoreDelta(lead[f.key], prevConsultant.lead[f.key]) : null} />
                ))}
                {lead.risks_present && (
                  <div className="mt-2 px-3 py-2"
                    style={{ background: 'var(--rag-red-bg)',
                      border: '1px solid var(--rag-red-border)' }}>
                    <div className="font-condensed text-xs uppercase tracking-wider mb-1"
                      style={{ color: 'var(--rag-red)', letterSpacing: '0.1em', fontWeight: 600 }}>
                      Active risks
                    </div>
                    {lead.risks_text ? (
                      <p className="font-sans text-sm italic leading-snug"
                        style={{ color: 'var(--text-primary)' }}>
                        "{lead.risks_text}"
                      </p>
                    ) : (
                      <p className="font-sans text-xs"
                        style={{ color: 'var(--rag-red)' }}>
                        Project lead flagged risks (no details provided)
                      </p>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <p className="font-sans text-sm" style={{ color: 'var(--text-muted)' }}>
                No report submitted this month
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export function ConsultantCards({ consultants, prevLookup }) {
  const sorted = [...consultants].sort((a, b) => {
    const order = { red: 0, amber: 1, green: 2 }
    return order[a.rag] - order[b.rag]
  })

  return (
    <section className="p-6">
      <div className="flex items-center gap-3 mb-4">
        <span className="font-condensed text-xs uppercase tracking-widest"
          style={{ color: 'var(--text-muted)', letterSpacing: '0.2em', fontWeight: 600 }}>
          Individual view
        </span>
        <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
        <span className="font-sans text-xs" style={{ color: 'var(--text-muted)' }}>
          Click a row to expand · WL = Workload · PL = Project lead score
        </span>
      </div>
      <div className="flex flex-col gap-1">
        {sorted.map((c, i) => (
          <div key={c.id} className="fade-up" style={{ animationDelay: `${i * 25}ms` }}>
            <ConsultantCard consultant={c} prevConsultant={prevLookup?.[c.id] ?? null} />
          </div>
        ))}
      </div>
    </section>
  )
}
