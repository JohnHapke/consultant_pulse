import { Component } from 'react'

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  render() {
    if (this.state.error) {
      return (
        <div className="p-8">
          <div className="border px-6 py-5" style={{ borderColor: 'var(--rag-red-border)', background: 'var(--rag-red-bg)' }}>
            <div className="font-condensed text-xs uppercase tracking-widest mb-2"
              style={{ color: 'var(--rag-red)', letterSpacing: '0.15em' }}>
              Render Error
            </div>
            <div className="font-mono text-sm" style={{ color: 'var(--text-primary)' }}>
              {this.state.error.message}
            </div>
            <pre className="font-mono text-xs mt-3 opacity-60" style={{ color: 'var(--text-secondary)' }}>
              {this.state.error.stack?.split('\n').slice(0, 5).join('\n')}
            </pre>
            <button
              className="mt-4 font-condensed text-xs uppercase tracking-widest px-3 py-1 border"
              style={{ borderColor: 'var(--rag-red-border)', color: 'var(--rag-red)' }}
              onClick={() => this.setState({ error: null })}
            >
              Retry
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
