import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, AlertCircle, Star, Info } from 'lucide-react'
import ConceptModal from './ConceptModal'

// Lazy-load KaTeX CSS once
let katexLoaded = false
function ensureKatex() {
    if (katexLoaded) return
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.css'
    document.head.appendChild(link)
    katexLoaded = true
}

/**
 * Renders a math expression string using KaTeX if possible,
 * otherwise falls back to styled plain text.
 */
function MathExpression({ expr }) {
    const ref = useRef(null)

    useEffect(() => {
        ensureKatex()
        if (!ref.current || !expr) return

        import('katex').then(({ default: katex }) => {
            try {
                // Convert common Unicode math to LaTeX
                const latex = expr
                    .replace(/²/g, '^{2}')
                    .replace(/³/g, '^{3}')
                    .replace(/√\(/g, '\\sqrt{')
                    .replace(/√(\S+)/g, '\\sqrt{$1}')
                    .replace(/π/g, '\\pi')
                    .replace(/×/g, '\\times')
                    .replace(/÷/g, '\\div')
                    .replace(/−/g, '-')
                    .replace(/≠/g, '\\neq')
                    .replace(/≤/g, '\\leq')
                    .replace(/≥/g, '\\geq')
                    .replace(/°/g, '^{\\circ}')
                    .replace(/\^(\S+)/g, '^{$1}')

                katex.render(latex, ref.current, {
                    throwOnError: false,
                    displayMode: false,
                    output: 'html',
                })
            } catch {
                if (ref.current) ref.current.textContent = expr
            }
        }).catch(() => {
            if (ref.current) ref.current.textContent = expr
        })
    }, [expr])

    return (
        <span
            ref={ref}
            className="font-mono text-sm"
            style={{ color: '#fbbf24' }}
        >
            {expr}
        </span>
    )
}

/**
 * Single step card with concept hint button
 */
function StepCard({ step, index, onConceptClick }) {
    const hasHint = !!step.concept_key

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.08, duration: 0.35 }}
            className="relative flex gap-4"
        >
            {/* Timeline line */}
            <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-xl flex items-center justify-center text-xs font-black shrink-0 z-10"
                    style={{
                        background: 'linear-gradient(135deg,#f59e0b,#ea580c)',
                        color: '#fff',
                        boxShadow: '0 0 14px rgba(245,158,11,0.4)',
                    }}>
                    {step.step_number}
                </div>
                <div className="flex-1 w-px mt-1" style={{ background: 'rgba(245,158,11,0.12)' }} />
            </div>

            {/* Card */}
            <div className="flex-1 rounded-2xl p-4 mb-4"
                style={{
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(245,158,11,0.1)',
                    borderLeft: '3px solid rgba(245,158,11,0.45)',
                }}>
                {/* Description row */}
                <div className="flex items-start justify-between gap-2 mb-2">
                    <p className="text-sm font-semibold leading-snug" style={{ color: 'rgba(255,255,255,0.75)' }}>
                        {step.description}
                    </p>
                    {hasHint && (
                        <button
                            id={`hint-btn-step-${step.step_number}`}
                            onClick={() => onConceptClick(step.concept_key)}
                            title={`Learn: ${step.concept_key.replace(/_/g, ' ')}`}
                            className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-black transition-all hover:scale-110 active:scale-90"
                            style={{
                                background: 'linear-gradient(135deg,#f59e0b,#ea580c)',
                                color: '#fff',
                                boxShadow: '0 0 8px rgba(245,158,11,0.5)',
                                animation: 'pulse-glow 2s ease-in-out infinite',
                            }}
                        >
                            !
                        </button>
                    )}
                </div>

                {/* Math expression */}
                {step.expression && (
                    <div className="mt-2 px-3 py-2 rounded-xl"
                        style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(245,158,11,0.08)' }}>
                        <MathExpression expr={step.expression} />
                    </div>
                )}

                {/* Concept tag */}
                {hasHint && (
                    <button
                        onClick={() => onConceptClick(step.concept_key)}
                        className="mt-2 flex items-center gap-1 text-xs font-medium transition-opacity hover:opacity-100 opacity-60"
                        style={{ color: '#f59e0b' }}
                    >
                        <Info size={11} />
                        {step.concept_key.replace(/_/g, ' ')}
                    </button>
                )}
            </div>
        </motion.div>
    )
}

/**
 * MathSolutionViewer
 * Props:
 *   solution — object returned by /api/math/solve
 */
export default function MathSolutionViewer({ solution }) {
    const [activeConceptKey, setActiveConceptKey] = useState(null)

    if (!solution) return null

    const { steps = [], final_answer, mark_commentary, question_number, marks, raw_question } = solution

    return (
        <div className="h-full flex flex-col">
            {/* Solution header */}
            <motion.div
                initial={{ opacity: 0, y: -12 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-5 rounded-2xl p-4"
                style={{
                    background: 'linear-gradient(135deg,rgba(245,158,11,0.08),rgba(234,88,12,0.06))',
                    border: '1px solid rgba(245,158,11,0.18)',
                }}
            >
                <div className="flex items-start justify-between gap-3 flex-wrap">
                    <div>
                        <p className="text-xs font-bold uppercase tracking-widest mb-1" style={{ color: '#f59e0b' }}>
                            Question {question_number} · {marks} Mark{marks !== 1 ? 's' : ''}
                        </p>
                        <p className="text-sm" style={{ color: 'rgba(255,255,255,0.65)' }}>
                            {raw_question?.length > 120 ? raw_question.slice(0, 120) + '…' : raw_question}
                        </p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                        <Star size={14} style={{ color: '#f59e0b' }} />
                        <span className="text-xs font-semibold" style={{ color: '#f59e0b' }}>
                            {steps.length} step{steps.length !== 1 ? 's' : ''}
                        </span>
                    </div>
                </div>
                {mark_commentary && (
                    <p className="mt-2 text-xs" style={{ color: 'rgba(255,255,255,0.4)' }}>
                        📝 {mark_commentary}
                    </p>
                )}
            </motion.div>

            {/* Steps */}
            <div className="flex-1 overflow-y-auto pr-1" style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(245,158,11,0.2) transparent' }}>
                {steps.map((step, i) => (
                    <StepCard
                        key={step.step_number}
                        step={step}
                        index={i}
                        onConceptClick={(key) => setActiveConceptKey(key)}
                    />
                ))}

                {/* Final answer card */}
                {final_answer && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: steps.length * 0.08 + 0.1 }}
                        className="mt-2 rounded-2xl p-5 flex items-center gap-4"
                        style={{
                            background: 'linear-gradient(135deg,rgba(245,158,11,0.12),rgba(234,88,12,0.08))',
                            border: '2px solid rgba(245,158,11,0.3)',
                            boxShadow: '0 0 30px rgba(245,158,11,0.1)',
                        }}
                    >
                        <div className="w-10 h-10 rounded-xl shrink-0 flex items-center justify-center"
                            style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>
                            <CheckCircle size={20} className="text-white" />
                        </div>
                        <div>
                            <p className="text-xs font-bold uppercase tracking-widest mb-1" style={{ color: '#f59e0b' }}>
                                Final Answer
                            </p>
                            <MathExpression expr={final_answer} />
                        </div>
                    </motion.div>
                )}

                {/* Hint legend */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6 }}
                    className="mt-6 mb-2 flex items-center gap-2"
                >
                    <div className="w-5 h-5 rounded-full flex items-center justify-center text-xs font-black"
                        style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)', color: '#fff' }}>
                        !
                    </div>
                    <p className="text-xs" style={{ color: 'rgba(255,255,255,0.3)' }}>
                        Tap the orange <b>!</b> on any step to learn that concept in detail
                    </p>
                </motion.div>
            </div>

            {/* Concept Modal */}
            {activeConceptKey && (
                <ConceptModal
                    conceptKey={activeConceptKey}
                    onClose={() => setActiveConceptKey(null)}
                />
            )}

            <style>{`
                @keyframes pulse-glow {
                    0%, 100% { box-shadow: 0 0 8px rgba(245,158,11,0.5); }
                    50% { box-shadow: 0 0 16px rgba(245,158,11,0.9); }
                }
            `}</style>
        </div>
    )
}
