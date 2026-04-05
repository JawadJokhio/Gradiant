import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { BrainCircuit, ChevronLeft, Target, Lightbulb, BarChart3, Loader2, Sparkles, TrendingUp, AlertCircle, ArrowLeft } from 'lucide-react'

export default function WeaknessAnalysis({ onBack }) {
    const [analysis, setAnalysis] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchAnalysis()
    }, [])

    const fetchAnalysis = async () => {
        try {
            const response = await fetch('http://localhost:8000/analyze-weakness')
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
                <p className="text-[var(--primary-purple)] font-black uppercase tracking-[0.3em] text-xs mt-8 animate-pulse">Synchronizing Neural Data...</p>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-[var(--bg-cream)] text-[var(--text-dark)] p-6 md:p-12 lg:p-20 transition-colors duration-500">
            <div className="max-w-6xl mx-auto space-y-16">
                <button
                    onClick={onBack}
                    className="flex items-center text-[var(--primary-purple)] font-black uppercase tracking-[0.2em] text-xs group"
                >
                    <ArrowLeft size={18} className="mr-2 group-hover:-translate-x-1 transition-transform" />
                    Return to Hub
                </button>

                <header className="flex flex-col md:flex-row md:items-end justify-between gap-8">
                    <div className="space-y-6">
                        <div className="flex items-center gap-4">
                            <div className="w-16 h-16 rounded-[1.5rem] bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] flex items-center justify-center shadow-2xl shadow-purple-900/20">
                                <BrainCircuit size={32} />
                            </div>
                            <div className="h-10 w-[1px] bg-[var(--border-color)]"></div>
                            <div className="px-4 py-1.5 rounded-full bg-[var(--accent-gold)]/10 text-[var(--accent-gold)] text-[10px] font-black uppercase tracking-widest border border-[var(--accent-gold)]/20">
                                AI Diagnostic active
                            </div>
                        </div>
                        <div>
                            <h1 className="text-5xl md:text-7xl font-black text-[var(--primary-purple)] tracking-tighter">Weakness Analysis</h1>
                            <p className="text-[var(--text-muted)] text-xl font-medium mt-4 max-w-2xl leading-relaxed">
                                Intelligence-driven insights derived from your granular interaction with marking schemes.
                            </p>
                        </div>
                    </div>

                    <div className="hidden lg:block">
                        <div className="bg-[var(--bg-card)] p-6 rounded-[2.5rem] border border-[var(--border-color)] shadow-xl shadow-purple-900/5 dark:shadow-black/20 flex items-center gap-6 transition-colors duration-500">
                            <div className="w-12 h-12 rounded-2xl bg-emerald-50 dark:bg-emerald-900/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                                <TrendingUp size={24} />
                            </div>
                            <div>
                                <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)]">Study Efficiency</p>
                                <p className="text-2xl font-black text-[var(--primary-purple)]">Optimized</p>
                            </div>
                        </div>
                    </div>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                    {/* Weak Areas Card */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="lg:col-span-5 bg-[var(--bg-card)] p-10 rounded-[3rem] border border-[var(--border-color)] shadow-2xl shadow-purple-900/5 dark:shadow-black/20 space-y-10 relative overflow-hidden transition-colors duration-500"
                    >
                        <div className="absolute top-0 right-0 p-10 opacity-5 text-[var(--primary-purple)]">
                            <Target size={150} />
                        </div>

                        <div className="flex items-center gap-4 text-[var(--accent-gold)] relative z-10">
                            <div className="p-3 bg-[var(--accent-gold)]/10 rounded-2xl">
                                <Target size={28} />
                            </div>
                            <h2 className="text-2xl font-black uppercase tracking-tighter text-[var(--primary-purple)]">Identified Blind Spots</h2>
                        </div>

                        <div className="space-y-6 relative z-10">
                            {analysis?.weak_areas.map((area, idx) => (
                                <div key={idx} className="group flex items-start gap-5 p-6 bg-[var(--primary-purple-light)]/5 rounded-[2rem] border border-transparent hover:border-[var(--primary-purple-light)]/20 transition-all">
                                    <div className="w-10 h-10 rounded-2xl bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] text-sm font-black flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
                                        {idx + 1}
                                    </div>
                                    <p className="font-bold text-[var(--text-dark)] text-lg leading-tight mt-1">{area}</p>
                                </div>
                            ))}
                        </div>
                    </motion.div>

                    {/* Improvement Plan Card */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="lg:col-span-7 bg-[var(--primary-purple)] p-10 md:p-14 rounded-[4rem] text-white dark:text-[#0f0a1e] shadow-2xl shadow-purple-900/30 dark:shadow-black/40 space-y-10 relative overflow-hidden flex flex-col"
                    >
                        <div className="absolute -bottom-20 -right-20 w-80 h-80 bg-white/10 dark:bg-black/10 rounded-full blur-3xl"></div>

                        <div className="flex items-center gap-4 relative z-10">
                            <div className="p-3 bg-white/10 dark:bg-black/10 rounded-2xl backdrop-blur-xl">
                                <Lightbulb size={28} className="text-[var(--accent-gold)]" />
                            </div>
                            <h2 className="text-2xl font-black uppercase tracking-[0.1em]">Strategic Action Plan</h2>
                        </div>

                        <div className="flex-1 space-y-8 font-medium text-purple-50/90 dark:text-[#0f0a1e]/80 leading-relaxed text-lg italic relative z-10">
                            {analysis?.improvement_plan.split('\n').map((line, i) => (
                                <p key={i}>{line}</p>
                            ))}
                        </div>

                        <div className="pt-10 flex flex-wrap items-center gap-6 relative z-10 border-t border-white/10 dark:border-black/10">
                            <div className="flex items-center gap-3">
                                <BarChart3 size={20} className="text-[var(--accent-gold)]" />
                                <p className="text-[10px] font-black uppercase tracking-[0.2em] opacity-60">Priority Factor: High</p>
                            </div>
                            <div className="flex items-center gap-3">
                                <Sparkles size={20} className="text-emerald-400 dark:text-emerald-900" />
                                <p className="text-[10px] font-black uppercase tracking-[0.2em] opacity-60">AI Confidence: 94%</p>
                            </div>
                        </div>
                    </motion.div>
                </div>

                {/* Summary Section */}
                <motion.section
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-[var(--bg-card)] border-2 border-[var(--primary-purple-light)]/10 p-10 md:p-16 rounded-[4rem] shadow-xl shadow-purple-900/5 dark:shadow-black/20 relative overflow-hidden transition-colors duration-500"
                >
                    <div className="max-w-4xl space-y-8 relative z-10">
                        <div className="flex items-center gap-3 text-[var(--primary-purple)]">
                            <AlertCircle size={24} />
                            <h2 className="text-sm font-black uppercase tracking-[0.4em]">Executive Summary</h2>
                        </div>
                        <h3 className="text-3xl md:text-4xl font-black text-[var(--primary-purple)] leading-tight">
                            Overall Performance Trajectory
                        </h3>
                        <p className="text-xl text-[var(--text-muted)] font-medium leading-relaxed italic border-l-4 border-[var(--accent-gold)] pl-10 py-2">
                            {analysis?.summary}
                        </p>
                        <div className="pt-6">
                            <button
                                onClick={() => window.location.reload()}
                                className="bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] px-10 py-4 rounded-2xl font-black uppercase tracking-widest hover:scale-105 transition-all shadow-xl shadow-purple-900/20 dark:shadow-black/40 active:scale-95 flex items-center gap-3"
                            >
                                <Loader2 size={20} className="animate-spin" />
                                Re-sync Analysis
                            </button>
                        </div>
                    </div>
                </motion.section>
            </div>
        </div>
    )
}
