import { useState } from 'react'
import { Header } from './components/Header'
import { WeeklyView } from './components/WeeklyView'
import { MonthlyView } from './components/MonthlyView'
import { ErrorBoundary } from './components/ErrorBoundary'
import { usePulseData } from './hooks/usePulseData'
import { useIndex } from './hooks/useIndex'

function LoadingState() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="flex items-center gap-3">
        <div className="w-1 h-6 animate-pulse" style={{ background: 'var(--rag-green)' }} />
        <span className="font-condensed text-sm uppercase tracking-widest"
          style={{ color: 'var(--text-muted)', letterSpacing: '0.2em' }}>
          Loading
        </span>
      </div>
    </div>
  )
}

function ErrorState({ message }) {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="border px-6 py-4" style={{ borderColor: 'var(--rag-red-border)', background: 'var(--rag-red-bg)' }}>
        <div className="font-condensed text-xs uppercase tracking-widest mb-1"
          style={{ color: 'var(--rag-red)', letterSpacing: '0.15em' }}>
          Error
        </div>
        <div className="font-mono text-sm" style={{ color: 'var(--text-primary)' }}>
          {message}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [view, setView] = useState('weekly')
  const { index, loading: indexLoading, error: indexError } = useIndex()

  const files = index
    ? (view === 'weekly' ? index.weekly : index.monthly) ?? []
    : []
  const file = files[0] ?? null
  const prevFile = files[1] ?? null

  const { data, loading, error } = usePulseData(file)
  const { data: prevData } = usePulseData(prevFile)

  const period = data ? (data.week ?? data.month) : '—'
  const isLoading = indexLoading || loading
  const loadError = indexError ?? error

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'var(--bg-base)' }}>
      <Header
        period={period}
        generatedAt={data?.generated_at}
        view={view}
        onViewChange={setView}
      />

      <main className="flex-1">
        {isLoading && <LoadingState />}
        {!isLoading && loadError && <ErrorState message={loadError} />}
        {!isLoading && !loadError && data && (
          <ErrorBoundary key={view}>
            {view === 'weekly'
              ? <WeeklyView data={data} prevData={prevData} />
              : <MonthlyView data={data} prevData={prevData} />}
          </ErrorBoundary>
        )}
      </main>
    </div>
  )
}
