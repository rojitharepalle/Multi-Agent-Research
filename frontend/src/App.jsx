import { SearchBar } from './components/SearchBar'
import { TracePanel } from './components/TracePanel'
import { AnswerPanel } from './components/AnswerPanel'
import { HistoryPanel } from './components/HistoryPanel'
import { useResearchStore } from './store/researchStore'
import { clsx } from 'clsx'

const TABS = [
  { id: 'trace', label: 'Agent Trace', icon: '⚡' },
  { id: 'answer', label: 'Answer', icon: '📄' },
  { id: 'history', label: 'History', icon: '🕐' },
]

function StatusBadge() {
  const { status, agentEvents } = useResearchStore()
  const toolCalls = agentEvents.filter(e => e.type === 'tool_call').length

  return (
    <div className="flex items-center gap-2 text-xs font-mono">
      {status === 'running' && (
        <>
          <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
          <span className="text-cyan-400">{toolCalls} tool calls</span>
        </>
      )}
      {status === 'completed' && (
        <>
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          <span className="text-emerald-400">complete</span>
        </>
      )}
      {status === 'error' && (
        <>
          <div className="w-1.5 h-1.5 rounded-full bg-red-400" />
          <span className="text-red-400">error</span>
        </>
      )}
    </div>
  )
}

export default function App() {
  const { activePanel, setActivePanel, status } = useResearchStore()

  return (
    <div className="min-h-screen bg-surface-0 flex flex-col">
      <header className="border-b border-white/7 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500/30 to-purple-500/30 border border-white/10 flex items-center justify-center text-sm">
              🤖
            </div>
            <div>
              <h1 className="text-sm font-display font-semibold text-white/90">
                Multi-Agent Research
              </h1>
              <p className="text-xs text-white/30 font-mono">
                Planner · Researcher · Writer
              </p>
            </div>
          </div>
          <StatusBadge />
        </div>
      </header>

      <main className="flex-1 flex flex-col max-w-6xl w-full mx-auto p-6 gap-4">
        <SearchBar />
        <div className="flex-1 glass rounded-xl overflow-hidden flex flex-col min-h-[500px]">
          <div className="flex border-b border-white/7">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActivePanel(tab.id)}
                className={clsx(
                  'flex items-center gap-2 px-5 py-3 text-xs font-mono transition-all border-b-2',
                  activePanel === tab.id
                    ? 'text-cyan-400 border-cyan-500/60 bg-cyan-500/5'
                    : 'text-white/30 border-transparent hover:text-white/60 hover:bg-white/3',
                )}
              >
                <span>{tab.icon}</span>
                <span>{tab.label.toUpperCase()}</span>
                {tab.id === 'trace' && status === 'running' && (
                  <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse ml-1" />
                )}
              </button>
            ))}
          </div>
          <div className="flex-1 flex flex-col overflow-hidden">
            {activePanel === 'trace' && <TracePanel />}
            {activePanel === 'answer' && <AnswerPanel />}
            {activePanel === 'history' && <HistoryPanel />}
          </div>
        </div>
      </main>

      <footer className="border-t border-white/5 px-6 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between text-xs text-white/20 font-mono">
          <span>LangGraph · FastAPI · WebSockets · React</span>
          <span>v1.0.0</span>
        </div>
      </footer>
    </div>
  )
}
