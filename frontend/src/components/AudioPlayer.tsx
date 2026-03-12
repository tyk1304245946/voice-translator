import { useRef, useState, useEffect } from 'react'
import { Play, Pause, Download } from 'lucide-react'

interface Props {
    src: string
}

function formatTime(s: number): string {
    if (!isFinite(s) || isNaN(s)) return '0:00'
    const m = Math.floor(s / 60)
    const sec = Math.floor(s % 60)
    return `${m}:${sec.toString().padStart(2, '0')}`
}

export default function AudioPlayer({ src }: Props) {
    const audioRef = useRef<HTMLAudioElement>(null)
    const [isPlaying, setIsPlaying] = useState(false)
    const [currentTime, setCurrentTime] = useState(0)
    const [duration, setDuration] = useState(0)

    // 切换音频源时重置状态
    useEffect(() => {
        setIsPlaying(false)
        setCurrentTime(0)
        setDuration(0)
    }, [src])

    const handlePlayPause = () => {
        if (!audioRef.current) return
        if (isPlaying) {
            audioRef.current.pause()
        } else {
            audioRef.current.play()
        }
    }

    const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!audioRef.current) return
        const time = Number(e.target.value)
        audioRef.current.currentTime = time
        setCurrentTime(time)
    }

    const handleDownload = () => {
        const a = document.createElement('a')
        a.href = src
        a.download = 'translation.mp3'
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
    }

    return (
        <div className="flex items-center gap-3 bg-slate-900/50 rounded-lg p-3">
            <audio
                ref={audioRef}
                src={src}
                onTimeUpdate={() => setCurrentTime(audioRef.current?.currentTime ?? 0)}
                onLoadedMetadata={() => setDuration(audioRef.current?.duration ?? 0)}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                onEnded={() => setIsPlaying(false)}
            />

            {/* 播放/暂停 */}
            <button
                onClick={handlePlayPause}
                className="flex-shrink-0 w-9 h-9 bg-indigo-600 hover:bg-indigo-500 rounded-full flex items-center justify-center text-white transition-colors"
                aria-label={isPlaying ? '暂停' : '播放'}
            >
                {isPlaying ? <Pause size={16} /> : <Play size={16} className="ml-0.5" />}
            </button>

            {/* 进度条 */}
            <div className="flex-1 flex flex-col gap-1 min-w-0">
                <input
                    type="range"
                    min={0}
                    max={duration || 0}
                    step={0.1}
                    value={currentTime}
                    onChange={handleSeek}
                    className="w-full h-1.5 appearance-none bg-slate-600 rounded-full cursor-pointer"
                />
                <div className="flex justify-between text-xs text-slate-500">
                    <span>{formatTime(currentTime)}</span>
                    <span>{formatTime(duration)}</span>
                </div>
            </div>

            {/* 下载 */}
            <button
                onClick={handleDownload}
                className="flex-shrink-0 w-9 h-9 bg-slate-700 hover:bg-slate-600 rounded-full flex items-center justify-center text-slate-400 hover:text-white transition-colors"
                aria-label="下载音频"
                title="下载 MP3"
            >
                <Download size={16} />
            </button>
        </div>
    )
}
