import { useState } from 'react'
import { useResearchStore } from '../store/researchStore'
import { useResearchWebSocket } from '../hooks/useResearchWebSocket'
import { clsx } from 'clsx'

const EXAMPLES = [
  'What are the latest developments in LangGraph?',
  'Explain quantum computing and its applications',
  'What is CRISPR and recent breakthroughs?',
]

export function SearchBar() {
  const { query, status, setQuery } = useResearchStore()
  const { startResearch, cancel } = useResearchWebSocket()
  const [focused, setFocused] = useState(false)
  const isRunning = status === 'running'

  const handleSubmit = (e) => {
    e.preventDefault()
    if (isRunning) cancel()
    else if (query.trim()) startResearch(query.trim())
  }

  return (
    <div className="w-full space-y-3">
      <form onSubmit={handleSubmit}>
        <div className={clsx(
          'flex items-center gap-2 rounded-xl border p-3 transition-all duration-200 bg-surface-2',
          focused ? 'border-cyan-500/40 shadow-[0_0_0_3px_rgba(0,212,255,0.06)]' : 'border-white/7',
        )}>
          <div className="text-white/30 pl-1 flex-shrink-0">
            {isRunning
              ? <div className="w-4 h-4 rounded-full border-2 border-cyan-500/60 border-t-transparent animate-spin" />
              : <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
            }
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Ask anything — agents will research it for you"
            className="flex-1 bg-transparent text-sm text-white/90 placeholder-white/25 outline-none"
            disabled={isRunning}
          />
          <button
            type="submit"
            disabled={!isRunning && !query.trim()}
            className={clsx(
              'flex-shrink-0 px-4 py-1.5 rounded-lg text-xs font-mono font-medium transition-all',
              isRunning
                ? 'bg-red-500/20 text-red-400 border border-red-500/20 hover:bg-red-500/30'
                : query.trim()
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/20 hover:bg-cyan-500/30'
                  : 'bg-white/5 text-white/20 border border-white/5 cursor-not-allowed',
            )}
          >
            {isRunning ? 'STOP' : 'RUN →'}
          </button>
        </div>
      </form>

      {status === 'idle' && (
        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((q, i) => (
            <button
              key={i}
              onClick={() => setQuery(q)}
              className="text-xs text-white/30 hover:text-white/60 bg-white/3 hover:bg-white/5 border border-white/5 px-3 py-1.5 rounded-full transition-all"
            >
              {q.length > 55 ? q.slice(0, 55) + '...' : q}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
