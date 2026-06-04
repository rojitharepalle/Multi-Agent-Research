import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useResearchStore } from '../store/researchStore'

export function AnswerPanel() {
  const { finalAnswer, sourcesUsed, status, query, error } = useResearchStore()

  if (status === 'idle') {
    return (
      <div className="flex-1 flex items-center justify-center text-white/20">
        <div className="text-center space-y-2">
          <div className="text-4xl">📄</div>
          <p className="text-sm font-mono">Final answer will appear here</p>
        </div>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="flex-1 p-6">
        <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-4">
          <p className="text-red-400 font-mono text-sm">Research failed</p>
          <p className="text-white/60 text-sm mt-1">{error}</p>
        </div>
      </div>
    )
  }

  if (!finalAnswer) return null

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="mb-6 pb-4 border-b border-white/7">
        <p className="text-xs text-white/30 font-mono mb-2">ANSWER FOR</p>
        <h2 className="text-base text-white/90 font-display font-medium">{query}</h2>
      </div>

      <div className="prose-dark">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {finalAnswer}
        </ReactMarkdown>
      </div>

      {sourcesUsed && sourcesUsed.length > 0 && (
        <div className="mt-8 pt-4 border-t border-white/7">
          <p className="text-xs text-white/30 font-mono mb-3">SOURCES USED</p>
          <div className="space-y-1">
            {sourcesUsed.map((source, i) => (
              <div key={i} className="flex items-start gap-2 text-xs text-white/40 font-mono">
                <span className="text-cyan-500/50">→</span>
                <span>{source}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
