import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import type { GenerateItem } from '../types'
import AudioPlayer from './AudioPlayer'

function ResultCard({ item, index }: { item: GenerateItem; index: number }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(item.translated)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-slate-700 rounded-lg p-4 flex flex-col gap-3">
      {/* 原文 */}
      <div>
        <div className="text-slate-500 text-xs mb-1.5 font-medium">
          {index + 1}. 原文
        </div>
        <p className="text-slate-300 text-sm leading-relaxed">{item.original}</p>
      </div>

      <div className="border-t border-slate-600/50" />

      {/* 译文 */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-slate-500 text-xs font-medium">译文（英文）</span>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-indigo-400 transition-colors"
          >
            {copied ? (
              <Check size={13} className="text-green-400" />
            ) : (
              <Copy size={13} />
            )}
            {copied ? '已复制' : '复制'}
          </button>
        </div>
        <p className="text-white text-sm leading-relaxed font-medium">
          {item.translated}
        </p>
      </div>

      {/* 音频播放器 */}
      <AudioPlayer src={item.audio_url} />
    </div>
  )
}

interface Props {
  results: GenerateItem[]
}

export default function ResultPanel({ results }: Props) {
  if (!results.length) {
    return (
      <div className="bg-slate-800 rounded-xl p-6 flex flex-col items-center justify-center min-h-64">
        <div className="text-6xl mb-4 opacity-30">🎙️</div>
        <p className="text-slate-500 text-sm text-center leading-relaxed">
          翻译结果和音频将在此显示
          <br />
          <span className="text-slate-600 text-xs">
            填入文案，点击「翻译并生成语音」
          </span>
        </p>
      </div>
    )
  }

  return (
    <div className="bg-slate-800 rounded-xl p-6 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-white font-semibold text-lg">
          翻译结果
          <span className="text-slate-400 text-sm font-normal ml-2">
            {results.length} 条
          </span>
        </h2>
      </div>

      <div className="flex flex-col gap-3 overflow-y-auto max-h-[calc(100vh-300px)]">
        {results.map((item, i) => (
          <ResultCard key={item.id} item={item} index={i} />
        ))}
      </div>
    </div>
  )
}
