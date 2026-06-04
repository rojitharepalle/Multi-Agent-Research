import { clsx } from 'clsx'

const AGENT_CONFIG = {
  planner: {
    label: 'Planner',
    color: 'text-purple-400',
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/20',
  },
  researcher: {
    label: 'Researcher',
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10',
    border: 'border-cyan-500/20',
  },
  writer: {
    label: 'Writer',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/20',
  },
}

const EVENT_ICONS = {
  agent_start: '▶',
  tool_call: '⚡',
  tool_result: '✓',
  agent_end: '●',
  error: '✗',
}

export function AgentEventCard({ event, isLatest }) {
  const config = AGENT_CONFIG[event.agent] || AGENT_CONFIG.researcher
  const icon = EVENT_ICONS[event.type] || '·'
  const isError = event.type === 'error'

  const time = new Date(event.timestamp).toLocaleTimeString('en-US', {
    hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit'
  })

  return (
    <div className={clsx(
      'animate-slide-up rounded-lg border p-3 text-sm transition-all',
      config.bg, config.border,
      isLatest && 'ring-1 ring-white/10',
    )}>
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-2">
          <span className={clsx('text-xs font-mono font-medium', config.color)}>
            {icon} {config.label.toUpperCase()}
          </span>
          {event.type === 'tool_call' && event.tool_name && (
            <span className="text-xs bg-white/5 text-white/50 px-2 py-0.5 rounded font-mono">
              {event.tool_name}
            </span>
          )}
        </div>
        <span className="text-xs text-white/20 font-mono">{time}</span>
      </div>

      <p className={clsx(
        'text-xs leading-relaxed',
        isError ? 'text-red-400' : 'text-white/70',
      )}>
        {event.content}
      </p>

      {event.type === 'tool_call' && event.tool_input && (
        <div className="mt-2 rounded bg-black/30 border border-white/5 p-2">
          <pre className="text-xs text-white/40 font-mono overflow-x-auto whitespace-pre-wrap">
            {JSON.stringify(event.tool_input, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

export function ThinkingIndicator({ agent = 'researcher' }) {
  const config = AGENT_CONFIG[agent] || AGENT_CONFIG.researcher
  return (
    <div className={clsx('rounded-lg border p-3 flex items-center gap-3', config.bg, config.border)}>
      <div className="flex gap-1">
        {[0, 1, 2].map(i => (
          <div
            key={i}
            className={clsx('thinking-dot', config.color.replace('text-', 'bg-'))}
            style={{ animationDelay: `${i * 0.2}s` }}
          />
        ))}
      </div>
      <span className={clsx('text-xs font-mono', config.color)}>
        {config.label} thinking...
      </span>
    </div>
  )
}
