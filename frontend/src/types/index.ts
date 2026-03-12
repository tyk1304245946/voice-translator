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
