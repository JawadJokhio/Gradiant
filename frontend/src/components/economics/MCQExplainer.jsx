import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Upload, X, CheckCircle, XCircle, AlertTriangle,
    Lightbulb, ArrowLeft, RefreshCw, BookOpen, ChevronRight,
    Sparkles, Brain, Target
} from 'lucide-react'

const DIFFICULTY_STYLE = {
    Easy: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30' },
    Medium: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30' },
    Hard: { bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/30' },
    Unknown: { bg: 'bg-slate-500/10', text: 'text-slate-400', border: 'border-slate-500/30' },
}

function ResultCard({ result }) {
    const diff = DIFFICULTY_STYLE[result.difficulty] || DIFFICULTY_STYLE.Unknown

    return (
        <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, ease: 'easeOut' }} className="space-y-5">
            <div className="flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                        <CheckCircle size={20} className="text-emerald-400" />
                    </div>
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-widest text-emerald-400">Correct Answer</p>
                        <p className="text-2xl font-black text-[var(--primary-purple)]">{result.correct_option}</p>
                    </div>
                </div>
                <span className={`px-3 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border ${diff.bg} ${diff.text} ${diff.border}`}>
                    {result.difficulty || 'MCQ'}
                </span>
            </div>

            {result.concept && (
                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--primary-purple-light)]/10 border border-[var(--primary-purple-light)]/20 w-fit">
                    <BookOpen size={12} className="text-[var(--primary-purple)]" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-[var(--primary-purple)]">{result.concept}</span>
                </div>
            )}

            <div className="p-5 rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)]">
                <p className="text-[10px] font-black uppercase tracking-widest text-[var(--primary-purple)] mb-3 flex items-center gap-2">
                    <Brain size={12} /> Why This Answer Is Correct
                </p>
                <p className="text-sm leading-relaxed text-[var(--text-dark)] font-medium">{result.rationale}</p>
            </div>

            {result.why_others_wrong && (
                <div className="p-5 rounded-2xl border border-rose-500/20 bg-rose-500/5">
                    <p className="text-[10px] font-black uppercase tracking-widest text-rose-400 mb-3 flex items-center gap-2">
                        <XCircle size={12} /> Why Other Options Are Wrong
                    </p>
                    <p className="text-sm leading-relaxed text-[var(--text-dark)] font-medium whitespace-pre-line">{result.why_others_wrong}</p>
                </div>
            )}

            {result.examiner_tip && (
                <div className="p-5 rounded-2xl border border-amber-500/25 bg-amber-500/5">
                    <p className="text-[10px] font-black uppercase tracking-widest text-amber-400 mb-3 flex items-center gap-2">
                        <Lightbulb size={12} /> Examiner Tip
                    </p>
                    <p className="text-sm leading-relaxed text-[var(--text-dark)] font-medium">{result.examiner_tip}</p>
                </div>
            )}
        </motion.div>
    )
}

export default function MCQExplainer({ onBack }) {
    const [mode, setMode] = useState('text')
    const [textQuery, setTextQuery] = useState('')
    const [imageNote, setImageNote] = useState('')
    const [imageFile, setImageFile] = useState(null)
    const [imagePreview, setImagePreview] = useState(null)
    const [isLoading, setIsLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)
    const fileRef = useRef()

    const handleImageUpload = (e) => {
        const file = e.target.files?.[0]
        if (!file) return
        setImageFile(file)
        const reader = new FileReader()
        reader.onload = () => setImagePreview(reader.result)
        reader.readAsDataURL(file)
        setResult(null)
        setError(null)
    }

    const clearImage = () => {
        setImageFile(null)
        setImagePreview(null)
        if (fileRef.current) fileRef.current.value = ''
    }

    const handleModeChange = (nextMode) => {
        setMode(nextMode)
        setResult(null)
        setError(null)
        if (nextMode === 'text') {
            clearImage()
            setImageNote('')
        }
    }

    const handleSubmit = async () => {
        if (mode === 'text' && !textQuery.trim()) return
        if (mode === 'image' && !imageFile) return
        setIsLoading(true)
        setResult(null)
        setError(null)

        const formData = new FormData()
        if (mode === 'text') {
            formData.append('query', textQuery.trim())
        } else {
            formData.append('image', imageFile)
            if (imageNote.trim()) formData.append('query', imageNote.trim())
        }

        try {
            const res = await fetch('http://localhost:8000/economics/explain-mcq', { method: 'POST', body: formData })
            const data = await res.json()
            if (data.error) { setError(data.error); return }
            setResult(data)
        } catch {
            setError('Could not reach the backend. Please ensure the server is running.')
        } finally {
            setIsLoading(false)
        }
    }

    const canSubmit = mode === 'text' ? textQuery.trim().length > 0 : !!imageFile

    return (
        <div className="min-h-screen bg-[var(--bg-cream)] text-[var(--text-dark)] flex flex-col transition-colors duration-500">
            <header className="h-20 flex-shrink-0 bg-[var(--bg-card)]/70 backdrop-blur-xl border-b border-[var(--border-color)] px-6 flex items-center justify-between z-10 sticky top-0">
                <div className="flex items-center gap-4">
                    <button onClick={onBack} className="p-2 hover:bg-[var(--primary-purple-light)]/10 rounded-xl transition-colors text-[var(--primary-purple)] group">
                        <ArrowLeft size={22} className="group-hover:-translate-x-1 transition-transform" />
                    </button>
                    <div className="h-8 w-px bg-[var(--border-color)]" />
                    <div>
                        <p className="text-[9px] font-black uppercase tracking-widest text-emerald-500 mb-0.5">Cambridge 2281</p>
                        <h2 className="text-lg font-black text-[var(--primary-purple)] uppercase tracking-tighter">Economics MCQ Explainer</h2>
                    </div>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                    <Sparkles size={12} className="text-emerald-400" />
                    <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">1 Mark - Auto-Detected</span>
                </div>
            </header>

            <main className="flex-1 flex flex-col lg:flex-row lg:divide-x divide-[var(--border-color)] overflow-y-auto lg:overflow-hidden">
                <section className="flex-1 flex flex-col p-8 md:p-12 space-y-8 overflow-y-auto">
                    <div className="flex gap-3 p-1 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl w-fit">
                        {[
                            { key: 'text', label: 'Type MCQ', icon: <Brain size={15} /> },
                            { key: 'image', label: 'Upload Image', icon: <Upload size={15} /> },
                        ].map(({ key, label, icon }) => (
                            <button
                                key={key}
                                onClick={() => handleModeChange(key)}
                                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black uppercase tracking-wider transition-all ${mode === key ? 'bg-[var(--primary-purple)] text-white shadow-lg shadow-purple-900/25' : 'text-[var(--text-muted)] hover:text-[var(--primary-purple)]'}`}
                            >
                                {icon} {label}
                            </button>
                        ))}
                    </div>

                    <AnimatePresence mode="wait">
                        {mode === 'text' ? (
                            <motion.div key="text" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} className="space-y-5">
                                <div>
                                    <label className="text-[10px] font-black uppercase tracking-widest text-[var(--primary-purple)] mb-3 block">MCQ Question + Options</label>
                                    <textarea
                                        value={textQuery}
                                        onChange={e => setTextQuery(e.target.value)}
                                        onKeyDown={e => { if (e.ctrlKey && e.key === 'Enter') handleSubmit() }}
                                        placeholder={`Paste or type your MCQ here. Example:\n\nThe demand for a good increases when:\nA  its price falls\nB  the price of a complement falls\nC  consumer income falls (inferior good)\nD  a substitute becomes cheaper`}
                                        rows={10}
                                        className="w-full p-5 rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)] text-sm font-medium text-[var(--text-dark)] placeholder:text-[var(--text-muted)]/50 focus:outline-none focus:border-[var(--primary-purple)] resize-none transition-colors leading-relaxed"
                                    />
                                    <p className="text-[10px] text-[var(--text-muted)] mt-2">Ctrl + Enter to submit</p>
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div key="image" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }} className="space-y-5">
                                {!imagePreview ? (
                                    <label className="flex flex-col items-center justify-center w-full aspect-video border-4 border-dashed border-[var(--border-color)] rounded-3xl cursor-pointer hover:border-emerald-500/50 hover:bg-emerald-500/5 transition-all group">
                                        <input ref={fileRef} type="file" className="hidden" accept="image/*" onChange={handleImageUpload} />
                                        <div className="w-20 h-20 rounded-2xl bg-emerald-500/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                                            <Upload size={36} className="text-emerald-400" />
                                        </div>
                                        <p className="text-xl font-black text-[var(--primary-purple)]">Upload MCQ Image</p>
                                        <p className="text-sm text-[var(--text-muted)] mt-2">PNG, JPG or WEBP - Max 10MB</p>
                                        <p className="text-[10px] font-black uppercase tracking-widest text-emerald-400 mt-4">AI will read all text, options and diagrams</p>
                                    </label>
                                ) : (
                                    <div className="relative rounded-3xl overflow-hidden border border-[var(--border-color)] bg-[var(--bg-card)] p-3">
                                        <img src={imagePreview} alt="MCQ Preview" className="w-full h-auto rounded-2xl" />
                                        <button onClick={clearImage} className="absolute top-6 right-6 p-2.5 bg-[var(--bg-card)]/90 backdrop-blur-sm rounded-xl text-rose-400 hover:bg-rose-500 hover:text-white transition-all shadow-xl">
                                            <X size={18} />
                                        </button>
                                    </div>
                                )}
                                {imagePreview && (
                                    <textarea
                                        value={imageNote}
                                        onChange={e => setImageNote(e.target.value)}
                                        placeholder="Optional: add context about the question (e.g. 'This is about elasticity')"
                                        rows={3}
                                        className="w-full p-4 rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)] text-sm font-medium text-[var(--text-dark)] placeholder:text-[var(--text-muted)]/50 focus:outline-none focus:border-[var(--primary-purple)] resize-none transition-colors"
                                    />
                                )}
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <motion.button
                        onClick={handleSubmit}
                        disabled={!canSubmit || isLoading}
                        whileTap={{ scale: 0.97 }}
                        className="w-full py-5 rounded-2xl bg-[var(--primary-purple)] text-white font-black text-sm uppercase tracking-widest flex items-center justify-center gap-3 shadow-2xl shadow-purple-900/30 disabled:opacity-30 hover:opacity-90 transition-all"
                    >
                        {isLoading ? <><RefreshCw size={18} className="animate-spin" /> Analyzing MCQ...</> : <><Target size={18} /> Explain This MCQ</>}
                    </motion.button>

                    <div className="p-5 rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)]/50">
                        <p className="text-[9px] font-black uppercase tracking-widest text-[var(--primary-purple)] mb-3">Cambridge 2281 - MCQ Tips</p>
                        <ul className="space-y-2 text-xs text-[var(--text-muted)] font-medium">
                            <li className="flex gap-2"><ChevronRight size={12} className="text-emerald-400 mt-0.5 shrink-0" />Eliminate extreme-sounding options first</li>
                            <li className="flex gap-2"><ChevronRight size={12} className="text-emerald-400 mt-0.5 shrink-0" />Demand and quantity demanded are different</li>
                            <li className="flex gap-2"><ChevronRight size={12} className="text-emerald-400 mt-0.5 shrink-0" />Trace cause-and-effect step by step for macro questions</li>
                            <li className="flex gap-2"><ChevronRight size={12} className="text-emerald-400 mt-0.5 shrink-0" />Opportunity cost is the next best alternative foregone</li>
                        </ul>
                    </div>
                </section>

                <section className="flex-1 flex flex-col p-8 md:p-12 overflow-y-auto bg-[var(--bg-card)]/30">
                    <h3 className="text-[9px] font-black uppercase tracking-widest text-[var(--primary-purple)] mb-8">Examiner Analysis</h3>

                    <AnimatePresence mode="wait">
                        {isLoading && (
                            <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
                                {[80, 60, 90, 50].map((w, i) => (
                                    <div key={i} className="space-y-3">
                                        <div className={`h-3 bg-[var(--primary-purple-light)]/10 rounded-full w-${w === 80 ? '1/2' : w === 60 ? '1/3' : w === 90 ? '2/3' : '1/4'} animate-pulse`} />
                                        <div className="h-16 bg-[var(--primary-purple-light)]/5 rounded-2xl w-full animate-pulse" />
                                    </div>
                                ))}
                            </motion.div>
                        )}

                        {error && !isLoading && (
                            <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center h-full gap-5 text-center">
                                <div className="w-16 h-16 rounded-2xl bg-rose-500/10 flex items-center justify-center">
                                    <AlertTriangle size={28} className="text-rose-400" />
                                </div>
                                <p className="text-sm font-bold text-rose-400">{error}</p>
                            </motion.div>
                        )}

                        {result && !isLoading && !error && (
                            <motion.div key="result" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                                <div className="flex items-center gap-3 text-emerald-400 bg-emerald-500/10 px-5 py-3 rounded-2xl border border-emerald-500/20 text-xs font-black uppercase tracking-tighter mb-8">
                                    <CheckCircle size={16} /> Analysis Complete - 1 Mark Question
                                </div>
                                <ResultCard result={result} />
                            </motion.div>
                        )}

                        {!result && !isLoading && !error && (
                            <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-1 flex flex-col items-center justify-center gap-6 text-center opacity-30 px-8 py-20">
                                <div className="w-20 h-20 rounded-3xl bg-emerald-500/10 flex items-center justify-center">
                                    <BookOpen size={36} className="text-emerald-400" />
                                </div>
                                <p className="text-2xl font-black text-[var(--primary-purple)]">Ready to Explain</p>
                                <p className="text-sm text-[var(--text-muted)] font-medium max-w-xs">
                                    Type your MCQ question or upload an image from a past paper to get a full explanation.
                                </p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </section>
            </main>
        </div>
    )
}
