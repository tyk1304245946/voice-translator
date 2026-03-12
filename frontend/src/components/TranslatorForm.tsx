import { useState } from 'react'
import { Plus, Trash2, Wand2, Loader2 } from 'lucide-react'
import { generate } from '../api/client'
import type { GenerateItem } from '../types'

interface Props {
    onResults: (items: GenerateItem[]) => void
    onSuccess: () => void
}

const EXAMPLE_TEXTS = [
    '今天给大家分享一个超级实用的小技巧，学会了之后真的能省很多时间。',
    '很多人都不知道，其实这件事可以用完全不同的方式来处理。',
]

export default function TranslatorForm({ onResults, onSuccess }: Props) {
    const [texts, setTexts] = useState<string[]>([''])
    const [mode, setMode] = useState<'normal' | 'short_video'>('normal')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const addText = () => setTexts((prev) => [...prev, ''])

    const removeText = (i: number) =>
        setTexts((prev) => prev.filter((_, idx) => idx !== i))

    const updateText = (i: number, val: string) =>
        setTexts((prev) => prev.map((t, idx) => (idx === i ? val : t)))

    const loadExamples = () => setTexts(EXAMPLE_TEXTS)

    const handleSubmit = async () => {
        const filtered = texts.filter((t) => t.trim())
        if (!filtered.length) return

        setLoading(true)
        setError(null)
        try {
            const results = await generate({ texts: filtered, mode })
            onResults(results)
            onSuccess()
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : '生成失败，请重试')
        } finally {
            setLoading(false)
        }
    }

    const hasContent = texts.some((t) => t.trim())

    return (
        <div className="bg-slate-800 rounded-xl p-6 flex flex-col gap-4">
            {/* 标题 + 模式切换 */}
            <div className="flex items-center justify-between flex-wrap gap-3">
                <h2 className="text-white font-semibold text-lg">输入文本</h2>
                <div className="flex items-center bg-slate-700 p-1 rounded-lg gap-1">
                    <button
                        onClick={() => setMode('normal')}
                        className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${mode === 'normal'
                                ? 'bg-indigo-600 text-white'
                                : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        普通翻译
                    </button>
                    <button
                        onClick={() => setMode('short_video')}
                        className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${mode === 'short_video'
                                ? 'bg-indigo-600 text-white'
                                : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        🎬 短视频优化
                    </button>
                </div>
            </div>

            {/* 模式说明 */}
            {mode === 'short_video' && (
                <div className="bg-indigo-900/30 border border-indigo-700/50 rounded-lg p-3 text-xs text-indigo-300 leading-relaxed">
                    短视频优化：每句 ≤12 词，语气口语化，方便录音朗读
                </div>
            )}

            {/* 文本输入区 */}
            <div className="flex flex-col gap-3">
                {texts.map((text, i) => (
                    <div key={i}>
                        {texts.length > 1 && (
                            <div className="flex items-center justify-between mb-1.5">
                                <span className="text-slate-400 text-xs font-medium">
                                    文案 {i + 1}
                                </span>
                                <button
                                    onClick={() => removeText(i)}
                                    className="text-slate-500 hover:text-red-400 transition-colors"
                                    aria-label="删除此条"
                                >
                                    <Trash2 size={14} />
                                </button>
                            </div>
                        )}
                        <textarea
                            value={text}
                            onChange={(e) => updateText(i, e.target.value)}
                            placeholder={
                                i === 0
                                    ? '在此输入中文口播文本，例如：今天给大家分享一个超级实用的技巧……'
                                    : '输入下一条文案……'
                            }
                            rows={5}
                            className="w-full bg-slate-700 text-white placeholder-slate-500 rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 border border-slate-600 focus:border-indigo-500 transition-colors"
                        />
                    </div>
                ))}
            </div>

            {/* 操作按钮行 */}
            <div className="flex items-center gap-3 flex-wrap">
                <button
                    onClick={addText}
                    className="flex items-center gap-1.5 text-slate-400 hover:text-indigo-400 border border-dashed border-slate-600 hover:border-indigo-500 rounded-lg px-3 py-2 text-sm transition-colors"
                >
                    <Plus size={15} />
                    添加文案（批量）
                </button>
                {!hasContent && (
                    <button
                        onClick={loadExamples}
                        className="text-slate-500 hover:text-slate-300 text-sm underline underline-offset-2 transition-colors"
                    >
                        加载示例
                    </button>
                )}
            </div>

            {/* 错误提示 */}
            {error && (
                <div className="bg-red-900/30 border border-red-700/60 rounded-lg p-3 text-sm text-red-400">
                    {error}
                </div>
            )}

            {/* 提交按钮 */}
            <button
                onClick={handleSubmit}
                disabled={loading || !hasContent}
                className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 disabled:cursor-not-allowed text-white rounded-lg py-3 font-medium transition-colors"
            >
                {loading ? (
                    <>
                        <Loader2 size={18} className="animate-spin" />
                        处理中，请稍候…
                    </>
                ) : (
                    <>
                        <Wand2 size={18} />
                        翻译并生成语音
                    </>
                )}
            </button>
        </div>
    )
}
