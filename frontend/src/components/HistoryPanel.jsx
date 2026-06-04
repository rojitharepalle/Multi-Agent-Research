import { useResearchStore } from '../store/researchStore'
import { clsx } from 'clsx'

export function HistoryPanel() {
  const { sessions, setQuery, setActivePanel } = useResearchStore()

  if (sessions.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-white/20">
        <div className="text-center space-y-2">
          <div className="text-4xl">🕐</div>
          <p className="text-sm font-mono">No sessions yet</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2">
      <p className="text-xs text-white/30 font-mono px-1 mb-3">
        {sessions.length} SESSION{sessions.length !== 1 ? 'S' : ''}
      </p>
      {sessions.map((session) => (
        <button
          key={session.id}
          onClick={() => { setQuery(session.query); setActivePanel('answer') }}
          className={clsx(
            'w-full text-left rounded-lg border p-3 transition-all',
            'bg-white/2 border-white/7 hover:bg-white/5 hover:border-white/12',
          )}
        >
          <p className="text-sm text-white/80 line-clamp-2 mb-2">{session.query}</p>
          <div className="flex items-center justify-between text-xs text-white/30 font-mono">
            <span>{session.eventCount} events</span>
            <span>{new Date(session.timestamp).toLocaleTimeString()}</span>
          </div>
        </button>
      ))}
    </div>
  )
}
