import { useEffect, useRef } from 'react'
import { useResearchStore } from '../store/researchStore'
import { AgentEventCard, ThinkingIndicator } from './AgentEventCard'

export function TracePanel() {
  const { agentEvents, status, query } = useResearchStore()
  const bottomRef = useRef(null)
  const isRunning = status === 'running'

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [agentEvents.length])

  const lastAgent = agentEvents.length > 0
    ? agentEvents[agentEvents.length - 1].agent
    : 'planner'

  if (status === 'idle') {
    return (
      <div className="flex-1 flex items-center justify-center text-white/20">
        <div className="text-center space-y-2">
          <div className="text-4xl">🔬</div>
          <p className="text-sm font-mono">Agent trace will appear here</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2">
      {query && (
        <div className="rounded-lg bg-white/3 border border-white/7 p-3 mb-4">
          <p className="text-xs text-white/40 font-mono mb-1">RESEARCH QUERY</p>
          <p className="text-sm text-white/90">{query}</p>
        </div>
      )}
      {agentEvents.map((event, i) => (
        <AgentEventCard
          key={i}
          event={event}
          isLatest={i === agentEvents.length - 1 && isRunning}
        />
      ))}
      {isRunning && <ThinkingIndicator agent={lastAgent} />}
      <div ref={bottomRef} />
    </div>
  )
}
