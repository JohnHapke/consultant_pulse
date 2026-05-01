import { useState, useMemo } from 'react'
import { useHistory } from '../hooks/useHistory'
import { TrendSparkline } from './TrendSparkline'
import { ragColors } from '../utils/rag'

const WEEKLY_METRICS = [
  { key: 'workload', label: 'Workload', inverted: true, range: [1, 5] },
]

const MONTHLY_METRICS = [
  { key: 'workload',        label: 'Workload',        inverted: true,  range: [1, 5] },
  { key: 'engagement',      label: 'Engagement',      inverted: false, range: [1, 5] },
  { key: 'motivation',      label: 'Motivation',      inverted: false, range: [1, 5] },
  { key: 'delivery',        label: 'Delivery',        inverted: false, range: [1, 5] },
  { key: 'skill_alignment', label: 'Skill match',     inverted: false, range: [1, 5] },
  { key: 'task_challenge',  label: 'Task challenge',  inverted: false, range: [1, 5] },
]

const gridTemplate = (metrics) => `140px 80px ${metrics.map(() => '160px').join(' ')}`

function RagStrip({ series }) {
  if (!series || series.length === 0) return null
  return (
    <div className="flex gap-0.5 h-4">
      {series.map((p, i) => {
        const c = ragColors(p.rag)
        return (
          <span
            key={i}
            title={`${p.period}: ${p.rag}`}
            className="flex-1"
            style={{
              background: c.text,
              opacity: 0.85,
              minWidth: 6,
              border: `1px solid ${c.border}`,
            }}
          />
        )
      })}
    </div>
  )
}

function slopeDirection(points) {
  const values = points.map(p => p.value).filter(v => typeof v === 'number')
  if (values.length < 2) return null
  const first = values[0]
  const last = values[values.length - 1]
  if (last > first) return 'up'
  if (last < first) return 'down'
  return 'flat'
}

function TrendArrow({ direction, inverted }) {
  if (!direction || direction === 'flat') return (
    <span className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>=</span>
  )
  const worse = inverted ? direction === 'up' : direction === 'down'
  const color = worse ? 'var(--rag-red)' : 'var(--rag-green)'
  const symbol = direction === 'up' ? '↑' : '↓'
  return (
    <span className="font-mono text-xs font-700" style={{ color }}>{symbol}</span>
  )
}

function ConsultantRow({ series, metrics }) {
  const ragSeries = series.points.map(p => ({ period: p.period, rag: p.rag }))

  return (
    <div
      className="grid items-center gap-3 py-2 border-b"
      style={{
        borderColor: 'var(--border)',
        gridTemplateColumns: gridTemplate(metrics),
      }}
    >
      <span className="font-condensed text-sm truncate" style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
        {series.name}
      </span>

      <div className="flex items-center">
        <RagStrip series={ragSeries} />
      </div>

      {metrics.map(m => {
        const sparkPoints = series.points.map(p => ({
          period: p.period,
          value: p[m.key],
        }))
        const numeric = sparkPoints.filter(p => typeof p.value === 'number')
        const dir = slopeDirection(numeric)
        return (
          <div key={m.key} className="flex items-center gap-2 min-w-0">
            <TrendSparkline
              points={sparkPoints}
              width={120}
              height={28}
              fixedRange={m.range}
              inverted={m.inverted}
            />
            <TrendArrow direction={dir} inverted={m.inverted} />
          </div>
        )
      })}
    </div>
  )
}

function AggregatedRow({ periods, view }) {
  const counts = periods.map(p => ({
    period: p.period,
    red: p.aggregated.rag_red,
    amber: p.aggregated.rag_amber,
    green: p.aggregated.rag_green,
  }))
  return (
    <div className="mb-6 p-4 border" style={{ borderColor: 'var(--border)', background: 'var(--bg-surface)' }}>
      <div className="font-condensed text-xs uppercase tracking-widest mb-3"
        style={{ color: 'var(--text-muted)', letterSpacing: '0.2em' }}>
        Team health over time — {periods.length} {view === 'weekly' ? 'weeks' : 'months'}
      </div>
      <div className="flex gap-1 h-12">
        {counts.map((c, i) => {
          const total = (c.red + c.amber + c.green) || 1
          const redPct = (c.red / total) * 100
          const amberPct = (c.amber / total) * 100
          const greenPct = (c.green / total) * 100
          return (
            <div key={i} className="flex-1 flex flex-col" title={`${c.period}: ${c.red}R ${c.amber}A ${c.green}G`}>
              <div style={{ flex: redPct, background: 'var(--rag-red)' }} />
              <div style={{ flex: amberPct, background: 'var(--rag-amber)' }} />
              <div style={{ flex: greenPct, background: 'var(--rag-green)' }} />
            </div>
          )
        })}
      </div>
      <div className="flex justify-between mt-2">
        {counts.map((c, i) => (
          <span key={i} className="font-mono text-xs" style={{ color: 'var(--text-muted)', flex: 1, textAlign: 'center' }}>
            {c.period.replace(/^\d{4}-/, '')}
          </span>
        ))}
      </div>
    </div>
  )
}

export function HistoryView({ index }) {
  const [granularity, setGranularity] = useState('weekly')
  const files = granularity === 'weekly' ? index?.weekly ?? [] : index?.monthly ?? []

  const { loading, error, data } = useHistory(files, granularity)

  const metrics = granularity === 'weekly' ? WEEKLY_METRICS : MONTHLY_METRICS

  const sortedSeries = useMemo(() => {
    if (!data) return []
    const latestRagOrder = { red: 0, amber: 1, green: 2 }
    return Object.values(data.seriesByConsultant).sort((a, b) => {
      const ar = latestRagOrder[a.points.at(-1)?.rag] ?? 99
      const br = latestRagOrder[b.points.at(-1)?.rag] ?? 99
      return ar - br
    })
  }, [data])

  return (
    <div className="p-6">
      <div className="flex items-center gap-4 mb-6">
        <span className="font-condensed text-xs uppercase tracking-widest"
          style={{ color: 'var(--text-muted)', letterSpacing: '0.2em', fontWeight: 600 }}>
          Trend granularity
        </span>
        <div className="flex border" style={{ borderColor: 'var(--border-bright)' }}>
          {['weekly', 'monthly'].map(g => (
            <button
              key={g}
              onClick={() => setGranularity(g)}
              className="px-3 py-1 text-xs font-condensed font-600 uppercase tracking-wider"
              style={{
                letterSpacing: '0.12em',
                background: granularity === g ? 'var(--bg-elevated)' : 'transparent',
                color: granularity === g ? 'var(--text-primary)' : 'var(--text-muted)',
                borderRight: g === 'weekly' ? '1px solid var(--border-bright)' : 'none',
              }}
            >
              {g}
            </button>
          ))}
        </div>
        <div className="flex-1 h-px" style={{ background: 'var(--border)' }} />
        <span className="font-sans text-xs" style={{ color: 'var(--text-muted)' }}>
          RAG strip shows status per period · sparklines colored by value
        </span>
      </div>

      {loading && (
        <div className="font-condensed text-sm" style={{ color: 'var(--text-muted)' }}>
          Loading history…
        </div>
      )}

      {error && (
        <div className="border px-4 py-3" style={{ borderColor: 'var(--rag-red-border)', background: 'var(--rag-red-bg)' }}>
          <span className="font-mono text-sm" style={{ color: 'var(--rag-red)' }}>
            Error loading history: {error}
          </span>
        </div>
      )}

      {data && data.periods.length === 0 && (
        <div className="font-sans text-sm" style={{ color: 'var(--text-muted)' }}>
          No historical data available.
        </div>
      )}

      {data && data.periods.length > 0 && (
        <>
          <AggregatedRow periods={data.periods} view={granularity} />

          <div className="border" style={{ borderColor: 'var(--border)', background: 'var(--bg-surface)' }}>
            <div
              className="grid items-center gap-3 px-4 py-2 border-b"
              style={{
                borderColor: 'var(--border)',
                background: 'var(--bg-elevated)',
                gridTemplateColumns: gridTemplate(metrics),
              }}
            >
              <span className="font-condensed text-xs uppercase tracking-widest"
                style={{ color: 'var(--text-muted)', letterSpacing: '0.15em' }}>
                Consultant
              </span>
              <span className="font-condensed text-xs uppercase tracking-widest"
                style={{ color: 'var(--text-muted)', letterSpacing: '0.15em' }}>
                RAG
              </span>
              {metrics.map(m => (
                <span key={m.key} className="font-condensed text-xs uppercase tracking-widest"
                  style={{ color: 'var(--text-muted)', letterSpacing: '0.15em' }}>
                  {m.label}
                </span>
              ))}
            </div>

            <div className="px-4">
              {sortedSeries.map((s, i) => (
                <div key={s.id} className="fade-up" style={{ animationDelay: `${i * 20}ms` }}>
                  <ConsultantRow series={s} metrics={metrics} />
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
