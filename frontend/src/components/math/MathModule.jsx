import { useState, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Calculator, Send, Sparkles, Hash, Award, RefreshCw, AlertTriangle } from 'lucide-react'
import MathCalculatorInput from './MathCalculatorInput'
import MathSolutionViewer from './MathSolutionViewer'

const MARKS_OPTIONS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20]

export default function MathModule({ onBack }) {
    const [question, setQuestion] = useState('')
    const [questionNumber, setQuestionNumber] = useState('1')
    const [marks, setMarks] = useState(null)
    const [solution, setSolution] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [showPad, setShowPad] = useState(true)
    const textareaRef = useRef(null)

    // Validation
    const isValid = question.trim().length >= 3 && marks !== null

    const handleSolve = useCallback(async () => {
        if (!isValid || loading) return
        setLoading(true)
        setError(null)
        setSolution(null)

        try {
            const res = await fetch('http://localhost:8000/api/math/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question.trim(),
                    question_number: parseInt(questionNumber),
                    marks: parseInt(marks),
                }),
            })
            if (!res.ok) {
                const err = await res.json().catch(() => ({}))
                throw new Error(err.detail || `Server error ${res.status}`)
            }
            const data = await res.json()
            setSolution(data)
        } catch (e) {
            setError(e.message || 'Something went wrong')
        } finally {
            setLoading(false)
        }
    }, [isValid, loading, question, questionNumber, marks])

    const handleReset = () => {
        setQuestion('')
        setQuestionNumber('')
        setMarks(null)
        setSolution(null)
        setError(null)
        textareaRef.current?.focus()
    }

    return (
        <div className="min-h-screen w-full flex flex-col"
            style={{
                background: 'linear-gradient(160deg,#0f0a1e 0%,#1a0e00 50%,#0f0a1e 100%)',
                fontFamily: "'Inter', 'Outfit', sans-serif",
            }}>

            {/* ── Header ──────────────────────────────────────────────────── */}
            <div className="flex items-center justify-between px-6 py-4 shrink-0"
                style={{ borderBottom: '1px solid rgba(245,158,11,0.1)' }}>
                <div className="flex items-center gap-4">
                    <button
                        id="math-back-btn"
                        onClick={onBack}
                        className="flex items-center gap-2 px-4 py-2 rounded-xl font-semibold text-sm transition-all hover:scale-105 active:scale-95"
                        style={{ background: 'rgba(245,158,11,0.08)', color: '#f59e0b', border: '1px solid rgba(245,158,11,0.15)' }}
                    >
                        <ArrowLeft size={16} /> Back
                    </button>
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-2xl flex items-center justify-center"
                            style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)', boxShadow: '0 0 20px rgba(245,158,11,0.4)' }}>
                            <Calculator size={20} className="text-white" />
                        </div>
                        <div>
                            <h1 className="font-black text-xl" style={{ color: '#fff' }}>Math Solver</h1>
                            <p className="text-xs" style={{ color: 'rgba(255,255,255,0.35)' }}>
                                O-Level · Cambridge 4024 / 0580
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {solution && (
                        <button
                            id="math-reset-btn"
                            onClick={handleReset}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl font-semibold text-sm transition-all hover:scale-105 active:scale-95"
                            style={{ background: 'rgba(245,158,11,0.08)', color: '#f59e0b', border: '1px solid rgba(245,158,11,0.15)' }}
                        >
                            <RefreshCw size={15} /> New Question
                        </button>
                    )}
                    <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full"
                        style={{ background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.12)' }}>
                        <Sparkles size={13} style={{ color: '#f59e0b' }} />
                        <span className="text-xs font-semibold" style={{ color: 'rgba(245,158,11,0.7)' }}>
                            Step-by-Step AI
                        </span>
                    </div>
                </div>
            </div>

            {/* ── Main layout ─────────────────────────────────────────────── */}
            <div className="flex-1 flex gap-0 overflow-hidden">

                {/* ── Left Panel: Input ────────────────────────────────────── */}
                <div className="w-full lg:w-[480px] shrink-0 flex flex-col overflow-y-auto p-5 gap-4"
                    style={{
                        borderRight: '1px solid rgba(245,158,11,0.08)',
                        scrollbarWidth: 'thin',
                        scrollbarColor: 'rgba(245,158,11,0.2) transparent',
                    }}>

                    {/* Question meta row */}
                    <div className="flex gap-3">
                        {/* Marks */}
                        <div className="flex-1">
                            <label className="block text-xs font-bold uppercase tracking-widest mb-2"
                                style={{ color: '#f59e0b' }}>
                                <Award size={11} className="inline mr-1" />
                                Marks <span style={{ color: '#ef4444' }}>*</span>
                            </label>
                            <select
                                id="math-marks-select"
                                value={marks ?? ''}
                                onChange={e => setMarks(e.target.value ? parseInt(e.target.value) : null)}
                                className="w-full rounded-xl px-4 py-3 text-sm font-bold outline-none transition-all appearance-none cursor-pointer"
                                style={{
                                    background: '#1a1228',
                                    border: `1px solid ${marks ? 'rgba(245,158,11,0.4)' : 'rgba(255,255,255,0.08)'}`,
                                    color: marks ? '#fff' : 'rgba(255,255,255,0.35)',
                                }}
                            >
                                <option value="">Select marks (controls solution depth)</option>
                                {MARKS_OPTIONS.map(m => (
                                    <option key={m} value={m}>{m} mark{m !== 1 ? 's' : ''}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Marks quick-pick */}
                    <div className="flex flex-wrap gap-2">
                        {[1, 2, 3, 4, 5, 6, 8, 10].map(m => (
                            <button
                                key={m}
                                id={`marks-quick-${m}`}
                                onClick={() => setMarks(m)}
                                className="px-3 py-1.5 rounded-xl text-xs font-bold transition-all hover:scale-105 active:scale-95"
                                style={{
                                    background: marks === m
                                        ? 'linear-gradient(135deg,#f59e0b,#ea580c)'
                                        : 'rgba(245,158,11,0.07)',
                                    color: marks === m ? '#fff' : 'rgba(245,158,11,0.65)',
                                    border: `1px solid ${marks === m ? 'transparent' : 'rgba(245,158,11,0.15)'}`,
                                    boxShadow: marks === m ? '0 0 12px rgba(245,158,11,0.4)' : 'none',
                                }}
                            >
                                [{m}]
                            </button>
                        ))}
                    </div>

                    {/* Question textarea */}
                    <div>
                        <label className="block text-xs font-bold uppercase tracking-widest mb-2"
                            style={{ color: '#f59e0b' }}>
                            Question <span style={{ color: '#ef4444' }}>*</span>
                        </label>
                        <textarea
                            id="math-question-input"
                            ref={textareaRef}
                            value={question}
                            onChange={e => setQuestion(e.target.value)}
                            onKeyDown={e => { if (e.key === 'Enter' && e.ctrlKey) handleSolve() }}
                            placeholder="Type or use the calculator pad below…&#10;e.g. Solve x² + 5x + 6 = 0"
                            rows={5}
                            className="w-full rounded-2xl px-5 py-4 text-sm leading-7 outline-none resize-none transition-all"
                            style={{
                                background: '#1a1228',
                                border: `1px solid ${question.trim().length >= 3 ? 'rgba(245,158,11,0.35)' : 'rgba(255,255,255,0.07)'}`,
                                color: '#fff',
                                caretColor: '#f59e0b',
                                scrollbarWidth: 'thin',
                            }}
                        />
                        <p className="text-right text-xs mt-1" style={{ color: 'rgba(255,255,255,0.2)' }}>
                            Ctrl+Enter to solve
                        </p>
                    </div>

                    {/* Calculator pad toggle */}
                    <div>
                        <button
                            id="math-pad-toggle"
                            onClick={() => setShowPad(p => !p)}
                            className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest mb-2 transition-opacity hover:opacity-100 opacity-70"
                            style={{ color: '#f59e0b' }}
                        >
                            <Calculator size={13} />
                            {showPad ? 'Hide' : 'Show'} Calculator Pad
                        </button>
                        <AnimatePresence>
                            {showPad && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    transition={{ duration: 0.25 }}
                                    style={{ overflow: 'hidden' }}
                                >
                                    <MathCalculatorInput
                                        textareaRef={textareaRef}
                                        value={question}
                                        onChange={setQuestion}
                                    />
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Validation hints */}
                    {!isValid && (question || questionNumber || marks) && (
                        <div className="flex items-start gap-2 rounded-xl px-4 py-3"
                            style={{ background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.12)' }}>
                            <AlertTriangle size={14} style={{ color: '#f59e0b', marginTop: 1, flexShrink: 0 }} />
                            <div className="text-xs space-y-1" style={{ color: 'rgba(255,255,255,0.5)' }}>
                                {!marks && <p>• Marks are required (controls solution depth)</p>}
                                {question.trim().length < 3 && <p>• Please enter your question</p>}
                            </div>
                        </div>
                    )}

                    {/* Error display */}
                    {error && (
                        <div className="rounded-xl px-4 py-3"
                            style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)' }}>
                            <p className="text-red-400 text-sm">⚠ {error}</p>
                        </div>
                    )}

                    {/* Solve button */}
                    <button
                        id="math-solve-btn"
                        onClick={handleSolve}
                        disabled={!isValid || loading}
                        className="flex items-center justify-center gap-3 py-4 rounded-2xl font-black text-base uppercase tracking-widest transition-all"
                        style={{
                            background: isValid && !loading
                                ? 'linear-gradient(135deg,#f59e0b,#ea580c)'
                                : 'rgba(255,255,255,0.05)',
                            color: isValid && !loading ? '#fff' : 'rgba(255,255,255,0.2)',
                            cursor: isValid && !loading ? 'pointer' : 'not-allowed',
                            boxShadow: isValid && !loading ? '0 0 30px rgba(245,158,11,0.35)' : 'none',
                            transform: isValid && !loading ? undefined : 'none',
                        }}
                    >
                        {loading ? (
                            <>
                                <div className="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                                Solving…
                            </>
                        ) : (
                            <>
                                <Send size={18} />
                                Solve Step-by-Step
                            </>
                        )}
                    </button>
                </div>

                {/* ── Right Panel: Solution ───────────────────────────────── */}
                <div className="hidden lg:flex flex-1 flex-col overflow-hidden p-5">
                    <AnimatePresence mode="wait">
                        {!solution && !loading && (
                            <motion.div
                                key="empty"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="flex-1 flex flex-col items-center justify-center text-center p-8"
                            >
                                {/* Decorative ring */}
                                <div className="relative w-32 h-32 mb-8">
                                    <div className="absolute inset-0 rounded-full"
                                        style={{
                                            background: 'radial-gradient(circle,rgba(245,158,11,0.12),transparent 70%)',
                                            animation: 'spin 8s linear infinite',
                                        }} />
                                    <div className="absolute inset-4 rounded-full"
                                        style={{
                                            background: 'rgba(245,158,11,0.06)',
                                            border: '1px dashed rgba(245,158,11,0.25)',
                                        }} />
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <Calculator size={40} style={{ color: 'rgba(245,158,11,0.4)' }} />
                                    </div>
                                </div>
                                <h2 className="text-2xl font-black mb-3" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                    Ready to Solve
                                </h2>
                                <p className="text-sm max-w-xs" style={{ color: 'rgba(255,255,255,0.25)' }}>
                                    Enter your question on the left with the marks, then click
                                    <span className="font-bold" style={{ color: 'rgba(245,158,11,0.5)' }}> Solve Step-by-Step</span>.
                                </p>
                                <div className="mt-8 grid grid-cols-3 gap-3 w-full max-w-sm">
                                    {[
                                        { icon: '①', label: 'Enter Question' },
                                        { icon: '②', label: 'Set Marks' },
                                        { icon: '③', label: 'Get Steps + Hints' },
                                    ].map((item, i) => (
                                        <div key={i} className="rounded-2xl p-4 text-center"
                                            style={{ background: 'rgba(245,158,11,0.04)', border: '1px solid rgba(245,158,11,0.08)' }}>
                                            <p className="text-2xl mb-1" style={{ color: 'rgba(245,158,11,0.5)' }}>{item.icon}</p>
                                            <p className="text-xs" style={{ color: 'rgba(255,255,255,0.3)' }}>{item.label}</p>
                                        </div>
                                    ))}
                                </div>
                            </motion.div>
                        )}

                        {loading && (
                            <motion.div
                                key="loading"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="flex-1 flex flex-col items-center justify-center gap-6"
                            >
                                <div className="relative w-20 h-20">
                                    <div className="absolute inset-0 rounded-full border-2 border-amber-400/20 border-t-amber-400 animate-spin" />
                                    <div className="absolute inset-3 rounded-full border border-orange-500/20 border-b-orange-500 animate-spin" style={{ animationDirection: 'reverse', animationDuration: '0.8s' }} />
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <Calculator size={24} style={{ color: '#f59e0b' }} />
                                    </div>
                                </div>
                                <div className="text-center">
                                    <p className="font-bold text-lg" style={{ color: '#fff' }}>Solving…</p>
                                    <p className="text-sm mt-1" style={{ color: 'rgba(255,255,255,0.35)' }}>
                                        Generating mark-scheme quality steps
                                    </p>
                                </div>
                            </motion.div>
                        )}

                        {solution && !loading && (
                            <motion.div
                                key="solution"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0 }}
                                className="flex-1 flex flex-col overflow-hidden"
                            >
                                <MathSolutionViewer solution={solution} />
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>

            {/* ── Mobile Solution (below input on small screens) ─────────── */}
            {(solution || loading) && (
                <div className="lg:hidden border-t p-5"
                    style={{ borderColor: 'rgba(245,158,11,0.1)' }}>
                    {loading ? (
                        <div className="flex items-center justify-center gap-3 py-8">
                            <div className="w-8 h-8 rounded-full border-2 border-t-amber-400 border-amber-400/20 animate-spin" />
                            <p style={{ color: 'rgba(255,255,255,0.5)' }}>Solving…</p>
                        </div>
                    ) : (
                        <MathSolutionViewer solution={solution} />
                    )}
                </div>
            )}
        </div>
    )
}
