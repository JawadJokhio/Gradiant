import { motion } from 'framer-motion'
import { Camera, MessageSquare, Globe, ArrowLeft, BookOpen, Layers, Info } from 'lucide-react'

interface SubjectHubProps {
    subject: {
        id: string;
        name: string;
        color: string;
        description: string;
    };
    onSelectMode: (mode: 'vision' | 'text' | 'geography') => void;
    onBack: () => void;
}

export default function SubjectHub({ subject, onSelectMode, onBack }: SubjectHubProps) {
    return (
        <div className="min-h-screen bg-slate-950 text-white p-8">
            <div className="max-w-4xl mx-auto space-y-12">
                <header className="flex items-center justify-between">
                    <button onClick={onBack} className="p-2 hover:bg-white/5 rounded-lg transition-colors flex items-center gap-2 text-slate-400 hover:text-white group">
                        <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
                        <span className="font-bold">Back to Dashboard</span>
                    </button>
                    <div className="text-right">
                        <div className={`inline-block px-3 py-1 rounded-full bg-gradient-to-r ${subject.color} text-[10px] font-black uppercase tracking-widest mb-2`}>
                            {subject.name} Module
                        </div>
                        <h1 className="text-4xl font-black tracking-tighter">{subject.name} Hub</h1>
                    </div>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <motion.button
                        whileHover={{ y: -5, scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => onSelectMode('vision')}
                        className="group relative overflow-hidden p-8 rounded-3xl bg-slate-900 border border-white/5 hover:border-indigo-500/50 transition-all text-left flex flex-col gap-6"
                    >
                        <div className="w-16 h-16 rounded-2xl bg-indigo-600 flex items-center justify-center shadow-xl shadow-indigo-600/30 group-hover:scale-110 transition-transform">
                            <Camera size={32} />
                        </div>
                        <div>
                            <h3 className="text-2xl font-bold mb-2">Vision Scanner</h3>
                            <p className="text-slate-400 text-sm leading-relaxed">
                                Scan your {subject.name} past paper questions. Our AI references the latest O-Level marking schemes to provide accurate solutions.
                            </p>
                        </div>
                        <div className="mt-4 flex items-center gap-2 text-xs font-bold text-indigo-400">
                            Launch AI Vision Sensor <ArrowLeft size={14} className="rotate-180" />
                        </div>
                    </motion.button>

                    <motion.button
                        whileHover={{ y: -5, scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => onSelectMode('text')}
                        className="group relative overflow-hidden p-8 rounded-3xl bg-slate-900 border border-white/5 hover:border-cyan-500/50 transition-all text-left flex flex-col gap-6"
                    >
                        <div className="w-16 h-16 rounded-2xl bg-cyan-600 flex items-center justify-center shadow-xl shadow-cyan-600/30 group-hover:scale-110 transition-transform">
                            <MessageSquare size={32} />
                        </div>
                        <div>
                            <h3 className="text-2xl font-bold mb-2">Text Explainer</h3>
                            <p className="text-slate-400 text-sm leading-relaxed">
                                Get conceptual clarity. Ask complex {subject.name} questions and receive structured, examiner-style explanations.
                            </p>
                        </div>
                        <div className="mt-4 flex items-center gap-2 text-xs font-bold text-cyan-400">
                            Open Intelligence Engine <ArrowLeft size={14} className="rotate-180" />
                        </div>
                    </motion.button>

                    {subject.id === 'geography' && (
                        <motion.button
                            whileHover={{ y: -5, scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => onSelectMode('geography')}
                            className="md:col-span-2 group relative overflow-hidden p-8 rounded-3xl bg-gradient-to-r from-emerald-600/20 to-teal-600/20 border border-emerald-500/30 hover:border-emerald-500/50 transition-all text-left flex items-center justify-between"
                        >
                            <div className="flex gap-6 items-center">
                                <div className="w-16 h-16 rounded-2xl bg-emerald-600 flex items-center justify-center shadow-xl shadow-emerald-600/30 group-hover:scale-110 transition-transform">
                                    <Globe size={32} />
                                </div>
                                <div>
                                    <h3 className="text-2xl font-bold mb-1">Interactive GIS Map</h3>
                                    <p className="text-slate-400 text-sm max-w-xl">
                                        Explore Pakistan's physical and human geography with our advanced GIS terminal. Layer forests, energy routes, and population data.
                                    </p>
                                </div>
                            </div>
                            <div className="hidden sm:flex items-center gap-2 text-xs font-black uppercase tracking-tighter bg-emerald-500 text-white px-4 py-2 rounded-full shadow-lg">
                                Launch GIS Terminal
                            </div>
                        </motion.button>
                    )}
                </div>

                <footer className="pt-12 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-6 opacity-40">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <BookOpen size={16} />
                            <span className="text-[10px] font-black uppercase tracking-widest">Syllabus 2024-26</span>
                        </div>
                        <div className="w-px h-4 bg-white/20"></div>
                        <div className="flex items-center gap-2">
                            <Layers size={16} />
                            <span className="text-[10px] font-black uppercase tracking-widest">Marking Scheme Precision</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-2 text-[10px] font-bold">
                        <Info size={14} />
                        Powered by Antigravity AI Examiner
                    </div>
                </footer>
            </div>
        </div>
    )
}
