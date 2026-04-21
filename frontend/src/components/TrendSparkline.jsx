import { useState } from 'react'
import { scoreColor, ragColors } from '../utils/rag'

/**
 * Inline SVG sparkline for a series of numeric points.
 *
 * points: [{ period, value, rag? }]
 * - Renders a polyline through the values, one dot per point.
 * - If rag provided, dot is colored by rag; otherwise by scoreColor.
 * - Hover reveals period + value as a small tooltip.
 *
 * fixedRange: [min, max] — when set, y-axis uses this range (e.g. [1, 5] for scores).
 * inverted: when true, higher values are worse (used for score color).
 */
export function TrendSparkline({
  points,
  width = 140,
  height = 32,
  fixedRange = null,
  inverted = false,
  strokeColor = 'var(--text-secondary)',
}) {
  const [hover, setHover] = useState(null)

  const valid = points.filter(p => typeof p.value === 'number')
  if (valid.length === 0) {
    return (
      <span className="font-condensed text-xs" style={{ color: 'var(--text-muted)' }}>
        no data
      </span>
    )
  }
  if (valid.length === 1) {
    return (
      <span className="font-condensed text-xs" style={{ color: 'var(--text-muted)' }}>
        {valid[0].period} · {valid[0].value} (single point)
      </span>
    )
  }

  const values = valid.map(p => p.value)
  const [minV, maxV] = fixedRange ?? [Math.min(...values), Math.max(...values)]
  const rawRange = maxV - minV

  const pad = 4
  const innerW = width - pad * 2
  const innerH = height - pad * 2

  const x = (i) => pad + (i / Math.max(valid.length - 1, 1)) * innerW
  const y = (v) => rawRange > 0
    ? pad + innerH - ((v - minV) / rawRange) * innerH
    : pad + innerH / 2

  const pathD = valid.map((p, i) => `${i === 0 ? 'M' : 'L'}${x(i).toFixed(1)},${y(p.value).toFixed(1)}`).join(' ')

  return (
    <div className="relative inline-block" style={{ width, height: height + 16 }}>
      <svg width={width} height={height} style={{ display: 'block' }}>
        <path d={pathD} fill="none" stroke={strokeColor} strokeWidth="1.2" opacity="0.5" />
        {valid.map((p, i) => {
          const color = p.rag
            ? ragColors(p.rag).text
            : scoreColor(p.value, inverted)
          const cx = x(i)
          const cy = y(p.value)
          return (
            <g key={i}>
              <circle cx={cx} cy={cy} r="2.5" fill={color} />
              <circle
                cx={cx} cy={cy} r="8"
                fill="transparent"
                onMouseEnter={() => setHover({ i, x: cx, y: cy, point: p })}
                onMouseLeave={() => setHover(null)}
                style={{ cursor: 'pointer' }}
              />
            </g>
          )
        })}
      </svg>
      {hover && (
        <div
          className="absolute font-mono text-xs px-1.5 py-0.5 pointer-events-none whitespace-nowrap"
          style={{
            left: Math.min(Math.max(hover.x - 40, 0), width - 80),
            top: height,
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-bright)',
            color: 'var(--text-primary)',
            zIndex: 10,
          }}
        >
          {hover.point.period} · {hover.point.value}
        </div>
      )}
    </div>
  )
}
