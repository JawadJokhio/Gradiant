import { motion } from 'framer-motion'
import { Book, Globe, TrendingUp, Landmark, Zap, Beaker, Camera, MessageSquare, ChevronRight } from 'lucide-react'

interface Subject {
    id: string;
    name: string;
    icon: React.ReactNode;
    color: string;
    description: string;
}

interface SubjectDashboardProps {
    onSelectSubject: (subjectId: string) => void;
    onSelectMode: (mode: 'vision' | 'text') => void;
}

const subjects: Subject[] = [
    { id: 'geography', name: 'Geography', icon: <Globe size={24} />, color: 'from-blue-500 to-cyan-500', description: 'Environment of Pakistan & GIS Mapping' },
    { id: 'history', name: 'History', icon: <Landmark size={24} />, color: 'from-amber-500 to-orange-600', description: 'Pakistan Studies & World History' },
    { id: 'economics', name: 'Economics', icon: <TrendingUp size={24} />, color: 'from-emerald-500 to-teal-600', description: 'Market Dynamics & Macroeconomics' },
    { id: 'islamiat', name: 'Islamiat', icon: <Book size={24} />, color: 'from-green-500 to-emerald-700', description: 'Quranic Studies & Islamic History' },
    { id: 'physics', name: 'Physics', icon: <Zap size={24} />, color: 'from-indigo-500 to-purple-600', description: 'Mechanics, Waves & Nuclear Physics' },
    { id: 'chemistry', name: 'Chemistry', icon: <Beaker size={24} />, color: 'from-rose-500 to-pink-600', description: 'Organic & Inorganic Chemistry' },
]

export default function SubjectDashboard({ onSelectSubject, onSelectMode }: SubjectDashboardProps) {
    return (
        <div className="bg-slate-950 text-white p-8">
            <div className="max-w-6xl mx-auto space-y-12">
                <header className="text-center space-y-4">
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-block px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-bold uppercase tracking-widest"
                    >
                        Ultimate O-Level Suite
                    </motion.div>
                    <motion.h1
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="text-5xl md:text-7xl font-black bg-clip-text text-transparent bg-gradient-to-b from-white to-white/40 tracking-tighter"
                    >
                        O-Level Mastermind
                    </motion.h1>
                    <p className="text-slate-400 max-w-2xl mx-auto text-lg">
                        AI-powered academic excellence. Scan past papers, solve concepts, and master the curriculum with precision.
                    </p>
                </header>

                <section className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-12">
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => { onSelectSubject('history'); onSelectMode('vision'); }}
                        className="group relative overflow-hidden p-8 rounded-3xl bg-slate-900 border border-white/5 hover:border-indigo-500/50 transition-all text-left"
                    >
                        <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Camera size={120} />
                        </div>
                        <div className="relative space-y-4">
                            <div className="w-14 h-14 rounded-2xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/30">
                                <Camera size={28} />
                            </div>
                            <div>
                                <h3 className="text-2xl font-bold">Quick Vision Scanner</h3>
                                <p className="text-slate-400">Instantly scan any O-Level question (Defaults to History).</p>
                            </div>
                        </div>
                    </motion.button>

                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => { onSelectSubject('history'); onSelectMode('text'); }}
                        className="group relative overflow-hidden p-8 rounded-3xl bg-slate-900 border border-white/5 hover:border-cyan-500/50 transition-all text-left"
                    >
                        <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
                            <MessageSquare size={120} />
                        </div>
                        <div className="relative space-y-4">
                            <div className="w-14 h-14 rounded-2xl bg-cyan-600 flex items-center justify-center shadow-lg shadow-cyan-600/30">
                                <MessageSquare size={28} />
                            </div>
                            <div>
                                <h3 className="text-2xl font-bold">Quick Text Explainer</h3>
                                <p className="text-slate-400">Ask a conceptual doubt instantly (Defaults to History).</p>
                            </div>
                        </div>
                    </motion.button>
                </section>

                <section className="space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-xs font-black uppercase tracking-[0.3em] text-slate-500">Select Subject Module</h2>
                        <div className="h-px flex-1 bg-white/5 mx-6"></div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {subjects.map((subject, idx) => (
                            <motion.button
                                key={subject.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                whileHover={{ y: -5 }}
                                onClick={() => onSelectSubject(subject.id)}
                                className="group relative flex flex-col p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/[0.08] hover:border-white/10 transition-all text-left"
                            >
                                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${subject.color} flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform`}>
                                    {subject.icon}
                                </div>
                                <h4 className="text-xl font-bold mb-2">{subject.name}</h4>
                                <p className="text-sm text-slate-500 line-clamp-2">{subject.description}</p>
                                <div className="mt-6 flex items-center text-xs font-bold text-slate-400 group-hover:text-white transition-colors">
                                    Open Module <ChevronRight size={14} className="ml-1" />
                                </div>
                            </motion.button>
                        ))}
                    </div>
                </section>
            </div>
        </div>
    )
}
