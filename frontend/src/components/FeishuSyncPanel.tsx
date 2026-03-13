import { useEffect, useState } from 'react'
import { Loader2, RefreshCw, AlertTriangle, CheckCircle2 } from 'lucide-react'
import {
    getFeishuPollingConfig,
    syncFeishu,
    updateFeishuPollingConfig,
} from '../api/client'
import type { FeishuPollingConfig, FeishuSyncResponse } from '../types'

interface Props {
    onSuccess?: () => void
}

export default function FeishuSyncPanel({ onSuccess }: Props) {
    const [limit, setLimit] = useState(20)
    const [mode, setMode] = useState<'normal' | 'short_video'>('short_video')
    const [audioOnly, setAudioOnly] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [result, setResult] = useState<FeishuSyncResponse | null>(null)
    const [polling, setPolling] = useState<FeishuPollingConfig | null>(null)
    const [pollingError, setPollingError] = useState<string | null>(null)
    const [pollingLoading, setPollingLoading] = useState(false)

    useEffect(() => {
        const loadPollingConfig = async () => {
            try {
                const config = await getFeishuPollingConfig()
                setPolling(config)
            } catch (e: unknown) {
                setPollingError(e instanceof Error ? e.message : '轮询配置加载失败')
            }
        }
        void loadPollingConfig()
    }, [])

    const handleSync = async () => {
        setLoading(true)
        setError(null)
        try {
            const data = await syncFeishu({ limit, mode, audio_only: audioOnly })
            setResult(data)
            if (onSuccess) {
                onSuccess()
            }
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : '飞书同步失败，请重试')
        } finally {
            setLoading(false)
        }
    }

    const handleSavePolling = async () => {
        if (!polling) return
        setPollingLoading(true)
        setPollingError(null)
        try {
            const next = await updateFeishuPollingConfig({
                enabled: polling.enabled,
                interval_seconds: polling.interval_seconds,
                batch_size: polling.batch_size,
            })
            setPolling(next)
        } catch (e: unknown) {
            setPollingError(e instanceof Error ? e.message : '轮询配置保存失败')
        } finally {
            setPollingLoading(false)
        }
    }

    return (
        <div className="bg-slate-800 rounded-xl p-6 flex flex-col gap-4">
            <div className="flex items-center justify-between gap-3 flex-wrap">
                <h2 className="text-white font-semibold text-lg">飞书多维表格同步</h2>
                <span className="text-xs text-slate-400">
                    批量读取中文脚本并回填英文与音频
                </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <label className="flex flex-col gap-1.5">
                    <span className="text-xs text-slate-400">本次处理上限</span>
                    <input
                        type="number"
                        min={1}
                        max={200}
                        value={limit}
                        onChange={(e) => {
                            const next = Number(e.target.value)
                            if (Number.isNaN(next)) return
                            setLimit(Math.min(200, Math.max(1, next)))
                        }}
                        className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                </label>

                <label className="flex flex-col gap-1.5">
                    <span className="text-xs text-slate-400">翻译模式</span>
                    <select
                        value={mode}
                        disabled={audioOnly}
                        onChange={(e) => setMode(e.target.value as 'normal' | 'short_video')}
                        className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-60"
                    >
                        <option value="normal">普通翻译</option>
                        <option value="short_video">短视频优化</option>
                    </select>
                </label>
            </div>

            <label className="flex items-center gap-2 text-sm text-slate-300">
                <input
                    type="checkbox"
                    checked={audioOnly}
                    onChange={(e) => setAudioOnly(e.target.checked)}
                    className="h-4 w-4 rounded border-slate-500 bg-slate-700 text-emerald-500 focus:ring-emerald-500"
                />
                仅补音频（不触发翻译）
            </label>

            <div className="bg-slate-700/60 border border-slate-600 rounded-lg p-4 flex flex-col gap-3">
                <div className="text-sm text-slate-200 font-medium">自动轮询配置</div>

                {polling && (
                    <>
                        <label className="flex items-center gap-2 text-sm text-slate-300">
                            <input
                                type="checkbox"
                                checked={polling.enabled}
                                onChange={(e) =>
                                    setPolling((prev) =>
                                        prev ? { ...prev, enabled: e.target.checked } : prev
                                    )
                                }
                                className="h-4 w-4 rounded border-slate-500 bg-slate-700 text-indigo-500 focus:ring-indigo-500"
                            />
                            启用自动轮询
                        </label>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <label className="flex flex-col gap-1.5">
                                <span className="text-xs text-slate-400">轮询间隔（秒）</span>
                                <input
                                    type="number"
                                    min={5}
                                    max={3600}
                                    value={polling.interval_seconds}
                                    onChange={(e) => {
                                        const next = Number(e.target.value)
                                        if (Number.isNaN(next)) return
                                        setPolling((prev) =>
                                            prev
                                                ? {
                                                    ...prev,
                                                    interval_seconds: Math.min(
                                                        3600,
                                                        Math.max(5, next)
                                                    ),
                                                }
                                                : prev
                                        )
                                    }}
                                    className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                />
                            </label>
                            <label className="flex flex-col gap-1.5">
                                <span className="text-xs text-slate-400">每轮处理上限</span>
                                <input
                                    type="number"
                                    min={1}
                                    max={200}
                                    value={polling.batch_size}
                                    onChange={(e) => {
                                        const next = Number(e.target.value)
                                        if (Number.isNaN(next)) return
                                        setPolling((prev) =>
                                            prev
                                                ? {
                                                    ...prev,
                                                    batch_size: Math.min(200, Math.max(1, next)),
                                                }
                                                : prev
                                        )
                                    }}
                                    className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                />
                            </label>
                        </div>

                        <button
                            onClick={handleSavePolling}
                            disabled={pollingLoading}
                            className="self-start px-3 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-600 disabled:text-slate-400 text-white transition-colors"
                        >
                            {pollingLoading ? '保存中...' : '保存轮询配置'}
                        </button>
                    </>
                )}

                {pollingError && (
                    <div className="text-xs text-amber-300 bg-amber-900/20 border border-amber-700/50 rounded-md px-3 py-2">
                        {pollingError}
                    </div>
                )}
            </div>

            <button
                onClick={handleSync}
                disabled={loading}
                className="flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-500 disabled:cursor-not-allowed text-white rounded-lg py-2.5 font-medium transition-colors"
            >
                {loading ? (
                    <>
                        <Loader2 size={17} className="animate-spin" />
                        同步中...
                    </>
                ) : (
                    <>
                        <RefreshCw size={17} />
                        立即同步飞书
                    </>
                )}
            </button>

            {error && (
                <div className="bg-red-900/30 border border-red-700/60 rounded-lg p-3 text-sm text-red-300 flex items-start gap-2">
                    <AlertTriangle size={16} className="mt-0.5 shrink-0" />
                    <span>{error}</span>
                </div>
            )}

            {result && (
                <div className="bg-slate-700/60 border border-slate-600 rounded-lg p-4 flex flex-col gap-3">
                    <div className="text-sm text-slate-200 flex items-center gap-2">
                        <CheckCircle2 size={16} className="text-emerald-400" />
                        本次同步已完成
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs">
                        <div className="bg-slate-800 rounded-md px-2 py-2 text-slate-300">
                            扫描: <span className="text-white">{result.scanned}</span>
                        </div>
                        <div className="bg-slate-800 rounded-md px-2 py-2 text-slate-300">
                            成功: <span className="text-white">{result.processed}</span>
                        </div>
                        <div className="bg-slate-800 rounded-md px-2 py-2 text-slate-300">
                            降级: <span className="text-white">{result.downgraded}</span>
                        </div>
                        <div className="bg-slate-800 rounded-md px-2 py-2 text-slate-300">
                            跳过: <span className="text-white">{result.skipped}</span>
                        </div>
                        <div className="bg-slate-800 rounded-md px-2 py-2 text-slate-300">
                            失败: <span className="text-white">{result.failed}</span>
                        </div>
                    </div>

                    {!!result.errors.length && (
                        <div className="max-h-32 overflow-y-auto bg-slate-900/50 rounded-md border border-slate-600 p-2 text-xs text-amber-300">
                            {result.errors.map((msg, idx) => (
                                <div key={`${idx}-${msg}`} className="mb-1 last:mb-0 break-all">
                                    {msg}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
