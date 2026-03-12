import type { GenerateItem, HistoryItem } from '../types'

export interface GenerateRequest {
    texts: string[]
    mode: 'normal' | 'short_video'
    voice_id?: string
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(path, options)
    if (!res.ok) {
        const text = await res.text()
        let message = text
        try {
            const json = JSON.parse(text)
            message = json.detail ?? text
        } catch {
            // 保持原始文本
        }
        throw new Error(message)
    }
    return res.json() as Promise<T>
}

export async function generate(req: GenerateRequest): Promise<GenerateItem[]> {
    const data = await request<{ results: GenerateItem[] }>('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
    })
    return data.results
}

export async function getHistory(): Promise<HistoryItem[]> {
    return request<HistoryItem[]>('/api/history')
}

export async function deleteHistoryItem(id: number): Promise<void> {
    await request(`/api/history/${id}`, { method: 'DELETE' })
}

export async function clearHistory(): Promise<void> {
    await request('/api/history', { method: 'DELETE' })
}
