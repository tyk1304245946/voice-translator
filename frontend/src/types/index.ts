export interface GenerateItem {
    id: number
    original: string
    translated: string
    audio_url: string
    download_name: string
}

export interface HistoryItem {
    id: number
    original_text: string
    translated_text: string
    audio_filename: string | null
    download_name: string | null
    mode: string
    created_at: string
}

export interface FeishuSyncRequest {
    limit: number
    mode: 'normal' | 'short_video'
    voice_id?: string
    audio_only?: boolean
}

export interface FeishuSyncResponse {
    scanned: number
    processed: number
    downgraded: number
    skipped: number
    failed: number
    errors: string[]
}

export interface FeishuPollingConfig {
    enabled: boolean
    interval_seconds: number
    batch_size: number
}

export interface FeishuPollingConfigUpdateRequest {
    enabled?: boolean
    interval_seconds?: number
    batch_size?: number
}
