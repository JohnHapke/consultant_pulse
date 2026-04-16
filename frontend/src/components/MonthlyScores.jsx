import { useState } from 'react'
import { scoreColor, fmtScore } from '../utils/rag'
import { scoreDelta, fmtDelta, deltaColor } from '../utils/delta'

const CONSULTANT_METRICS = [
  { key: 'avg_engagement',      label: 'Engagement',      inverted: false },
  { key: 'avg_motivation',      label: 'Motivation',      inverted: false },
  { key: 'avg_delivery',        label: 'Delivery quality', inverted: false },
  { key: 'avg_workload',        label: 'Workload',         inverted: true  },
  { key: 'avg_skill_alignment', label: 'Skill match',      inverted: false },
  { key: 'avg_task_challenge',  label: 'Task challenge',   inverted: false },
]

const LEAD_METRICS = [
  { key: 'avg_reliability',    label: 'Reliability',     inverted: false },
  { key: 'avg_proactivity',    label: 'Proactivity',     inverted: false },
  { key: 'avg_skill_fit',      label: 'Skill fit',       inverted: false },
  { key: 'avg_project_status', label: 'Project health',  inverted: false },
]

// Primary metrics shown by default
const PRIMARY_CONSULTANT = ['avg_engagement', 'avg_motivation', 'avg_delivery', 'avg_workload']
const PRIMARY_LEAD = ['avg_project_status', 'avg_reliability']

function ScoreBadge({ label, value, inverted, delta }) {
  const color = scoreColor(value, inverted)
  const isNull = value === null || value === undefined
  const deltaStr = fmtDelta(delta)
  const dColor = deltaColor(delta, inverted)

  return (
    <div className="flex flex-col gap-2 p-4 border"
      style={{
        borderColor: isNull ? 'var(--border)' : color + '44',
        background: isNull ? 'var(--bg-surface)' : color + '0D',
      }}>
      <div className="flex items-baseline gap-2">
        <div className="font-mono text-2xl tabular-nums leading-none"
          style={{ color: isNull ? 'var(--text-muted)' : color, fontWeight: 600 }}>
          {fmtScore(value)}
          {!isNull && <span className="text-sm ml-1" style={{ color: 'var(--text-muted)', fontWeight: 400 }}>/5</span>}
        </div>
        {deltaStr && (
          <span className="font-mono text-xs" style={{ color: dColor, fontWeight: 600 }}>
            {deltaStr}
          </span>
        )}
      </div>
      <div className="font-condensed text-xs uppercase tracking-wider"
        style={{ color: 'var(--text-secondary)', letterSpacing: '0.1em' }}>
        {label}
      </div>
    </div>
  )
}

function MetricGroup({ title, subtitle, metrics, aggregated, prevAggregated, showAll }) {
  const visible = showAll ? metrics : metrics.filter(m =>
    PRIMARY_CONSULTANT.includes(m.key) || PRIMARY_LEAD.includes(m.key)
  )

  return (
    <div>
      <div className="flex items-baseline gap-2 mb-3">
        <span className="font-condensed text-sm uppercase tracking-wider"
          style={{ color: 'var(--text-accent)', letterSpacing: '0.12em', fontWeight: 600 }}>
          {title}
        </span>
        {subtitle && (
          <span className="font-sans text-xs" style={{ color: 'var(--text-muted)' }}>
            {subtitle}
          </span>
        )}
      </div>
      <div className="grid gap-2" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))' }}>
        {visible.map(m => (
          <ScoreBadge
            key={m.key}
            label={m.label}
            value={aggregated[m.key]}
            inverted={m.inverted}
            delta={prevAggregated ? scoreDelta(aggregated[m.key], prevAggregated[m.key]) : null}
          />
        ))}
      </div>
    </div>
  )
}

export function MonthlyScores({ aggregated, prevAggregated }) {
  const [showAll, setShowAll] = useState(false)

  return (
    <section className="p-6" style={{ borderBottom: '1px solid var(--border)' }}>
      <div className="flex items-center gap-3 mb-5">
        <span className="font-condensed text-xs uppercase tracking-widest"
          style={{ color: 'var(--text-muted)', letterSpacing: '0.2em', fontWeight: 600 }}>
          Team Health
        </span>
        <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
        <button
          onClick={() => setShowAll(v => !v)}
          className="font-condensed text-xs uppercase tracking-wider px-2 py-1 border"
          style={{
            color: 'var(--text-secondary)',
            borderColor: 'var(--border-bright)',
            letterSpacing: '0.1em',
          }}>
          {showAll ? 'Show less' : 'Show all metrics'}
        </button>
      </div>

      <div className="flex flex-col gap-6">
        <MetricGroup
          title="Consultant perspective"
          subtitle="Self-reported monthly"
          metrics={CONSULTANT_METRICS}
          aggregated={aggregated}
          prevAggregated={prevAggregated}
          showAll={showAll}
        />

        <div className="h-px" style={{ background: 'var(--border)' }} />

        <MetricGroup
          title="Project lead perspective"
          subtitle={aggregated.lead_response_count != null
            ? `Based on ${aggregated.lead_response_count} reports`
            : 'No reports received'}
          metrics={LEAD_METRICS}
          aggregated={aggregated}
          prevAggregated={prevAggregated}
          showAll={showAll}
        />
      </div>
    </section>
  )
}
