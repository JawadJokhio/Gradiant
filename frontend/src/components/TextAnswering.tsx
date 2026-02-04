import { useState } from 'react'
import { motion } from 'framer-motion'
import { MessageSquare, ArrowLeft, Send, Sparkles, Brain, BookOpen } from 'lucide-react'

interface TextAnsweringProps {
    onBack: () => void;
    initialSubject?: string;
}

export default function TextAnswering({ onBack, initialSubject }: TextAnsweringProps) {
    const [query, setQuery] = useState('')
    const [subject] = useState(initialSubject || 'history')
    const [marks, setMarks] = useState(4)
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [explanation, setExplanation] = useState<string | null>(null)

    const handleAsk = async () => {
        if (!query.trim()) return
        setIsAnalyzing(true)

        const formData = new FormData()
        formData.append('query', query)
        formData.append('subject', subject)
        formData.append('mode', 'text')
        formData.append('marks', marks.toString())

        try {
            const response = await fetch('http://localhost:8000/ask-ai', {
                method: 'POST',
                body: formData,
            })
            const data = await response.json()
            setExplanation(data.answer)
        } catch (error) {
            console.error("Analysis error:", error)
            setExplanation("**Error:** AI engine connection failed. Please check your backend.\n\n### Concept Explainer (Simulation)\nSince you asked about **" + subject + "**, here is a conceptual breakdown:\n- **Definition:** Core principles of the topic.\n- **Significance:** Why this is tested in the O-Level syllabus.\n- **Exam Strategy:** How to approach this in a Paper 1 or Paper 2 context.")
        } finally {
            setIsAnalyzing(false)
        }
    }

    return (
        <div className="min-h-screen bg-slate-950 text-white flex flex-col">
            <header className="h-16 flex-shrink-0 bg-slate-900/50 backdrop-blur-xl border-b border-white/5 px-6 flex items-center justify-between z-10">
                <div className="flex items-center gap-4">
                    <button onClick={onBack} className="p-2 hover:bg-white/5 rounded-lg transition-colors text-slate-400">
                        <ArrowLeft size={20} />
                    </button>
                    <div className="h-6 w-px bg-white/10 mx-2"></div>
                    <h2 className="text-lg font-bold flex items-center gap-2">
                        <MessageSquare size={18} className="text-cyan-400" /> Text Explainer
                    </h2>
                </div>

                <div className="flex items-center gap-3">
                    <div className={`px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-[10px] font-black uppercase tracking-widest`}>
                        {subject}
                    </div>
                </div>

                <div className="flex items-center gap-2 bg-slate-800 border border-white/10 rounded-lg px-2 py-1">
                    <span className="text-[10px] font-black text-slate-500 uppercase">Marks</span>
                    <select
                        value={marks}
                        onChange={(e) => setMarks(Number(e.target.value))}
                        className="bg-transparent text-xs font-bold focus:outline-none text-cyan-400 cursor-pointer"
                    >
                        {subject === 'history' ? (
                            [3, 4, 5, 7, 10, 14].map(m => <option key={m} value={m} className="bg-slate-900">{m}</option>)
                        ) : (
                            [1, 2, 3, 4, 5, 6, 8, 10, 12, 14].map(m => <option key={m} value={m} className="bg-slate-900">{m}</option>)
                        )}
                    </select>
                </div>
            </header>

            <main className="flex-1 flex flex-col items-center justify-start p-6 overflow-y-auto custom-scrollbar">
                <div className="w-full max-w-4xl space-y-8">
                    {/* Input Area */}
                    <section className="space-y-4">
                        <div className="flex items-center gap-3 text-slate-500">
                            <Sparkles size={16} className="text-cyan-400" />
                            <p className="text-sm font-bold uppercase tracking-widest">Subject Intelligence Engine</p>
                        </div>
                        <div className="relative group">
                            <textarea
                                placeholder={`Ask anything about O-Level ${subject}...`}
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                className="w-full bg-slate-900 border border-white/5 rounded-3xl p-6 h-40 text-lg focus:outline-none focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/10 transition-all shadow-2xl resize-none placeholder:text-slate-700"
                            />
                            <button
                                onClick={handleAsk}
                                disabled={isAnalyzing || !query.trim()}
                                className="absolute bottom-6 right-6 p-4 rounded-2xl bg-cyan-600 hover:bg-cyan-500 transition-all shadow-xl shadow-cyan-600/20 active:scale-95 disabled:opacity-30"
                            >
                                <Send size={24} />
                            </button>
                        </div>
                        <div className="flex gap-4">
                            <button onClick={() => setQuery("Explain the main causes of the 1857 War of Independence.")} className="text-[10px] bg-white/5 px-3 py-1.5 rounded-full border border-white/5 hover:border-cyan-500/30 transition-all text-slate-400">Suggest: 1857 War</button>
                            <button onClick={() => setQuery("Differentiate between market equilibrium and disequilibrium.")} className="text-[10px] bg-white/5 px-3 py-1.5 rounded-full border border-white/5 hover:border-cyan-500/30 transition-all text-slate-400">Suggest: Economics</button>
                            <button onClick={() => setQuery("How does a step-up transformer work?")} className="text-[10px] bg-white/5 px-3 py-1.5 rounded-full border border-white/5 hover:border-cyan-500/30 transition-all text-slate-400">Suggest: Transformers</button>
                        </div>
                    </section>

                    {/* Result Area */}
                    <section className="min-h-[200px]">
                        {isAnalyzing ? (
                            <div className="flex flex-col items-center justify-center p-20 gap-6">
                                <div className="relative">
                                    <div className="w-20 h-20 border-4 border-cyan-500/20 rounded-full"></div>
                                    <div className="absolute inset-0 w-20 h-20 border-t-4 border-cyan-500 rounded-full animate-spin"></div>
                                    <Brain className="absolute inset-0 m-auto text-cyan-400 animate-pulse" size={32} />
                                </div>
                                <p className="text-cyan-400 font-mono text-sm animate-pulse tracking-widest uppercase">Consulting O-Level Databases...</p>
                            </div>
                        ) : explanation ? (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="bg-white/5 border border-white/5 rounded-3xl p-8 shadow-2xl space-y-6"
                            >
                                <div className="flex items-center gap-3 text-cyan-400 border-b border-white/5 pb-4">
                                    <BookOpen size={20} />
                                    <h3 className="font-bold text-lg">Curriculum Explanation</h3>
                                </div>
                                <div className="prose prose-invert max-w-none text-slate-300 leading-relaxed whitespace-pre-wrap">
                                    {explanation.split('\n').map((line, i) => {
                                        if (line.startsWith('### [1]')) return (
                                            <div key={i} className="mt-6 mb-6 p-4 bg-amber-500/5 border-l-4 border-amber-500/50 rounded-xl">
                                                <h4 className="text-xl font-black text-amber-400 uppercase tracking-widest">1. Marking Scheme Breakdown</h4>
                                            </div>
                                        )
                                        if (line.startsWith('### [2]')) return (
                                            <div key={i} className="mt-10 mb-6 p-4 bg-cyan-500/5 border-l-4 border-cyan-500/50 rounded-xl">
                                                <h4 className="text-xl font-black text-cyan-400 uppercase tracking-widest">2.O-Level Script</h4>
                                            </div>
                                        )
                                        if (line.startsWith('### [3]')) return (
                                            <div key={i} className="mt-12 mb-6 p-4 bg-rose-500/5 border-l-4 border-rose-500/50 rounded-xl">
                                                <h4 className="text-xl font-black text-rose-400 uppercase tracking-widest">3. Common Pitfalls</h4>
                                            </div>
                                        )
                                        if (line.startsWith('### [4]')) return (
                                            <div key={i} className="mt-12 mb-6 p-4 bg-purple-500/5 border-l-4 border-purple-500/50 rounded-xl">
                                                <h4 className="text-xl font-black text-purple-400 uppercase tracking-widest">4. Tutor Wisdom</h4>
                                            </div>
                                        )
                                        if (line.startsWith('###')) return <h4 key={i} className="text-xl font-bold text-white mt-8 mb-4">{line.replace('###', '')}</h4>
                                        if (line.startsWith('- **')) return <div key={i} className="mb-3 pl-4 border-l-3 border-cyan-500/50 bg-cyan-500/5 p-3 rounded-r-xl"><strong className="text-cyan-300">{line.replace('- **', '').split('**')[0]}</strong> {line.split('**')[2]}</div>
                                        if (line.startsWith('- ')) return <div key={i} className="mb-2 flex items-start gap-2 text-slate-400 italic"><span>•</span> {line.replace('- ', '')}</div>
                                        return line ? <p key={i} className="mb-4">{line}</p> : <br key={i} />
                                    })}
                                </div>
                                {explanation && (
                                    <div className="mt-12 pt-8 border-t border-white/5 space-y-6">
                                        <div className="flex items-center gap-3 text-slate-500">
                                            <Brain size={16} className="text-purple-400" />
                                            <p className="text-xs font-black uppercase tracking-widest text-slate-500">Interactive Follow-up</p>
                                        </div>
                                        <div className="relative group">
                                            <input
                                                type="text"
                                                placeholder="Ask for clarification or deeper detail..."
                                                className="w-full bg-slate-900 border border-white/10 rounded-2xl py-4 px-6 pr-14 text-sm focus:outline-none focus:border-cyan-500/50 transition-all"
                                            />
                                            <button className="absolute right-3 top-2.5 p-2.5 bg-cyan-600 rounded-xl hover:bg-cyan-500 transition-colors shadow-lg shadow-cyan-600/20">
                                                <Send size={18} />
                                            </button>
                                        </div>
                                        <p className="text-[10px] text-center text-slate-600 font-bold uppercase tracking-widest">Tutor reasoning engine active</p>
                                    </div>
                                )}
                            </motion.div>
                        ) : (
                            <div className="h-full py-20 border border-white/5 rounded-3xl bg-slate-900/40 flex flex-col items-center justify-center text-slate-600 gap-4">
                                <Sparkles size={48} className="opacity-10" />
                                <p className="text-sm font-medium opacity-40">Your AI-powered tutor is ready. Ask a question to begin.</p>
                            </div>
                        )}
                    </section>
                </div>
            </main>
        </div>
    )
}
