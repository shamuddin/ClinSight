import { useState, useCallback, useRef } from 'react'
import { CaseResult, AgentId, AgentNodeState, PipelineAgents } from '../types'

// Which display-agent IDs each LangGraph node maps to
const NODE_TO_AGENTS: Record<string, AgentId[]> = {
  coordinator: ['coordinator'],
  analysis:    ['radiologist', 'lab_analyst'],
  safety:      ['safety'],
  documenter:  ['documenter'],
  reject:      ['coordinator'],
}

// Which agent should be set to 'running' after each node completes
const NEXT_RUNNING: Record<string, AgentId | null> = {
  coordinator: 'radiologist',
  analysis:    'safety',
  safety:      'documenter',
  documenter:  null,
  reject:      null,
}

const INITIAL_AGENTS: PipelineAgents = {
  coordinator: { status: 'pending' },
  radiologist: { status: 'pending' },
  lab_analyst: { status: 'pending' },
  safety:      { status: 'pending' },
  documenter:  { status: 'pending' },
}

export interface PipelineStreamState {
  agents:    PipelineAgents
  result:    CaseResult | null
  error:     string
  streaming: boolean
}

export function usePipelineStream(apiBase: string) {
  const [state, setState] = useState<PipelineStreamState>({
    agents:    INITIAL_AGENTS,
    result:    null,
    error:     '',
    streaming: false,
  })

  const esRef = useRef<EventSource | null>(null)

  const startStream = useCallback((caseId: string) => {
    // Tear down any existing stream
    esRef.current?.close()

    // Optimistic: coordinator starts immediately
    setState({
      agents:    { ...INITIAL_AGENTS, coordinator: { status: 'running' } },
      result:    null,
      error:     '',
      streaming: true,
    })

    const url = `${apiBase}/demo/analyze/${encodeURIComponent(caseId)}/stream`
    const es = new EventSource(url)
    esRef.current = es

    es.onmessage = (ev: MessageEvent<string>) => {
      const data = JSON.parse(ev.data) as Record<string, unknown>

      // Final event — pipeline done
      if (data.agent === '__done__') {
        setState(prev => ({
          ...prev,
          result:    data.result as CaseResult,
          streaming: false,
        }))
        es.close()
        esRef.current = null
        return
      }

      const nodeName = String(data.agent)
      const completedIds = NODE_TO_AGENTS[nodeName] ?? []
      const nextId       = NEXT_RUNNING[nodeName] ?? null
      const elapsed      = typeof data.elapsed_ms === 'number' ? data.elapsed_ms : undefined

      setState(prev => {
        const updated: PipelineAgents = { ...prev.agents }

        // Mark completed agents
        for (const id of completedIds) {
          updated[id] = {
            status:    'complete',
            elapsedMs: elapsed,
            summary:   data,
          } satisfies AgentNodeState
        }

        // Mark next agent as running
        if (nextId) {
          updated[nextId] = { status: 'running' }
        }

        return { ...prev, agents: updated }
      })
    }

    es.onerror = () => {
      setState(prev => ({ ...prev, error: 'stream', streaming: false }))
      es.close()
      esRef.current = null
    }
  }, [apiBase])

  const stop = useCallback(() => {
    esRef.current?.close()
    esRef.current = null
    setState(prev => ({ ...prev, streaming: false }))
  }, [])

  /** Derive PipelineAgents from a completed result's audit_log (no-stream fallback). */
  const agentsFromResult = useCallback((result: CaseResult): PipelineAgents => {
    const agentMap: Record<string, AgentId[]> = {
      coordinator:          ['coordinator'],
      radiologist:          ['radiologist'],
      lab_analyst:          ['lab_analyst'],
      lab:                  ['lab_analyst'],
      safety:               ['safety'],
      documenter:           ['documenter'],
      clinical_documenter:  ['documenter'],
    }
    const agents: PipelineAgents = { ...INITIAL_AGENTS }
    for (const entry of result.audit_log) {
      const ids = agentMap[entry.agent] ?? []
      for (const id of ids) {
        agents[id] = { status: 'complete', elapsedMs: entry.duration_ms }
      }
    }
    return agents
  }, [])

  return { pipeline: state, startStream, stop, agentsFromResult }
}
