import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, ChevronLeft, Calendar, BookOpen, Layers, ChevronRight, FileText, CheckCircle2, AlertCircle, Sparkles, MapPin, ArrowLeft } from 'lucide-react'

export default function PaperExplorer({ initialSubject, onBack }) {
    const [years, setYears] = useState([])
    const [selectedYear, setSelectedYear] = useState(null)
    const [sessions, setSessions] = useState([])
    const [selectedSession, setSelectedSession] = useState(null)
    const [content, setContent] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchYears()
    }, [])

    const fetchYears = async () => {
        try {
            const response = await fetch(`http://localhost:8000/papers/${initialSubject}/years`)
            const data = await response.json()
            setYears(data)
            if (data.length > 0) handleYearSelect(data[0])
        } catch (error) {
            console.error("Error fetching years:", error)
        } finally {
            setLoading(false)
        }
    }

    const handleYearSelect = async (year) => {
        setSelectedYear(year)
        setSelectedSession(null)
        setContent(null)
        try {
            const response = await fetch(`http://localhost:8000/papers/${initialSubject}/${year}`)
            const data = await response.json()
            setSessions(data)
            if (data.length > 0) handleSessionSelect(year, data[0])
        } catch (error) {
            console.error("Error fetching sessions:", error)
        }
    }

    const handleSessionSelect = async (year, session) => {
        setSelectedSession(session)
        try {
            const response = await fetch(`http://localhost:8000/papers/${initialSubject}/${year}/${session}`)
            const data = await response.json()
            setContent(data)
        } catch (error) {
            console.error("Error fetching content:", error)
        }
    }

    return (
        <div className="min-h-screen bg-[var(--bg-cream)] text-[var(--text-dark)] flex flex-col md:flex-row h-screen overflow-hidden transition-colors duration-500">
            {/* Navigation Sidebar */}
            <aside className="w-full md:w-[380px] bg-[var(--bg-card)] border-r border-[var(--border-color)] flex flex-col p-8 md:p-12 overflow-y-auto custom-scrollbar transition-colors duration-500">
                <button
                    onClick={onBack}
                    className="flex items-center text-[var(--primary-purple)] font-black uppercase tracking-[0.2em] text-[10px] group mb-12"
                >
                    <ArrowLeft size={16} className="mr-2 group-hover:-translate-x-1 transition-transform" />
                    Archive Hub
                </button>

                <div className="space-y-12">
                    <header className="space-y-2">
                        <div className="flex items-center gap-3 text-[var(--accent-gold)]">
                            <BookOpen size={24} />
                            <span className="font-black uppercase tracking-[0.3em] text-[10px]">Cambridge Repository</span>
                        </div>
                        <h1 className="text-4xl font-black text-[var(--primary-purple)] capitalize leading-none tracking-tighter">
                            {initialSubject} Files
                        </h1>
                    </header>

                    {/* Year Selection */}
                    <div className="space-y-6">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-[var(--text-muted)] flex items-center gap-2">
                            <Calendar size={14} /> Chronological Range
                        </h3>
                        <div className="grid grid-cols-2 gap-3">
                            {years.map(year => (
                                <button
                                    key={year}
                                    onClick={() => handleYearSelect(year)}
                                    className={`px-6 py-4 rounded-2xl font-black text-xs transition-all text-center border-2 ${selectedYear === year
                                        ? 'bg-[var(--primary-purple)] border-[var(--primary-purple)] text-white dark:text-[#0f0a1e] shadow-xl shadow-purple-900/10 dark:shadow-black/40'
                                        : 'bg-[var(--bg-card)] border-[var(--border-color)] text-[var(--text-muted)] hover:border-[var(--primary-purple)]'
                                        }`}
                                >
                                    {year}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Session Selection */}
                    <AnimatePresence mode="wait">
                        {selectedYear && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="space-y-6 pt-6 border-t border-[var(--border-color)]"
                            >
                                <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-[var(--text-muted)] flex items-center gap-2">
                                    <Layers size={14} /> Available Sessions
                                </h3>
                                <div className="space-y-3">
                                    {sessions.map(session => (
                                        <button
                                            key={session}
                                            onClick={() => handleSessionSelect(selectedYear, session)}
                                            className={`w-full px-6 py-5 rounded-[1.5rem] font-bold text-sm transition-all text-left flex justify-between items-center group ${selectedSession === session
                                                ? 'bg-[var(--accent-gold)] text-white dark:text-[#0f0a1e] shadow-xl shadow-yellow-900/10 dark:shadow-black/40'
                                                : 'bg-[var(--primary-purple-light)]/5 dark:bg-[var(--bg-card)] text-[var(--primary-purple)] hover:bg-[var(--primary-purple-light)]/10 dark:hover:bg-[var(--primary-purple-light)]/10 border border-transparent hover:border-[var(--border-color)]'
                                                }`}
                                        >
                                            <span className="uppercase tracking-widest text-[11px] font-black">
                                                {session.replace(/_/g, ' ')}
                                            </span>
                                            <ChevronRight size={18} className={selectedSession === session ? 'opacity-100' : 'opacity-0 group-hover:opacity-100 translate-x-2 group-hover:translate-x-0 transition-all'} />
                                        </button>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </aside>

            {/* Content Area */}
            <main className="flex-1 bg-transparent overflow-y-auto p-8 md:p-16 lg:p-24 custom-scrollbar">
                <AnimatePresence mode="wait">
                    {content ? (
                        <motion.div
                            key={`${selectedYear}-${selectedSession}`}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="space-y-20 max-w-5xl"
                        >
                            {Object.entries(content).map(([paperKey, paperData]) => (
                                <div key={paperKey} className="space-y-12">
                                    <div className="flex flex-col md:flex-row md:items-center gap-6">
                                        <div className="w-20 h-20 rounded-[2rem] bg-[var(--bg-card)] border border-[var(--border-color)] flex items-center justify-center text-[var(--primary-purple)] shadow-2xl shadow-purple-900/5 dark:shadow-black/20">
                                            <FileText size={40} />
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-3">
                                                <span className="px-3 py-1 bg-emerald-50 dark:bg-emerald-900/10 text-emerald-600 dark:text-emerald-400 text-[10px] font-black uppercase tracking-widest rounded-lg border border-emerald-100 dark:border-emerald-900/20">Official Mark Scheme</span>
                                            </div>
                                            <h2 className="text-4xl md:text-5xl font-black text-[var(--primary-purple)] uppercase tracking-tighter mt-2">
                                                {paperKey.replace(/_/g, ' ')}
                                            </h2>
                                        </div>
                                    </div>

                                    <div className="space-y-16">
                                        {paperData.mark_scheme?.map((item, idx) => (
                                            <div key={idx} className="group relative">
                                                <div className="absolute -left-12 top-0 text-[80px] font-black text-[var(--primary-purple-light)]/10 dark:text-[var(--primary-purple-light)]/5 -z-10 select-none">
                                                    {idx + 1 < 10 ? `0${idx + 1}` : idx + 1}
                                                </div>

                                                <div className="space-y-8">
                                                    <div className="flex items-start gap-6">
                                                        <p className="text-2xl md:text-3xl font-black text-[var(--primary-purple)] leading-tight flex-1">
                                                            {item.question}
                                                        </p>
                                                    </div>

                                                    <div className="md:ml-2 grid grid-cols-1 gap-8">
                                                        <div className="space-y-4">
                                                            <h4 className="flex items-center gap-3 text-[11px] font-black uppercase tracking-[0.3em] text-[var(--accent-gold)]">
                                                                <CheckCircle2 size={16} /> Scoring Points
                                                            </h4>
                                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                                {item.mark_scheme_points.map((point, pIdx) => (
                                                                    <div key={pIdx} className="bg-[var(--bg-card)] p-6 rounded-[2rem] border border-[var(--border-color)] text-md font-bold text-[var(--text-muted)] leading-relaxed shadow-sm hover:shadow-md transition-all">
                                                                        {point}
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>

                                                        {item.examiner_tips && item.examiner_tips.length > 0 && (
                                                            <div className="p-8 md:p-12 bg-[var(--primary-purple)] rounded-[3rem] text-white dark:text-[#0f0a1e] relative overflow-hidden shadow-2xl shadow-purple-900/20 dark:shadow-black/40">
                                                                <div className="absolute top-0 right-0 p-12 opacity-5 pointer-events-none text-white dark:text-black">
                                                                    <Sparkles size={180} />
                                                                </div>
                                                                <h4 className="flex items-center gap-3 text-[10px] font-black uppercase tracking-[0.3em] opacity-40 mb-6 font-mono">
                                                                    <AlertCircle size={18} /> Chief Examiner Insight
                                                                </h4>
                                                                {item.examiner_tips.map((tip, tIdx) => (
                                                                    <p key={tIdx} className="text-xl font-bold leading-relaxed italic">"{tip}"</p>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="h-[2px] w-full bg-gradient-to-r from-[var(--border-color)] via-transparent to-transparent"></div>
                                </div>
                            ))}
                        </motion.div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-center p-12 space-y-10">
                            <div className="w-32 h-32 rounded-[3.5rem] bg-[var(--bg-card)] border border-dashed border-[var(--border-color)] flex items-center justify-center text-[var(--primary-purple)]/10">
                                <Search size={64} />
                            </div>
                            <div className="space-y-4">
                                <h2 className="text-3xl font-black text-[var(--primary-purple-light)]/20 uppercase tracking-[0.4em]">Initialize Archive Access</h2>
                                <p className="text-[var(--text-muted)]/50 max-w-sm mx-auto text-lg font-medium italic">Select a chronological range and exam session from the repository sidebar.</p>
                            </div>
                        </div>
                    )}
                </AnimatePresence>
            </main>
        </div>
    )
}
