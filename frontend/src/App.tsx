import { useState, useCallback } from 'react'
import type { GenerateItem } from './types'
import TranslatorForm from './components/TranslatorForm'
import ResultPanel from './components/ResultPanel'
import HistoryPanel from './components/HistoryPanel'
import FeishuSyncPanel from './components/FeishuSyncPanel'

type Tab = 'translate' | 'history'

export default function App() {
    const [activeTab, setActiveTab] = useState<Tab>('translate')
    const [results, setResults] = useState<GenerateItem[]>([])
    const [historyKey, setHistoryKey] = useState(0)

    const handleResults = useCallback((items: GenerateItem[]) => {
        setResults(items)
    }, [])

    // 生成成功后刷新历史（切换到历史 tab 时重新拉取）
    const handleSuccess = useCallback(() => {
        setHistoryKey((k) => k + 1)
    }, [])

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800">
            {/* Header */}
            <header className="bg-slate-900/80 backdrop-blur border-b border-slate-700/50 px-6 py-4">
                <div className="max-w-7xl mx-auto flex items-center gap-3">
                    <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center font-bold text-white text-sm">
                        VT
                    </div>
                    <h1 className="text-white font-semibold text-lg">Voice Translator</h1>
                    <span className="text-slate-500 text-sm">中文口播 → 英文语音</span>
                </div>
            </header>

            {/* Tab Navigation */}
            <div className="max-w-7xl mx-auto px-6 pt-6">
                <div className="flex gap-1 bg-slate-800/60 p-1 rounded-xl w-fit border border-slate-700/50">
                    {(
                        [
                            { id: 'translate', label: '翻译 & 语音' },
                            { id: 'history', label: '历史记录' },
                        ] as { id: Tab; label: string }[]
                    ).map(({ id, label }) => (
                        <button
                            key={id}
                            onClick={() => setActiveTab(id)}
                            className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === id
                                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/30'
                                : 'text-slate-400 hover:text-white'
                                }`}
                        >
                            {label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Content */}
            <main className="max-w-7xl mx-auto px-6 py-6">
                {activeTab === 'translate' ? (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
                        <div className="flex flex-col gap-6">
                            <TranslatorForm onResults={handleResults} onSuccess={handleSuccess} />
                            <FeishuSyncPanel onSuccess={handleSuccess} />
                        </div>
                        <ResultPanel results={results} />
                    </div>
                ) : (
                    <HistoryPanel key={historyKey} />
                )}
            </main>
        </div>
    )
}
