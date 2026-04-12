import { useState } from 'react'
import { motion } from 'framer-motion'
import { MessageSquare, ArrowLeft, Send, Sparkles, Brain, BookOpen, ChevronLeft } from 'lucide-react'

export default function TextAnswering({ onBack, initialSubject }) {

    const [query, setQuery] = useState('')
    const [subject] = useState(initialSubject || 'history')
    const [marks, setMarks] = useState(4)
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [explanation, setExplanation] = useState(null)

    const handleAsk = async () => {
        if (!query.trim()) return
        setIsAnalyzing(true)

        const formData = new FormData()
        formData.append('query', query)
        formData.append('subject', subject)
        formData.append('mode', 'text')
        formData.append('marks', marks.toString())

        try {
            const response = await fetch('http://localhost:8000/history/ask-ai', {
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
        <div className="min-h-screen bg-[var(--bg-cream)] text-[var(--text-dark)] flex flex-col transition-colors duration-500">
            <header className="h-20 flex-shrink-0 bg-[var(--bg-card)]/70 backdrop-blur-xl border-b border-[var(--border-color)] px-6 flex items-center justify-between z-10 sticky top-0 transition-colors duration-500">
                <div className="flex items-center gap-4">
                    <button onClick={onBack} className="p-2 hover:bg-[var(--primary-purple-light)]/10 rounded-xl transition-colors text-[var(--primary-purple)] group">
                        <ChevronLeft size={24} className="group-hover:-translate-x-1 transition-transform" />
                    </button>
                    <div className="h-8 w-[1px] bg-[var(--border-color)] mx-1"></div>
                    <div>
                        <h2 className="text-xl font-black text-[var(--primary-purple)] flex items-center gap-2">
                            Concept Explainer
                        </h2>
                        <p className="text-[10px] font-black uppercase tracking-widest text-[var(--accent-gold)]">AI Intelligence Engine</p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <div className={`px-4 py-1.5 rounded-full bg-[var(--primary-purple-light)]/10 border border-[var(--border-color)] text-[var(--primary-purple)] text-[10px] font-black uppercase tracking-widest`}>
                        {subject}
                    </div>
                    <div className="flex items-center gap-3 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-4 py-2 shadow-sm">
                        <span className="text-[10px] font-black text-[var(--text-muted)] uppercase tracking-tighter">Marks Allocation</span>
                        <select
                            value={marks}
                            onChange={(e) => setMarks(Number(e.target.value))}
                            className="bg-transparent text-sm font-black focus:outline-none text-[var(--primary-purple)] cursor-pointer"
                        >
                            {subject === 'history' ? (
                                [3, 4, 5, 7, 10, 14].map(m => <option key={m} value={m} className="bg-[var(--bg-card)]">{m}</option>)
                            ) : (
                                [1, 2, 3, 4, 5, 6, 8, 10, 12, 14].map(m => <option key={m} value={m} className="bg-[var(--bg-card)]">{m}</option>)
                            )}
                        </select>
                    </div>
                </div>
            </header>

            <main className="flex-1 flex flex-col items-center justify-start p-6 md:p-12 overflow-y-auto custom-scrollbar">
                <div className="w-full max-w-4xl space-y-12">
                    {/* Input Area */}
                    <section className="space-y-6">
                        <div className="flex items-center gap-3 text-[var(--text-muted)]">
                            <Sparkles size={20} className="text-[var(--accent-gold)]" />
                            <p className="text-sm font-black uppercase tracking-widest">Question Terminal</p>
                        </div>
                        <div className="relative group">
                            <textarea
                                placeholder={`Type or paste your O-Level ${subject} question here...`}
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                className="w-full bg-[var(--bg-card)] border-2 border-[var(--border-color)] rounded-[2.5rem] p-10 h-56 text-xl focus:outline-none focus:border-[var(--primary-purple)] focus:ring-8 focus:ring-[var(--primary-primary-purple-light)]/10 transition-all shadow-2xl shadow-purple-900/5 dark:shadow-black/20 resize-none placeholder:text-[var(--border-color)] text-[var(--text-dark)] font-medium"
                            />
                            <button
                                onClick={handleAsk}
                                disabled={isAnalyzing || !query.trim()}
                                className="absolute bottom-8 right-8 p-6 rounded-[1.5rem] bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] hover:scale-105 transition-all shadow-2xl shadow-purple-900/40 dark:shadow-black/60 active:scale-95 disabled:opacity-20 flex items-center gap-3 font-black uppercase tracking-widest text-xs"
                            >
                                <span className="hidden md:block">Analyze Question</span>
                                <Send size={20} />
                            </button>
                        </div>
                        <div className="flex flex-wrap gap-3">
                            <button onClick={() => setQuery("Explain the main causes of the 1857 War of Independence.")} className="text-[10px] font-black uppercase tracking-widest bg-[var(--bg-card)] px-4 py-2 rounded-full border border-[var(--border-color)] hover:border-[var(--primary-purple)] transition-all text-[var(--text-muted)]">Suggest: 1857 War</button>
                            <button onClick={() => setQuery("How does a step-up transformer work?")} className="text-[10px] font-black uppercase tracking-widest bg-[var(--bg-card)] px-4 py-2 rounded-full border border-[var(--border-color)] hover:border-[var(--primary-purple)] transition-all text-[var(--text-muted)]">Suggest: Transformers</button>
                        </div>
                    </section>

                    {/* Result Area */}
                    <section className="min-h-[300px] mb-20 text-[var(--text-dark)]">
                        {isAnalyzing ? (
                            <div className="flex flex-col items-center justify-center p-20 gap-8">
                                <div className="relative">
                                    <div className="w-24 h-24 border-8 border-[var(--primary-purple-light)]/20 rounded-full"></div>
                                    <div className="absolute inset-0 w-24 h-24 border-t-8 border-[var(--primary-purple)] rounded-full animate-spin"></div>
                                    <Brain className="absolute inset-0 m-auto text-[var(--accent-gold)] animate-pulse" size={32} />
                                </div>
                                <div className="text-center space-y-2">
                                    <p className="text-[var(--primary-purple)] font-black text-sm tracking-[0.3em] uppercase">Simulating Examiner</p>
                                    <p className="text-[var(--text-muted)] text-xs font-medium">Accessing structured Cambridge marking schemes...</p>
                                </div>
                            </div>
                        ) : explanation ? (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.98 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-[3rem] p-8 md:p-14 shadow-2xl shadow-purple-900/5 dark:shadow-black/20 space-y-10"
                            >
                                <div className="flex items-center justify-between border-b border-[var(--border-color)] pb-8">
                                    <div className="flex items-center gap-4 text-[var(--primary-purple)]">
                                        <div className="w-12 h-12 rounded-2xl bg-[var(--primary-purple-light)]/10 flex items-center justify-center">
                                            <BookOpen size={24} />
                                        </div>
                                        <div>
                                            <h3 className="font-black text-2xl uppercase tracking-tighter">Examiner Report</h3>
                                            <p className="text-[10px] font-black text-[var(--accent-gold)] uppercase tracking-widest">Marked for {marks} points</p>
                                        </div>
                                    </div>
                                    <button
                                        className="text-[10px] font-black uppercase tracking-widest text-[var(--primary-purple)] hover:underline"
                                        onClick={() => window.print()}
                                    >
                                        Export PDF
                                    </button>
                                </div>

                                <div className="prose prose-purple dark:prose-invert max-w-none text-[var(--text-dark)] leading-relaxed whitespace-pre-wrap font-medium">
                                    {explanation.split('\n').map((line, i) => {
                                        if (line.startsWith('### [1]')) return (
                                            <div key={i} className="mt-8 mb-6 p-6 bg-[var(--primary-purple-light)]/10 border-l-4 border-[var(--primary-purple)] rounded-2xl">
                                                <h4 className="text-lg font-black text-[var(--primary-purple)] uppercase tracking-widest">1. Marking Protocol</h4>
                                            </div>
                                        )
                                        if (line.startsWith('### [2]')) return (
                                            <div key={i} className="mt-12 mb-6 p-6 bg-blue-50 dark:bg-blue-900/10 border-l-4 border-blue-600 rounded-2xl">
                                                <h4 className="text-lg font-black text-blue-600 dark:text-blue-400 uppercase tracking-widest">2. Model Answer</h4>
                                            </div>
                                        )
                                        if (line.startsWith('### [3]')) return (
                                            <div key={i} className="mt-12 mb-6 p-6 bg-amber-50 dark:bg-amber-900/10 border-l-4 border-[var(--accent-gold)] rounded-2xl">
                                                <h4 className="text-lg font-black text-[var(--accent-gold)] uppercase tracking-widest">3. Common Mistakes</h4>
                                            </div>
                                        )
                                        if (line.startsWith('### [4]')) return (
                                            <div key={i} className="mt-12 mb-6 p-6 bg-emerald-50 dark:bg-emerald-900/10 border-l-4 border-emerald-600 rounded-2xl">
                                                <h4 className="text-lg font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest">4. Examiner Tips</h4>
                                            </div>
                                        )
                                        if (line.startsWith('###')) return <h4 key={i} className="text-2xl font-black text-[var(--primary-purple)] mt-12 mb-6">{line.replace('###', '')}</h4>
                                        if (line.startsWith('- **')) {
                                            const parts = line.replace('- **', '').split('**')
                                            return (
                                                <div key={i} className="mb-4 pl-6 border-l-2 border-[var(--border-color)] py-1">
                                                    <strong className="text-[var(--primary-purple)] font-black">{parts[0]}</strong> {parts[2]}
                                                </div>
                                            )
                                        }
                                        if (line.startsWith('- ')) return <div key={i} className="mb-2 flex items-start gap-3 text-[var(--text-muted)] font-medium italic"><span className="text-[var(--accent-gold)]">•</span> {line.replace('- ', '')}</div>
                                        return line ? <p key={i} className="mb-6 text-lg">{line}</p> : <br key={i} />
                                    })}
                                </div>

                                <div className="mt-16 pt-10 border-t border-[var(--border-color)] space-y-8">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-[var(--primary-purple-light)]/10 flex items-center justify-center text-[var(--primary-purple)]">
                                            <Brain size={16} />
                                        </div>
                                        <p className="text-xs font-black uppercase tracking-widest text-[var(--text-muted)]">Interactive Follow-up</p>
                                    </div>
                                    <div className="relative group">
                                        <input
                                            type="text"
                                            placeholder="Ask for clarification on any point..."
                                            className="w-full bg-[var(--bg-cream)] dark:bg-[var(--bg-card)] border-2 border-transparent focus:border-[var(--primary-purple)] rounded-[1.5rem] py-5 px-8 pr-16 text-sm focus:outline-none transition-all font-medium text-[var(--text-dark)]"
                                        />
                                        <button className="absolute right-4 top-3.5 p-3 bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] rounded-xl shadow-xl shadow-purple-900/20 active:scale-95 transition-transform">
                                            <Send size={18} />
                                        </button>
                                    </div>
                                    <div className="flex items-center justify-center gap-2">
                                        <div className="w-1 h-1 rounded-full bg-[var(--border-color)]"></div>
                                        <p className="text-[10px] text-center text-[var(--text-muted)] font-black uppercase tracking-widest opacity-40">Intelligence loop active</p>
                                        <div className="w-1 h-1 rounded-full bg-[var(--border-color)]"></div>
                                    </div>
                                </div>
                            </motion.div>
                        ) : (
                            <div className="h-[40vh] border-4 border-dashed border-[var(--border-color)] rounded-[3rem] flex flex-col items-center justify-center text-[var(--text-muted)] opacity-20 gap-6">
                                <Sparkles size={64} className="animate-pulse" />
                                <div className="text-center">
                                    <p className="text-xl font-black uppercase tracking-widest">Awaiting Question</p>
                                    <p className="text-sm font-bold mt-2">The AI examiner is standing by.</p>
                                </div>
                            </div>
                        )}
                    </section>
                </div>
            </main>
        </div>
    )
}
