import { create } from 'zustand'

export const useResearchStore = create((set, get) => ({
  sessionId: null,
  query: '',
  status: 'idle',
  agentEvents: [],
  finalAnswer: null,
  sourcesUsed: [],
  error: null,
  sessions: [],
  activePanel: 'trace',

  setQuery: (query) => set({ query }),
  setActivePanel: (panel) => set({ activePanel: panel }),

  startSession: (sessionId, query) => set({
    sessionId,
    query,
    status: 'running',
    agentEvents: [],
    finalAnswer: null,
    sourcesUsed: [],
    error: null,
    activePanel: 'trace',
  }),

  addEvent: (event) => set((state) => ({
    agentEvents: [...state.agentEvents, event],
  })),

  setFinalAnswer: (answer, sources) => set((state) => ({
    finalAnswer: answer,
    sourcesUsed: sources || [],
    status: 'completed',
    activePanel: 'answer',
    sessions: [
      {
        id: state.sessionId,
        query: state.query,
        answer,
        timestamp: new Date().toISOString(),
        eventCount: state.agentEvents.length,
      },
      ...state.sessions.slice(0, 19),
    ],
  })),

  setError: (error) => set({ error, status: 'error' }),

  reset: () => set({
    sessionId: null,
    status: 'idle',
    agentEvents: [],
    finalAnswer: null,
    sourcesUsed: [],
    error: null,
  }),
}))
