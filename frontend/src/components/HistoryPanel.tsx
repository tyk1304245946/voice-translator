import { useState, useEffect, useCallback } from 'react'
import { Trash2, Trash, RefreshCw } from 'lucide-react'
import { getHistory, deleteHistoryItem, clearHistory } from '../api/client'
import type { HistoryItem } from '../types'
import AudioPlayer from './AudioPlayer'

function formatBeijingTime(isoString: string): string {
    // 后端历史时间可能是无时区的 ISO 字符串（SQLite 常见），需按 UTC 解释。
    const hasTimezone = /([zZ]|[+-]\d{2}:\d{2})$/.test(isoString)
    const normalized = hasTimezone ? isoString : `${isoString}Z`
    const date = new Date(normalized)
    if (Number.isNaN(date.getTime())) return isoString
    return new Intl.DateTimeFormat('zh-CN', {
        timeZone: 'Asia/Shanghai',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
    }).format(date)
}

export default function HistoryPanel() {
    const [items, setItems] = useState<HistoryItem[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const fetchHistory = useCallback(async () => {
        setLoading(true)
        setError(null)
        try {
            const data = await getHistory()
            setItems(data)
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : '加载失败')
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchHistory()
    }, [fetchHistory])

    const handleDelete = async (id: number) => {
        try {
            await deleteHistoryItem(id)
            setItems((prev) => prev.filter((item) => item.id !== id))
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : '删除失败')
        }
    }

    const handleClearAll = async () => {
        if (!window.confirm('确认清空所有历史记录？此操作不可撤销。')) return
        try {
            await clearHistory()
            setItems([])
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : '清空失败')
        }
    }

    return (
        <div className="bg-slate-800 rounded-xl p-6">
            {/* 标题栏 */}
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-white font-semibold text-lg">
                    历史记录
                    {!loading && (
                        <span className="text-slate-400 text-sm font-normal ml-2">
                            {items.length} 条
                        </span>
                    )}
                </h2>
                <div className="flex gap-2">
                    <button
                        onClick={fetchHistory}
                        disabled={loading}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-slate-400 hover:text-white bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors disabled:opacity-50"
                    >
                        <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
                        刷新
                    </button>
                    {items.length > 0 && (
                        <button
                            onClick={handleClearAll}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-red-400 hover:text-red-300 bg-red-900/30 hover:bg-red-900/50 rounded-lg transition-colors"
                        >
                            <Trash size={14} />
                            清空
                        </button>
                    )}
                </div>
            </div>

            {/* 错误 */}
            {error && (
                <div className="bg-red-900/30 border border-red-700/60 rounded-lg p-3 text-sm text-red-400 mb-4">
                    {error}
                </div>
            )}

            {/* 加载中 */}
            {loading && (
                <div className="flex items-center justify-center h-40 text-slate-400 text-sm">
                    加载中…
                </div>
            )}

            {/* 空状态 */}
            {!loading && items.length === 0 && (
                <div className="flex flex-col items-center justify-center h-40 text-slate-500">
                    <div className="text-5xl mb-3 opacity-40">📭</div>
                    <p className="text-sm">暂无历史记录</p>
                </div>
            )}

            {/* 历史列表 */}
            {!loading && items.length > 0 && (
                <div className="flex flex-col gap-4">
                    {items.map((item) => (
                        <div key={item.id} className="bg-slate-700 rounded-lg p-4">
                            {/* 元信息行 */}
                            <div className="flex items-start gap-3 mb-3">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                                        <span
                                            className={`px-2 py-0.5 rounded text-xs font-medium ${item.mode === 'short_video'
                                                ? 'bg-purple-900/60 text-purple-300'
                                                : 'bg-slate-600 text-slate-300'
                                                }`}
                                        >
                                            {item.mode === 'short_video' ? '🎬 短视频' : '普通'}
                                        </span>
                                        <span className="text-slate-500 text-xs">
                                            {formatBeijingTime(item.created_at)}
                                        </span>
                                    </div>
                                    <p className="text-slate-400 text-sm mb-1 leading-relaxed">
                                        {item.original_text}
                                    </p>
                                    <p className="text-white text-sm leading-relaxed">
                                        {item.translated_text}
                                    </p>
                                    {item.download_name && (
                                        <p className="text-slate-400 text-xs mt-2 break-all">
                                            下载名称：
                                            <span className="text-slate-200 ml-1">
                                                {item.download_name}
                                            </span>
                                        </p>
                                    )}
                                </div>
                                <button
                                    onClick={() => handleDelete(item.id)}
                                    className="flex-shrink-0 text-slate-500 hover:text-red-400 transition-colors mt-1"
                                    aria-label="删除此记录"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>

                            {/* 音频播放 */}
                            {item.audio_filename && (
                                <AudioPlayer
                                    src={`/audio/${item.audio_filename}`}
                                    downloadName={item.download_name}
                                />
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
