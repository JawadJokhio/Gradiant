import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    BrainCircuit, Target, Lightbulb, BarChart3, Loader2,
    Sparkles, TrendingUp, AlertCircle, ArrowLeft, BookOpen,
    HelpCircle, Flame, CheckCircle2
} from 'lucide-react'
import { sessionId } from './SessionTracker'

export default function WeaknessAnalysis({ onBack }) {
    const [analysis, setAnalysis] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchAnalysis()
    }, [])

    const fetchAnalysis = async () => {
        try {
            setLoading(true)
            const response = await fetch('http://localhost:8000/analyze-weakness', {
                headers: {
                    'X-Session-ID': sessionId
                }
            })
            const data = await response.json()
            setAnalysis(data)
        } catch (error) {
            console.error("Error fetching analysis:", error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-[var(--bg-cream)] flex flex-col items-center justify-center p-8 transition-colors duration-500">
                <div className="relative">
                    <div className="w-24 h-24 rounded-[2rem] bg-[var(--primary-purple-light)]/10 flex items-center justify-center animate-pulse">
                        <BrainCircuit size={48} className="text-[var(--primary-purple)]" />
                    </div>
                    <div className="absolute -top-2 -right-2">
                        <Loader2 size={32} className="text-[var(--accent-gold)] animate-spin" />
                    </div>
                </div>
                <p className="text-[var(--primary-purple)] font-black uppercase tracking-[0.3em] text-xs mt-8 animate-pulse">
                    Synchronizing Neural Performance Diagnostics...
                </p>
            </div>
        )
    }

    const readinessScore = analysis?.overall_readiness_score ?? 50
    const weakAreas = analysis?.weak_areas || []
    const practiceQuestions = analysis?.practice_questions || []

    return (
        <div className="min-h-screen bg-[var(--bg-cream)] text-[var(--text-dark)] p-6 md:p-12 lg:p-20 transition-colors duration-500">
            <div className="max-w-6xl mx-auto space-y-14">
                <button
                    onClick={onBack}
                    className="flex items-center text-[var(--primary-purple)] font-black uppercase tracking-[0.2em] text-xs group"
                >
                    <ArrowLeft size={18} className="mr-2 group-hover:-translate-x-1 transition-transform" />
                    Return to Hub
                </button>

                {/* Header */}
                <header className="flex flex-col md:flex-row md:items-end justify-between gap-8">
                    <div className="space-y-5">
                        <div className="flex items-center gap-4">
                            <div className="w-16 h-16 rounded-[1.5rem] bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] flex items-center justify-center shadow-2xl shadow-purple-900/20">
                                <BrainCircuit size={32} />
                            </div>
                            <div className="h-10 w-[1px] bg-[var(--border-color)]"></div>
                            <div className="px-4 py-1.5 rounded-full bg-[var(--accent-gold)]/10 text-[var(--accent-gold)] text-[10px] font-black uppercase tracking-widest border border-[var(--accent-gold)]/20">
                                AI Diagnostic Active
                            </div>
                        </div>
                        <div>
                            <h1 className="text-4xl md:text-6xl font-black text-[var(--primary-purple)] tracking-tighter">
                                Weakness Analysis
                            </h1>
                            <p className="text-[var(--text-muted)] text-lg md:text-xl font-medium mt-3 max-w-2xl leading-relaxed">
                                Continuous diagnostic engine powered by Cambridge mark schemes, exam auditor feedback, and spaced repetition decay.
                            </p>
                        </div>
                    </div>

                    {/* Readiness Gauge Card */}
                    <div className="bg-[var(--bg-card)] p-6 rounded-[2.5rem] border border-[var(--border-color)] shadow-xl shadow-purple-900/5 dark:shadow-black/20 flex items-center gap-6 transition-colors duration-500">
                        <div className="w-16 h-16 rounded-2xl bg-emerald-50 dark:bg-emerald-900/10 text-emerald-600 dark:text-emerald-400 flex flex-col items-center justify-center">
                            <span className="text-xl font-black">{Math.round(readinessScore)}%</span>
                        </div>
                        <div>
                            <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)]">Exam Readiness</p>
                            <p className="text-base font-black text-[var(--primary-purple)]">
                                {readinessScore >= 75 ? 'Distinction Pace' : readinessScore >= 50 ? 'Steady Progress' : 'Needs Reinforcement'}
                            </p>
                            <span className="text-xs text-[var(--text-muted)]">
                                {analysis?.total_interactions ?? 0} tracked sessions
                            </span>
                        </div>
                    </div>
                </header>

                {/* Study Suggestion Alert Banner */}
                {analysis?.study_session_suggestion && (
                    <div className="p-6 rounded-[2rem] bg-gradient-to-r from-[var(--primary-purple)]/10 via-[var(--accent-gold)]/10 to-transparent border border-[var(--primary-purple-light)]/20 flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-[var(--primary-purple)] text-white flex items-center justify-center shrink-0 shadow-lg">
                            <Flame size={24} className="text-[var(--accent-gold)]" />
                        </div>
                        <div>
                            <p className="text-[10px] font-black uppercase tracking-widest text-[var(--accent-gold)]">Recommended Daily Objective</p>
                            <p className="text-lg font-bold text-[var(--primary-purple)]">{analysis.study_session_suggestion}</p>
                        </div>
                    </div>
                )}

                {/* Main 2-Column Section */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                    {/* Weak Areas Card */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="lg:col-span-5 bg-[var(--bg-card)] p-8 md:p-10 rounded-[3rem] border border-[var(--border-color)] shadow-2xl shadow-purple-900/5 dark:shadow-black/20 space-y-8 relative overflow-hidden transition-colors duration-500"
                    >
                        <div className="flex items-center gap-4 text-[var(--accent-gold)] relative z-10">
                            <div className="p-3 bg-[var(--accent-gold)]/10 rounded-2xl">
                                <Target size={28} />
                            </div>
                            <div>
                                <h2 className="text-2xl font-black uppercase tracking-tighter text-[var(--primary-purple)]">
                                    Identified Weak Areas
                                </h2>
                                <p className="text-xs text-[var(--text-muted)]">Topics requiring focused revision</p>
                            </div>
                        </div>

                        <div className="space-y-4 relative z-10">
                            {weakAreas.length === 0 ? (
                                <div className="p-8 text-center text-[var(--text-muted)] bg-[var(--primary-purple-light)]/5 rounded-3xl">
                                    <CheckCircle2 size={36} className="mx-auto text-emerald-500 mb-3" />
                                    <p className="font-bold text-sm">No critical weak areas detected yet!</p>
                                    <p className="text-xs mt-1">Keep solving past paper questions to train the diagnostic engine.</p>
                                </div>
                            ) : (
                                weakAreas.map((area, idx) => {
                                    const name = typeof area === 'string' ? area : area.display_name || area.topic;
                                    const score = typeof area === 'object' && area.weakness_score != null ? Math.round(area.weakness_score * 100) : 70;
                                    const subject = typeof area === 'object' ? area.subject : 'General';
                                    const attempts = typeof area === 'object' ? area.attempts : null;

                                    return (
                                        <div
                                            key={idx}
                                            className="p-5 bg-[var(--primary-purple-light)]/5 rounded-[1.8rem] border border-[var(--border-color)] hover:border-[var(--primary-purple-light)]/30 transition-all space-y-3"
                                        >
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    <span className="w-8 h-8 rounded-xl bg-[var(--primary-purple)] text-white text-xs font-black flex items-center justify-center shrink-0">
                                                        {idx + 1}
                                                    </span>
                                                    <div>
                                                        <p className="font-bold text-[var(--text-dark)] text-base leading-tight">{name}</p>
                                                        <span className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)]">
                                                            {subject} {attempts ? `• ${attempts} attempts` : ''}
                                                        </span>
                                                    </div>
                                                </div>
                                                <span className="text-xs font-black text-rose-500 bg-rose-500/10 px-2.5 py-1 rounded-full">
                                                    {score}% error rate
                                                </span>
                                            </div>

                                            {/* Progress bar */}
                                            <div className="w-full bg-[var(--border-color)]/30 h-2 rounded-full overflow-hidden">
                                                <div
                                                    className="bg-gradient-to-r from-amber-500 to-rose-500 h-full rounded-full transition-all duration-700"
                                                    style={{ width: `${Math.min(100, Math.max(15, score))}%` }}
                                                />
                                            </div>
                                        </div>
                                    )
                                })
                            )}
                        </div>
                    </motion.div>

                    {/* Improvement Plan Card */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="lg:col-span-7 bg-[var(--primary-purple)] p-8 md:p-12 rounded-[3.5rem] text-white dark:text-[#0f0a1e] shadow-2xl shadow-purple-900/30 dark:shadow-black/40 space-y-8 relative overflow-hidden flex flex-col"
                    >
                        <div className="absolute -bottom-20 -right-20 w-80 h-80 bg-white/10 dark:bg-black/10 rounded-full blur-3xl"></div>

                        <div className="flex items-center gap-4 relative z-10">
                            <div className="p-3 bg-white/10 dark:bg-black/10 rounded-2xl backdrop-blur-xl">
                                <Lightbulb size={28} className="text-[var(--accent-gold)]" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-black uppercase tracking-[0.1em]">Strategic Action Plan</h2>
                                <p className="text-xs text-purple-200 dark:text-purple-950/70">7-Day Personalized Cambridge Syllabus Protocol</p>
                            </div>
                        </div>

                        <div className="flex-1 space-y-5 font-medium text-purple-50/90 dark:text-[#0f0a1e]/90 leading-relaxed text-base relative z-10">
                            {analysis?.improvement_plan ? (
                                analysis.improvement_plan.split('\n').filter(Boolean).map((line, i) => (
                                    <p key={i} className="leading-relaxed">{line}</p>
                                ))
                            ) : (
                                <p className="italic">Begin practicing with exam questions to unlock your custom revision roadmap.</p>
                            )}
                        </div>

                        <div className="pt-6 flex flex-wrap items-center gap-6 relative z-10 border-t border-white/10 dark:border-black/10 text-xs">
                            <div className="flex items-center gap-2">
                                <BarChart3 size={18} className="text-[var(--accent-gold)]" />
                                <span className="font-black uppercase tracking-widest opacity-80">Priority: High</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Sparkles size={18} className="text-emerald-400 dark:text-emerald-800" />
                                <span className="font-black uppercase tracking-widest opacity-80">Mark-Scheme Aligned</span>
                            </div>
                        </div>
                    </motion.div>
                </div>

                {/* Practice Questions Recommendation Section */}
                {practiceQuestions.length > 0 && (
                    <motion.section
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-6"
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="p-3 bg-[var(--accent-gold)]/10 text-[var(--accent-gold)] rounded-2xl">
                                    <BookOpen size={24} />
                                </div>
                                <div>
                                    <h3 className="text-2xl md:text-3xl font-black text-[var(--primary-purple)]">
                                        Recommended Practice Questions
                                    </h3>
                                    <p className="text-xs text-[var(--text-muted)]">
                                        Curated from Cambridge Past Papers to reinforce your vulnerable topics
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {practiceQuestions.map((q, idx) => (
                                <div
                                    key={q.question_id || idx}
                                    className="p-6 rounded-[2.5rem] bg-[var(--bg-card)] border border-[var(--border-color)] shadow-xl shadow-purple-900/5 space-y-4 hover:border-[var(--primary-purple-light)]/40 transition-all flex flex-col justify-between"
                                >
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between gap-2">
                                            <span className="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest bg-[var(--primary-purple)]/10 text-[var(--primary-purple)] border border-[var(--primary-purple)]/20">
                                                {q.subject} • {q.marks} Marks
                                            </span>
                                            {q.year && (
                                                <span className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)]">
                                                    Paper {q.year}
                                                </span>
                                            )}
                                        </div>

                                        <p className="text-base font-bold text-[var(--text-dark)] leading-snug">
                                            {q.question_text}
                                        </p>
                                    </div>

                                    <div className="pt-3 border-t border-[var(--border-color)]">
                                        <p className="text-xs text-[var(--accent-gold)] font-medium flex items-center gap-1.5">
                                            <Sparkles size={14} className="shrink-0" />
                                            {q.why_recommended}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </motion.section>
                )}

                {/* Summary Section */}
                <motion.section
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-[var(--bg-card)] border-2 border-[var(--primary-purple-light)]/10 p-8 md:p-14 rounded-[3.5rem] shadow-xl shadow-purple-900/5 dark:shadow-black/20 space-y-6 transition-colors duration-500"
                >
                    <div className="flex items-center gap-3 text-[var(--primary-purple)]">
                        <AlertCircle size={24} />
                        <h2 className="text-xs font-black uppercase tracking-[0.3em]">Executive Summary</h2>
                    </div>
                    <h3 className="text-2xl md:text-3xl font-black text-[var(--primary-purple)] leading-tight">
                        Overall Performance Trajectory
                    </h3>
                    <p className="text-lg text-[var(--text-muted)] font-medium leading-relaxed italic border-l-4 border-[var(--accent-gold)] pl-6 py-2">
                        {analysis?.summary || 'Complete study sessions to generate your comprehensive performance summary.'}
                    </p>
                    <div className="pt-2">
                        <button
                            onClick={fetchAnalysis}
                            className="bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] px-8 py-3.5 rounded-2xl font-black uppercase tracking-widest hover:scale-105 transition-all shadow-xl shadow-purple-900/20 active:scale-95 flex items-center gap-3 text-xs"
                        >
                            <Loader2 size={16} className={loading ? "animate-spin" : ""} />
                            Re-sync Diagnostics
                        </button>
                    </div>
                </motion.section>
            </div>
        </div>
    )
}
