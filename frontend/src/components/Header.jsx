export function Header({ period, generatedAt, view, onViewChange }) {
  const ts = generatedAt
    ? new Date(generatedAt).toLocaleString('de-DE', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit',
      })
    : null

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b"
      style={{ borderColor: 'var(--border)', background: 'var(--bg-surface)' }}>

      <div className="flex items-center gap-4">
        {/* Logo mark */}
        <div className="flex items-center gap-2">
          <div className="w-1 h-6" style={{ background: 'var(--rag-green)' }} />
          <span className="font-condensed font-700 tracking-widest text-xs uppercase"
            style={{ color: 'var(--text-secondary)', letterSpacing: '0.2em' }}>
            Consultant Pulse
          </span>
        </div>

        <div className="h-4 w-px" style={{ background: 'var(--border-bright)' }} />

        <span className="font-mono text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
          {period}
        </span>
      </div>

      <div className="flex items-center gap-4">
        {ts && (
          <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
            GEN {ts}
          </span>
        )}

        {/* View toggle */}
        <div className="flex border" style={{ borderColor: 'var(--border-bright)' }}>
          {['weekly', 'monthly'].map(v => (
            <button
              key={v}
              onClick={() => onViewChange(v)}
              className="px-3 py-1 text-xs font-condensed font-600 uppercase tracking-wider transition-colors"
              style={{
                letterSpacing: '0.12em',
                background: view === v ? 'var(--bg-elevated)' : 'transparent',
                color: view === v ? 'var(--text-primary)' : 'var(--text-muted)',
                borderRight: v === 'weekly' ? '1px solid var(--border-bright)' : 'none',
              }}
            >
              {v}
            </button>
          ))}
        </div>
      </div>
    </header>
  )
}
