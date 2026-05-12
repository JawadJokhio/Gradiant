import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, BookOpen, Lightbulb, Calculator } from 'lucide-react'

export default function ConceptModal({ conceptKey, onClose }) {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (!conceptKey) return
        setLoading(true)
        setError(null)
        setData(null)
        fetch(`http://localhost:8000/api/math/concepts/${conceptKey}`)
            .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
            .then(d => { setData(d); setLoading(false) })
            .catch(e => { setError(String(e)); setLoading(false) })
    }, [conceptKey])

    useEffect(() => {
        const handler = (e) => { if (e.key === 'Escape') onClose() }
        window.addEventListener('keydown', handler)
        return () => window.removeEventListener('keydown', handler)
    }, [onClose])

    return (
        <AnimatePresence>
            <motion.div
                className="fixed inset-0 z-50 flex items-center justify-end"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={(e) => { if (e.target === e.currentTarget) onClose() }}
                style={{ background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(6px)' }}
            >
                <motion.div
                    initial={{ x: '100%', opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: '100%', opacity: 0 }}
                    transition={{ type: 'spring', damping: 28, stiffness: 280 }}
                    className="h-full w-full max-w-md flex flex-col"
                    style={{
                        background: 'linear-gradient(160deg,#1c1033 0%,#0f0a1e 100%)',
                        borderLeft: '1px solid rgba(245,158,11,0.22)',
                        boxShadow: '-12px 0 60px rgba(0,0,0,0.7)',
                    }}
                >
                    {/* Header */}
                    <div className="flex items-center justify-between px-6 py-5"
                        style={{ borderBottom: '1px solid rgba(245,158,11,0.12)' }}>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                                style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>
                                <BookOpen size={18} className="text-white" />
                            </div>
                            <div>
                                <p className="text-xs font-bold uppercase tracking-widest"
                                    style={{ color: '#f59e0b' }}>Concept Guide</p>
                                <p className="text-white font-black text-lg leading-tight">
                                    {loading ? 'Loading…' : (data?.title ?? conceptKey)}
                                </p>
                            </div>
                        </div>
                        <button
                            id="concept-modal-close"
                            onClick={onClose}
                            className="w-9 h-9 rounded-xl flex items-center justify-center transition-all hover:scale-110 active:scale-90"
                            style={{ background: 'rgba(245,158,11,0.1)', color: '#f59e0b' }}
                        >
                            <X size={18} />
                        </button>
                    </div>

                    {/* Body */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-5"
                        style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(245,158,11,0.3) transparent' }}>

                        {loading && (
                            <div className="flex flex-col items-center justify-center h-48 gap-4">
                                <div className="w-10 h-10 rounded-full border-2 animate-spin"
                                    style={{ borderColor: 'rgba(245,158,11,0.15)', borderTopColor: '#f59e0b' }} />
                                <p className="text-sm" style={{ color: 'rgba(255,255,255,0.35)' }}>Loading concept…</p>
                            </div>
                        )}

                        {error && (
                            <div className="rounded-2xl p-4"
                                style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)' }}>
                                <p className="text-red-400 text-sm">Could not load concept: {error}</p>
                            </div>
                        )}

                        {data && !loading && (
                            <>
                                {/* Explanation card */}
                                <div className="rounded-2xl p-5"
                                    style={{ background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.15)' }}>
                                    <div className="flex items-center gap-2 mb-3">
                                        <Lightbulb size={15} style={{ color: '#f59e0b' }} />
                                        <span className="text-xs font-bold uppercase tracking-widest"
                                            style={{ color: '#f59e0b' }}>Explanation</span>
                                    </div>
                                    <p className="text-sm leading-7" style={{ color: 'rgba(255,255,255,0.82)' }}>
                                        {data.explanation}
                                    </p>
                                </div>

                                {/* Worked example card */}
                                <div className="rounded-2xl p-5"
                                    style={{ background: 'rgba(234,88,12,0.06)', border: '1px solid rgba(234,88,12,0.18)' }}>
                                    <div className="flex items-center gap-2 mb-3">
                                        <Calculator size={15} style={{ color: '#ea580c' }} />
                                        <span className="text-xs font-bold uppercase tracking-widest"
                                            style={{ color: '#ea580c' }}>Worked Example</span>
                                    </div>
                                    <p className="font-mono text-sm leading-7 whitespace-pre-line"
                                        style={{ color: 'rgba(255,255,255,0.9)' }}>
                                        {data.example}
                                    </p>
                                </div>

                                {/* Footer tag */}
                                <div className="flex justify-end">
                                    <span className="px-3 py-1 rounded-full text-xs font-mono"
                                        style={{ background: 'rgba(245,158,11,0.08)', color: 'rgba(245,158,11,0.5)' }}>
                                        key: {data.key}
                                    </span>
                                </div>
                            </>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="px-6 py-4" style={{ borderTop: '1px solid rgba(245,158,11,0.08)' }}>
                        <p className="text-xs text-center" style={{ color: 'rgba(255,255,255,0.25)' }}>
                            Cambridge O-Level Mathematics · Syllabus 4024 / 0580
                        </p>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    )
}
