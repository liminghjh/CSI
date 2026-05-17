export interface ToolItem {
  id: number
  name: string
  address: string | null
  description: string | null
}

export interface LlmItem {
  id: number
  name: string
  provider: string
  key: string | null
  url: string
  model: string
}

export interface ToolForm {
  tool_name: string
  tool_address: string
  tool_description: string
}

export interface LlmForm {
  name: string
  provider: string
  key: string
  url: string
  model: string
}

export interface TaskPayload {
  url_or_ip: string
  port: number | null
  LLM_id: number
  system_doc: number
}

export interface SseStartEvent {
  type: 'start'
  message: string
}

export interface SsePrepareEvent {
  type: 'prepare'
  message: string
}

export interface SseStartToolEvent {
  type: 'start_tool'
  message: string
  tool: string
}

export interface SseEndToolEvent {
  type: 'end_tool'
  message: string
  tool: string
}

export interface SseReportEvent {
  type: 'report'
  message: string
}

export interface SseErrorEvent {
  type: 'error'
  message: string
}

export type SseTaskEvent =
  | SseStartEvent
  | SsePrepareEvent
  | SseStartToolEvent
  | SseEndToolEvent
  | SseReportEvent
  | SseErrorEvent

export interface KnowledgeUploadPayload {
  file_addr: string
  file: File
}

export interface KnowledgeDeletePayload {
  file_addr: string
  file_name: string
}

export interface KnowledgeTreeNode {
  path_name: string
  dirs: KnowledgeTreeNode[]
  files: string[]
}

type ResponseMode = 'json' | 'text'

async function request<T>(path: string, init?: RequestInit, mode: ResponseMode = 'json'): Promise<T> {
  const headers = new Headers(init?.headers ?? {})
  const body = init?.body

  if (!(body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(path, {
    ...init,
    headers,
  })

  const rawText = await response.text()

  if (!response.ok) {
    throw new Error(rawText || `Request failed with status ${response.status}`)
  }

  if (!rawText) {
    return null as T
  }

  if (mode === 'text') {
    try {
      return JSON.parse(rawText) as T
    } catch {
      return rawText as T
    }
  }

  const parsed = JSON.parse(rawText) as T

  if (typeof parsed === 'string') {
    return rawText as T
  }

  return parsed
}

export function fetchTools() {
  return request<ToolItem[]>('/tool/tools_list')
}

export function createTool(payload: ToolForm) {
  return request<null>('/tool/add', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function removeTool(toolId: number) {
  return request<null>('/tool/delete', {
    method: 'POST',
    body: JSON.stringify(toolId),
  })
}

export function fetchLlms() {
  return request<LlmItem[]>('/LLM/LLM_list')
}

export function createLlm(payload: LlmForm) {
  return request<null>('/LLM/add', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function removeLlm(id: number) {
  return request<null>('/LLM/delete', {
    method: 'POST',
    body: JSON.stringify(id),
  })
}

export function testLlm(id: number) {
  return request<boolean>('/LLM/test', {
    method: 'POST',
    body: JSON.stringify(id),
  })
}

export async function fetchKnowledgeTree() {
  const payload = await request<string>('/vul_database/database_list', undefined, 'text')
  const firstPass = JSON.parse(payload) as KnowledgeTreeNode | string
  if (typeof firstPass === 'string') {
    return JSON.parse(firstPass) as KnowledgeTreeNode
  }
  return firstPass
}

export function uploadKnowledgeFile(payload: KnowledgeUploadPayload) {
  const form = new FormData()
  form.append('file_addr', payload.file_addr)
  form.append('file', payload.file)

  return request<{ message: string; ids: string[] }>('/vul_database/upload', {
    method: 'POST',
    body: form,
  })
}

export function deleteKnowledgeFile(payload: KnowledgeDeletePayload) {
  return request<{ message: string }>('/vul_database/delete', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function* startTaskStream(
  payload: TaskPayload,
): AsyncGenerator<SseTaskEvent, void, void> {
  const response = await fetch('/start_task', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const text = await response.text().catch(() => '')
    throw new Error(text || `Request failed with status ${response.status}`)
  }

  if (!response.body) {
    throw new Error('浏览器不支持流式读取（ReadableStream 不可用）')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n')
    buffer = parts.pop() ?? ''

    for (const line of parts) {
      if (line.startsWith('data: ')) {
        const raw = line.slice(6).trim()
        if (!raw) continue
        try {
          const parsed = JSON.parse(raw) as SseTaskEvent
          yield parsed
        } catch {
          // skip unparseable lines
        }
      }
    }
  }

  if (buffer.startsWith('data: ')) {
    const raw = buffer.slice(6).trim()
    if (raw) {
      try {
        const parsed = JSON.parse(raw) as SseTaskEvent
        yield parsed
      } catch {
        // skip
      }
    }
  }
}
