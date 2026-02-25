import { motion } from 'framer-motion'
import { Book, Globe, TrendingUp, Landmark, Zap, Beaker, Camera, MessageSquare, ChevronRight, BrainCircuit, Search } from 'lucide-react'

const subjects = [
    { id: 'geography', name: 'Geography', icon: <Globe size={24} />, color: 'bg-blue-600', description: 'Environment of Pakistan & GIS Mapping' },
    { id: 'history', name: 'History', icon: <Landmark size={24} />, color: 'bg-purple-600', description: 'Pakistan Studies & World History' },
    { id: 'economics', name: 'Economics', icon: <TrendingUp size={24} />, color: 'bg-emerald-600', description: 'Market Dynamics & Macroeconomics' },
    { id: 'islamiat', name: 'Islamiat', icon: <Book size={24} />, color: 'bg-green-600', description: 'Quranic Studies & Islamic History' },
    { id: 'physics', name: 'Physics', icon: <Zap size={24} />, color: 'bg-indigo-600', description: 'Mechanics, Waves & Nuclear Physics' },
    { id: 'chemistry', name: 'Chemistry', icon: <Beaker size={24} />, color: 'bg-rose-600', description: 'Organic & Inorganic Chemistry' },
]

export default function SubjectDashboard({ onSelectSubject, onSelectMode }) {
    return (
        <div className="min-h-screen bg-[var(--bg-cream)] text-[var(--text-dark)] p-6 md:p-12 relative overflow-hidden transition-colors duration-500">
            {/* Background Decorative Elements */}
            <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-[var(--primary-purple-light)]/20 dark:bg-[var(--primary-purple-light)]/10 rounded-full blur-[120px] pointer-events-none"></div>
            <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-[var(--accent-gold)]/10 rounded-full blur-[120px] pointer-events-none"></div>

            <div className="max-w-7xl mx-auto space-y-16 relative z-10">
                {/* Hero Section */}
                <header className="text-center space-y-6 pt-8">
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-block px-4 py-1.5 rounded-full bg-[var(--primary-purple-light)]/10 border border-[var(--primary-purple-light)]/20 text-[var(--primary-purple)] text-xs font-black uppercase tracking-widest"
                    >
                        Master Your O-Levels
                    </motion.div>
                    <motion.h1
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="text-6xl md:text-8xl font-black text-[var(--primary-purple)] tracking-tight animate-float"
                    >
                        Gradiant AI
                    </motion.h1>
                    <p className="text-[var(--text-muted)] max-w-2xl mx-auto text-xl font-medium leading-relaxed">
                        Your personalized Cambridge examiner. Browse past papers, scan questions, and identify your blind spots with precision.
                    </p>

                    {/* Search Bar Simulation */}
                    <div className="max-w-2xl mx-auto relative group">
                        <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                            <Search size={22} className="text-[var(--primary-purple)]/40 group-focus-within:text-[var(--primary-purple)] transition-colors" />
                        </div>
                        <input
                            type="text"
                            placeholder="Search topics, questions, or papers..."
                            className="w-full bg-[var(--bg-card)] border-2 border-[var(--primary-purple-light)]/10 rounded-2xl py-5 pl-14 pr-6 text-lg shadow-sm focus:border-[var(--primary-purple)] focus:ring-4 focus:ring-[var(--primary-purple-light)]/10 transition-all outline-none"
                        />
                    </div>
                </header>

                {/* Quick Actions */}
                <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <motion.button
                        whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)' }}
                        onClick={() => { onSelectSubject('history'); onSelectMode('vision'); }}
                        className="group relative overflow-hidden p-8 rounded-[2rem] bg-[var(--bg-card)] border border-[var(--border-color)] transition-all text-left shadow-xl shadow-purple-900/5 dark:shadow-black/20"
                    >
                        <div className="w-16 h-16 rounded-2xl bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] flex items-center justify-center mb-6 shadow-lg shadow-purple-900/30">
                            <Camera size={32} />
                        </div>
                        <h3 className="text-2xl font-black text-[var(--primary-purple)] mb-2">Vision Scanner</h3>
                        <p className="text-[var(--text-muted)] font-medium leading-relaxed">Scan any past paper question for instant examiner-level feedback.</p>
                        <div className="mt-6 flex items-center text-sm font-black text-[var(--primary-purple)] uppercase tracking-wider">
                            Launch Scanner <ChevronRight size={18} className="ml-1" />
                        </div>
                    </motion.button>

                    <motion.button
                        whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)' }}
                        onClick={() => { onSelectSubject(subjects[0].id); onSelectMode('text'); }}
                        className="group relative overflow-hidden p-8 rounded-[2rem] bg-[var(--bg-card)] border border-[var(--border-color)] transition-all text-left shadow-xl shadow-purple-900/5 dark:shadow-black/20"
                    >
                        <div className="w-16 h-16 rounded-2xl bg-[var(--accent-gold)] text-white dark:text-[#0f0a1e] flex items-center justify-center mb-6 shadow-lg shadow-gold-900/30">
                            <Search size={32} />
                        </div>
                        <h3 className="text-2xl font-black text-[var(--primary-purple)] mb-2">Paper Explorer</h3>
                        <p className="text-[var(--text-muted)] font-medium leading-relaxed">Browse yearly and topical past papers with official marking schemes.</p>
                        <div className="mt-6 flex items-center text-sm font-black text-[var(--primary-purple)] uppercase tracking-wider">
                            Explore Repository <ChevronRight size={18} className="ml-1" />
                        </div>
                    </motion.button>

                    <motion.button
                        whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(0, 0, 0, 0.2)' }}
                        onClick={() => { onSelectSubject('history'); onSelectMode('weakness'); }}
                        className="group relative overflow-hidden p-8 rounded-[2rem] bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] transition-all text-left shadow-xl shadow-purple-900/20"
                    >
                        <div className="w-16 h-16 rounded-2xl bg-[var(--bg-card)] text-[var(--primary-purple)] flex items-center justify-center mb-6">
                            <BrainCircuit size={32} />
                        </div>
                        <h3 className="text-2xl font-black mb-2">Weakness Fixer</h3>
                        <p className="opacity-80 font-medium leading-relaxed">AI analysis of your performance to identify and resolve weak spots.</p>
                        <div className="mt-6 flex items-center text-sm font-black uppercase tracking-wider">
                            Run Diagnostic <ChevronRight size={18} className="ml-1" />
                        </div>
                    </motion.button>
                </section>

                {/* Subject Modules */}
                <section className="space-y-8 pb-20">
                    <div className="flex items-center gap-6">
                        <h2 className="text-sm font-black uppercase tracking-[0.4em] text-[var(--primary-purple)]/40 whitespace-nowrap">Academic Categories</h2>
                        <div className="h-[2px] w-full bg-[var(--primary-purple-light)]/10"></div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {subjects.map((subject, idx) => (
                            <motion.button
                                key={subject.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.05 }}
                                whileHover={{ scale: 1.02 }}
                                onClick={() => onSelectSubject(subject.id)}
                                className="group flex flex-col p-8 rounded-[2rem] bg-[var(--bg-card)] border border-[var(--border-color)] hover:border-[var(--primary-purple)] transition-all text-left shadow-sm hover:shadow-xl hover:shadow-purple-900/5 rotate-0 hover:rotate-1"
                            >
                                <div className={`w-14 h-14 rounded-2xl ${subject.color} text-white flex items-center justify-center mb-6 shadow-md`}>
                                    {subject.icon}
                                </div>
                                <h4 className="text-2xl font-black text-[var(--primary-purple)] mb-2">{subject.name}</h4>
                                <p className="text-[var(--text-muted)] font-medium text-sm leading-relaxed mb-6">{subject.description}</p>
                                <div className="mt-auto pt-4 flex items-center text-xs font-black text-[var(--primary-purple)] group-hover:translate-x-2 transition-transform uppercase tracking-widest">
                                    Open Subject <ChevronRight size={16} className="ml-1" />
                                </div>
                            </motion.button>
                        ))}
                    </div>
                </section>
            </div>
        </div>
    )
}
