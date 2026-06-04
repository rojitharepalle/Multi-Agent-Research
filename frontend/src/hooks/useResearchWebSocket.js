import { useCallback, useRef } from 'react'
import { useResearchStore } from '../store/researchStore'

const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export function useResearchWebSocket() {
  const wsRef = useRef(null)
  const { startSession, addEvent, setFinalAnswer, setError } = useResearchStore()

  const startResearch = useCallback((query) => {
    if (!query.trim()) return

    if (wsRef.current) wsRef.current.close()

    const sessionId = crypto.randomUUID()
    startSession(sessionId, query)

    const ws = new WebSocket(`${WS_BASE}/ws/research/${sessionId}`)
    wsRef.current = ws

    ws.onopen = () => ws.send(JSON.stringify({ query }))

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        switch (msg.type) {
          case 'session_start':
            break
          case 'agent_event':
            addEvent(msg.data)
            break
          case 'final':
            setFinalAnswer(msg.data.final_answer, msg.data.sources_used)
            ws.close()
            break
          case 'error':
            setError(msg.data.message)
            ws.close()
            break
        }
      } catch (err) {
        console.error('WebSocket parse error:', err)
      }
    }

    ws.onerror = () => setError('WebSocket connection failed. Is the backend running?')

    ws.onclose = (event) => {
      const store = useResearchStore.getState()
      if (event.code !== 1000 && event.code !== 1005 && store.status === 'running') {
        setError('Connection lost unexpectedly.')
      }
    }
  }, [startSession, addEvent, setFinalAnswer, setError])

  const cancel = useCallback(() => {
    if (wsRef.current) wsRef.current.close(1000, 'User cancelled')
  }, [])

  return { startResearch, cancel }
}
