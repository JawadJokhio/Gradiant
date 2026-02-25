import { motion } from 'framer-motion'
import { Camera, MessageSquare, Globe, ArrowLeft, BookOpen, Layers, Info, BrainCircuit, Search, ChevronRight } from 'lucide-react'

export default function SubjectHub({ subject, onSelectMode, onBack }) {
    return (
        <div className="min-h-screen bg-[var(--bg-cream)] text-[var(--text-dark)] p-6 md:p-12 transition-colors duration-500">
            <div className="max-w-5xl mx-auto space-y-12">
                <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <button
                        onClick={onBack}
                        className="flex items-center text-[var(--primary-purple)] font-black uppercase tracking-widest text-sm group w-fit"
                    >
                        <ArrowLeft size={20} className="mr-2 group-hover:-translate-x-1 transition-transform" />
                        Back to Dashboard
                    </button>

                    <div className="text-left md:text-right">
                        <div className={`inline-block px-4 py-1 rounded-full bg-[var(--primary-purple-light)]/10 text-[var(--primary-purple)] text-[10px] font-black uppercase tracking-widest mb-3 border border-[var(--primary-purple-light)]/20`}>
                            {subject.name} Module
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black text-[var(--primary-purple)] tracking-tighter">{subject.name} Study Hub</h1>
                    </div>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Vision Scanner Card */}
                    <motion.button
                        whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)' }}
                        onClick={() => onSelectMode('vision')}
                        className="group relative overflow-hidden p-8 rounded-[2.5rem] bg-[var(--bg-card)] border border-[var(--border-color)] transition-all text-left flex flex-col gap-6 shadow-xl shadow-purple-900/5 dark:shadow-black/20"
                    >
                        <div className="w-16 h-16 rounded-2xl bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                            <Camera size={32} />
                        </div>
                        <div>
                            <h3 className="text-2xl font-black text-[var(--primary-purple)] mb-2">Vision Scanner</h3>
                            <p className="text-[var(--text-muted)] font-medium leading-relaxed">
                                Upload pictures of your {subject.name} past papers for instant, marking-scheme-aligned solutions and examiner analysis.
                            </p>
                        </div>
                        <div className="mt-auto flex items-center gap-2 text-xs font-black text-[var(--primary-purple)] uppercase tracking-widest">
                            Start Scanning <ChevronRight size={18} />
                        </div>
                    </motion.button>

                    {/* Text Explainer Card */}
                    <motion.button
                        whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)' }}
                        onClick={() => onSelectMode('text')}
                        className="group relative overflow-hidden p-8 rounded-[2.5rem] bg-[var(--bg-card)] border border-[var(--border-color)] transition-all text-left flex flex-col gap-6 shadow-xl shadow-purple-900/5 dark:shadow-black/20"
                    >
                        <div className="w-16 h-16 rounded-2xl bg-blue-600 text-white flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                            <MessageSquare size={32} />
                        </div>
                        <div>
                            <h3 className="text-2xl font-black text-[var(--primary-purple)] mb-2">Concept Explainer</h3>
                            <p className="text-[var(--text-muted)] font-medium leading-relaxed">
                                Ask any theoretical or conceptual question about {subject.name} and get precise, exam-focused explanations.
                            </p>
                        </div>
                        <div className="mt-auto flex items-center gap-2 text-xs font-black text-blue-600 uppercase tracking-widest">
                            Ask AI Examiner <ChevronRight size={18} />
                        </div>
                    </motion.button>

                    {/* Paper Repository Card */}
                    <motion.button
                        whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)' }}
                        onClick={() => onSelectMode('papers')}
                        className="group relative overflow-hidden p-8 rounded-[2.5rem] bg-[var(--bg-card)] border border-[var(--border-color)] transition-all text-left flex flex-col gap-6 shadow-xl shadow-purple-900/5 dark:shadow-black/20"
                    >
                        <div className="w-16 h-16 rounded-2xl bg-[var(--accent-gold)] text-white dark:text-[#0f0a1e] flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                            <Search size={32} />
                        </div>
                        <div>
                            <h3 className="text-2xl font-black text-[var(--primary-purple)] mb-2">Past Paper Repository</h3>
                            <p className="text-[var(--text-muted)] font-medium leading-relaxed">
                                Browse through yearly and topical past papers for {subject.name} with official Cambridge marking schemes.
                            </p>
                        </div>
                        <div className="mt-auto flex items-center gap-2 text-xs font-black text-[var(--accent-gold)] uppercase tracking-widest">
                            Browse Collection <ChevronRight size={18} />
                        </div>
                    </motion.button>

                    {/* Weakness Diagnostic Card */}
                    <motion.button
                        whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(0, 0, 0, 0.2)' }}
                        onClick={() => onSelectMode('weakness')}
                        className="group relative overflow-hidden p-8 rounded-[2.5rem] bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] transition-all text-left flex flex-col gap-6 shadow-xl shadow-purple-900/20"
                    >
                        <div className="w-16 h-16 rounded-2xl bg-[var(--bg-card)] text-[var(--primary-purple)] flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                            <BrainCircuit size={32} />
                        </div>
                        <div>
                            <h3 className="text-2xl font-black mb-2 text-white">Weakness Diagnostic</h3>
                            <p className="opacity-80 font-medium leading-relaxed">
                                Let AI analyze your recent {subject.name} practice sessions to identify exact topics you need to focus on.
                            </p>
                        </div>
                        <div className="mt-auto flex items-center gap-2 text-xs font-black uppercase tracking-widest">
                            Run Analysis <ChevronRight size={18} />
                        </div>
                    </motion.button>

                    {subject.id === 'geography' && (
                        <motion.button
                            whileHover={{ scale: 1.01, boxShadow: '0 20px 40px rgba(16, 185, 129, 0.1)' }}
                            onClick={() => onSelectMode('geography')}
                            className="md:col-span-2 group relative overflow-hidden p-8 rounded-[2.5rem] bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-100 dark:border-emerald-900/20 transition-all text-left flex flex-col sm:flex-row sm:items-center justify-between gap-8 shadow-sm"
                        >
                            <div className="flex gap-6 items-center">
                                <div className="w-20 h-20 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shadow-xl group-hover:rotate-6 transition-transform">
                                    <Globe size={40} />
                                </div>
                                <div className="space-y-2">
                                    <h3 className="text-3xl font-black text-[var(--primary-purple)]">Interactive GIS Map</h3>
                                    <p className="text-[var(--text-muted)] font-medium max-w-xl">
                                        Advanced GIS terminal for physical and human geography of Pakistan. Analyze energy, forests, and infrastructure layers.
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2 text-sm font-black uppercase tracking-widest bg-emerald-600 text-white px-8 py-4 rounded-2xl shadow-xl shadow-emerald-900/20 whitespace-nowrap">
                                Launch GIS Engine <ChevronRight size={20} />
                            </div>
                        </motion.button>
                    )}
                </div>

                <footer className="pt-12 border-t border-[var(--border-color)] flex flex-col sm:flex-row items-center justify-between gap-6 opacity-60">
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2">
                            <BookOpen size={16} className="text-[var(--primary-purple)]" />
                            <span className="text-[10px] font-black uppercase tracking-widest">Academic Excellence 2026</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Layers size={16} className="text-[var(--accent-gold)]" />
                            <span className="text-[10px] font-black uppercase tracking-widest">Structured Mark Schemes</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-[var(--primary-purple)]">
                        <Info size={14} />
                        Gradiant Examiner Simulation Engine
                    </div>
                </footer>
            </div>
        </div>
    )
}
