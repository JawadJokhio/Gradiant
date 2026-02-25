import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Brain, BookOpen, User, Award, ShieldCheck, Info, Sparkles, ChevronRight, AlertTriangle, ArrowLeft, ChevronLeft, Sparkle } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function HistoryExaminer({ onBack }) {
    const { token } = useAuth()
    const [query, setQuery] = useState('')
    const [selectedMarks, setSelectedMarks] = useState(null)
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [messages, setMessages] = useState([])
    const [lastWisdom, setLastWisdom] = useState("Focus on command words like 'Why' (4/7) and 'Describe' (4). For 14 marks, your judgement must match the evidence provided in the essay body.")
    const chatEndRef = useRef(null)

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages, isAnalyzing])

    const handleAsk = async () => {
        if (!query.trim() || selectedMarks === null) return

        const userQuery = query
        setQuery('')
        setMessages(prev => [...prev, { role: 'user', content: userQuery, marks: selectedMarks }])
        setIsAnalyzing(true)

        const formData = new FormData()
        formData.append('query', userQuery)
        formData.append('subject', 'history')
        formData.append('marks', selectedMarks.toString())
        formData.append('mode', 'chat')

        try {
            const response = await fetch('http://localhost:8000/ask-ai', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData,
            })
            const data = await response.json()

            // Dynamic Wisdom Extraction
            if (data.answer && data.answer.includes('### [4]')) {
                const wisdomPart = data.answer.split('### [4]')[1].split('\n')[1] || data.answer.split('### [4]')[1].split('\n')[0]
                if (wisdomPart.trim()) {
                    setLastWisdom(wisdomPart.trim().replace(/^Tutor Wisdom:?\s*/i, ''))
                }
            }

            setMessages(prev => [...prev, { role: 'ai', content: data.answer, marks: selectedMarks }])
        } catch (error) {
            setMessages(prev => [...prev, { role: 'ai', content: "Error connecting to Examiner Engine. Please ensure the backend is running.", isError: true }])
        } finally {
            setIsAnalyzing(false)
        }
    }

    const renderAudit = (content) => {
        const auditIndex = content.indexOf('[EXAMINER AUDIT]')
        if (auditIndex === -1) return null

        const auditText = content.substring(auditIndex + 16).trim()
        return (
            <div className="mt-8 p-6 bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-100 dark:border-emerald-900/20 rounded-3xl flex items-start gap-4">
                <ShieldCheck className="text-emerald-600 mt-1 shrink-0" size={24} />
                <div>
                    <h4 className="text-emerald-700 dark:text-emerald-400 text-xs font-black uppercase tracking-widest mb-2">Examiner Audit Protocol</h4>
                    <p className="text-sm text-emerald-800/80 dark:text-emerald-300/80 leading-relaxed font-mono whitespace-pre-wrap">{auditText}</p>
                </div>
            </div>
        )
    }

    const renderContent = (content) => {
        const auditIndex = content.indexOf('[EXAMINER AUDIT]')
        const cleanContent = auditIndex !== -1 ? content.substring(0, auditIndex) : content

        return cleanContent.split('\n').map((line, i) => {
            if (line.match(/^REASON \d:|^POINT:|^INTRODUCTION:|^AGREE SECTION:|^DISAGREE SECTION:|^FINAL JUDGEMENT:/i)) {
                return (
                    <div key={i} className="mt-6 mb-3 p-4 bg-[var(--primary-purple-light)]/10 border-l-4 border-[var(--primary-purple)] rounded-r-2xl">
                        <span className="text-xs font-black text-[var(--primary-purple)] uppercase tracking-[0.2em]">{line}</span>
                    </div>
                )
            }
            if (line.match(/^EVIDENCE:/i)) {
                return (
                    <div key={i} className="mt-3 pl-6 py-2 border-l-2 border-[var(--accent-gold)]/30 flex items-start gap-3">
                        <Award size={16} className="text-[var(--accent-gold)] mt-1 shrink-0" />
                        <span className="text-md text-[var(--text-dark)] font-bold"><span className="text-[var(--accent-gold)] font-black italic">HISTORICAL DATA:</span> {line.replace(/EVIDENCE:/i, '')}</span>
                    </div>
                )
            }
            if (line.match(/^EXPLANATION:/i)) {
                return (
                    <div key={i} className="mt-3 pl-6 py-2 border-l-2 border-[var(--primary-purple-light)]/20 flex items-start gap-3 text-md text-[var(--text-muted)] font-medium leading-relaxed italic">
                        <Brain size={16} className="text-[var(--primary-purple)] mt-1 shrink-0" />
                        <span><span className="text-[var(--primary-purple)] font-black not-italic uppercase text-[10px] tracking-widest">Syllabic Analysis:</span> {line.replace(/EXPLANATION:/i, '')}</span>
                    </div>
                )
            }
            if (line.startsWith('###')) return <h4 key={i} className="text-2xl font-black text-[var(--primary-purple)] mt-10 mb-6 tracking-tighter">{line.replace('###', '')}</h4>
            return line ? <p key={i} className="mb-4 text-[var(--text-dark)] text-lg leading-relaxed font-medium">{line}</p> : <div key={i} className="h-4" />
        })
    }

    return (
        <div className="h-screen bg-[var(--bg-cream)] flex flex-col md:flex-row overflow-hidden font-sans transition-colors duration-500">
            {/* Sidebar - Mark Schemes & Reference */}
            <aside className="hidden lg:flex w-[400px] bg-[var(--bg-card)] border-r border-[var(--border-color)] flex-col p-8 overflow-y-auto custom-scrollbar transition-colors duration-500">
                <div className="flex items-center gap-4 mb-12">
                    <div className="p-3 bg-[var(--primary-purple)] rounded-[1.5rem] shadow-2xl shadow-purple-900/20">
                        <BookOpen className="text-white dark:text-[#0f0a1e]" size={32} />
                    </div>
                    <div>
                        <h1 className="text-2xl font-black text-[var(--primary-purple)] tracking-tighter">EXAMINER</h1>
                        <p className="text-[10px] font-black uppercase tracking-widest text-[var(--accent-gold)]">Syllabus 2059/01</p>
                    </div>
                </div>

                <div className="space-y-10">
                    <div>
                        <h3 className="text-[10px] font-black text-[var(--text-muted)] uppercase tracking-[3px] mb-6 flex items-center gap-2">
                            Marking Protocol <ChevronRight size={12} className="text-[var(--accent-gold)]" />
                        </h3>
                        <div className="space-y-4">
                            {[4, 7, 14].map(m => (
                                <div key={m}
                                    onClick={() => setSelectedMarks(m)}
                                    className={`p-6 rounded-[2rem] border-2 transition-all cursor-pointer ${selectedMarks === m ? 'bg-[var(--primary-purple)] border-[var(--primary-purple)] text-white dark:text-[#0f0a1e] shadow-2xl shadow-purple-900/10' : 'bg-[var(--bg-card)] border-[var(--border-color)] opacity-60 hover:opacity-100 hover:border-[var(--primary-purple-light)]'}`}
                                >
                                    <div className="flex justify-between items-center mb-3">
                                        <span className="text-xl font-black tracking-tighter">{m} Mark Scripts</span>
                                        <Award size={20} className={selectedMarks === m ? 'text-[var(--accent-gold)]' : 'text-[var(--border-color)]'} />
                                    </div>
                                    <p className={`text-xs font-medium leading-relaxed ${selectedMarks === m ? 'text-white/70 dark:text-[#0f0a1e]/70' : 'text-[var(--text-muted)]'}`}>
                                        {m === 4 && "Requires 2 precise PEEL paragraphs. Factual depth (dates/names) is critical for L3-L4."}
                                        {m === 7 && "3 high-impact Analytical paragraphs. Focused on consequences and historical impact."}
                                        {m === 14 && "Full evaluation essay. Balanced debate + sustained judgement across syllabus themes."}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="p-8 bg-[var(--bg-card)] border-2 border-dashed border-[var(--border-color)] rounded-[2.5rem] relative overflow-hidden group">
                        <div className="absolute -top-10 -right-10 w-24 h-24 bg-[var(--primary-purple-light)]/5 rounded-full group-hover:scale-150 transition-transform"></div>
                        <div className="relative z-10">
                            <div className="flex items-center gap-3 mb-4 text-[var(--accent-gold)]">
                                <Sparkle size={20} />
                                <span className="text-[10px] font-black uppercase tracking-widest">Examiner Wisdom</span>
                            </div>
                            <p className="text-sm text-[var(--text-dark)] leading-relaxed font-bold italic">
                                "{lastWisdom}"
                            </p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Chat Area */}
            <main className="flex-1 flex flex-col relative bg-transparent overflow-hidden">
                {/* Header */}
                <header className="h-24 border-b border-[var(--border-color)] flex items-center justify-between px-10 bg-[var(--bg-card)]/70 backdrop-blur-2xl z-20 transition-colors duration-500">
                    <div className="flex items-center gap-6">
                        <button onClick={onBack} className="p-3 hover:bg-[var(--primary-purple-light)]/10 rounded-2xl transition-all text-[var(--primary-purple)] group">
                            <ChevronLeft size={24} className="group-hover:-translate-x-1 transition-transform" />
                        </button>
                        <div className="h-10 w-[1px] bg-[var(--border-color)] mx-1"></div>
                        <div>
                            <h2 className="text-[11px] font-black text-[var(--text-muted)] uppercase tracking-[4px]">Pakistan History Specialist</h2>
                            <p className="text-[10px] font-black text-emerald-600 flex items-center gap-2 uppercase tracking-tighter mt-1">
                                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
                                Neural Marking Model v2.4 Online
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="hidden sm:flex bg-[var(--primary-purple-light)]/10 rounded-2xl p-1.5 border border-[var(--border-color)]">
                            {[4, 7, 14].map(m => (
                                <button
                                    key={m}
                                    onClick={() => setSelectedMarks(m)}
                                    className={`px-6 py-2 rounded-xl text-xs font-black transition-all ${selectedMarks === m ? 'bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] shadow-xl' : 'text-[var(--text-muted)] hover:text-[var(--primary-purple)]'}`}
                                >
                                    {m}M
                                </button>
                            ))}
                        </div>
                        <div className="w-12 h-12 rounded-2xl bg-[var(--primary-purple)] flex items-center justify-center text-white dark:text-[#0f0a1e] border-2 border-[var(--primary-purple-light)]/20 shadow-xl overflow-hidden">
                            <User size={24} />
                        </div>
                    </div>
                </header>

                <div className="flex-1 overflow-y-auto p-8 md:p-14 space-y-10 custom-scrollbar">
                    {messages.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto space-y-8">
                            <div className="w-32 h-32 rounded-[3rem] bg-[var(--bg-card)] border border-[var(--border-color)] flex items-center justify-center text-[var(--primary-purple)] shadow-2xl shadow-purple-900/5 dark:shadow-black/20">
                                <Sparkles size={64} className="animate-pulse" />
                            </div>
                            <div className="space-y-4">
                                <h3 className="text-3xl font-black text-[var(--primary-purple)] uppercase tracking-[0.2em]">History Engine</h3>
                                <p className="text-lg font-medium text-[var(--text-muted)] leading-relaxed">Select your question magnitude (4, 7, 14) and allow the AI Examiner to generate high-mark model responses.</p>
                            </div>
                            <div className="flex flex-wrap justify-center gap-3">
                                {["Looming decline of Mughals?", "Why was Congress formed?", "Sutlej/Ravi water treaty impact?"].map((t, i) => (
                                    <button key={i} onClick={() => { setQuery(t); if (selectedMarks === null) setSelectedMarks(4); }} className="px-6 py-3 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl text-xs font-black text-[var(--primary-purple)] hover:border-[var(--primary-purple)] transition-all uppercase tracking-widest shadow-sm">
                                        {t}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    <AnimatePresence>
                        {messages.map((msg, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div className={`w-full lg:max-w-[85%] rounded-[3rem] p-10 shadow-xl ${msg.role === 'user' ? 'bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] shadow-purple-900/20' : 'bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-dark)] shadow-purple-900/5 dark:shadow-black/20'}`}>
                                    {msg.role === 'ai' && (
                                        <div className="flex items-center gap-4 mb-8 text-[11px] font-black uppercase tracking-[0.3em] text-[var(--accent-gold)] border-b border-[var(--border-color)] pb-6">
                                            <Brain size={18} /> Cambridge Examiner Core (v2.4)
                                        </div>
                                    )}
                                    <div className="prose prose-purple dark:prose-invert max-w-none">
                                        {msg.role === 'ai' ? renderContent(msg.content) : <p className="text-xl font-bold leading-relaxed">{msg.content}</p>}
                                    </div>
                                    {msg.role === 'ai' && renderAudit(msg.content)}
                                    {msg.role === 'user' && (
                                        <div className="mt-8 pt-6 border-t border-white/10 flex justify-end">
                                            <span className="text-[10px] font-black uppercase tracking-[0.2em] opacity-60 border border-white/20 px-4 py-2 rounded-full bg-white/10">{msg.marks} Marks Allocated</span>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                    {isAnalyzing && (
                        <div className="flex justify-start">
                            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-[3rem] p-10 flex items-center gap-6 shadow-xl shadow-purple-900/5 dark:shadow-black/20">
                                <div className="flex gap-2">
                                    <div className="w-3 h-3 bg-[var(--primary-purple)] rounded-full animate-bounce [animation-delay:-0.3s]" />
                                    <div className="w-3 h-3 bg-[var(--accent-gold)] rounded-full animate-bounce [animation-delay:-0.15s]" />
                                    <div className="w-3 h-3 bg-[var(--primary-purple)] rounded-full animate-bounce" />
                                </div>
                                <div className="space-y-1">
                                    <span className="text-sm font-black text-[var(--primary-purple)] uppercase tracking-[0.3em] block">Analyzing Sources</span>
                                    <span className="text-[10px] font-black text-[var(--accent-gold)] uppercase tracking-widest block">Generating examiner-aligned script...</span>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={chatEndRef} />
                </div>

                {/* Input Controls */}
                <div className="p-10 bg-[var(--bg-card)]/50 backdrop-blur-3xl border-t border-[var(--border-color)] space-y-6 transition-colors duration-500">
                    {selectedMarks === null && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-[var(--accent-gold)] text-white dark:text-[#0f0a1e] rounded-3xl p-6 flex items-center gap-4 shadow-2xl shadow-yellow-900/20"
                        >
                            <AlertTriangle size={24} className="shrink-0" />
                            <p className="text-sm font-black uppercase tracking-widest leading-relaxed">Initialize Marker Specification (4, 7, 14) to activate neural input.</p>
                            <div className="flex gap-2 ml-auto">
                                {[4, 7, 14].map(m => (
                                    <button key={m} onClick={() => setSelectedMarks(m)} className="px-6 py-3 bg-white text-[var(--accent-gold)] text-[10px] font-black rounded-2xl hover:scale-105 transition-all uppercase">
                                        {m}M SET
                                    </button>
                                ))}
                            </div>
                        </motion.div>
                    )}

                    <div className={`relative group transition-all duration-500 scale-100 ${selectedMarks === null ? 'pointer-events-none opacity-20 blur-sm' : 'opacity-100'}`}>
                        <div className="absolute inset-x-0 -top-px h-[2px] bg-gradient-to-r from-transparent via-[var(--primary-purple)]/30 to-transparent" />
                        <textarea
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault()
                                    handleAsk()
                                }
                            }}
                            placeholder={selectedMarks ? `Draft your ${selectedMarks}-mark investigation query...` : "Select marking specification first"}
                            className="w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-[2.5rem] p-8 pr-24 h-24 text-lg focus:outline-none focus:border-[var(--primary-purple)] focus:ring-8 focus:ring-[var(--primary-purple-light)]/5 transition-all shadow-2xl shadow-purple-900/5 dark:shadow-black/20 resize-none placeholder:text-[var(--primary-purple-light)]/40 font-bold text-[var(--primary-purple)]"
                        />
                        <button
                            onClick={handleAsk}
                            disabled={isAnalyzing || !query.trim() || selectedMarks === null}
                            className="absolute right-6 bottom-6 p-5 rounded-[1.5rem] bg-[var(--primary-purple)] hover:bg-[var(--primary-purple-light)] text-white dark:text-[#0f0a1e] transition-all shadow-2xl shadow-purple-900/40 dark:shadow-black/60 active:scale-90 disabled:opacity-0 disabled:scale-50 disabled:rotate-45"
                        >
                            <Send size={24} />
                        </button>
                    </div>

                    <div className="flex gap-4 overflow-x-auto pb-4 custom-scrollbar lg:justify-center">
                        {[
                            "Looming decline of Mughals?",
                            "Why was Congress formed?",
                            "Sutlej/Ravi water treaty impact?",
                            "Sir Syed's educational role?"
                        ].map((suggestion, i) => (
                            <button
                                key={i}
                                onClick={() => setQuery(suggestion)}
                                disabled={selectedMarks === null}
                                className="whitespace-nowrap px-6 py-2.5 rounded-full bg-[var(--bg-card)] border border-[var(--border-color)] text-[10px] font-black text-[var(--text-muted)] hover:text-[var(--primary-purple)] hover:border-[var(--primary-purple)] hover:shadow-xl transition-all uppercase tracking-widest disabled:opacity-0"
                            >
                                {suggestion}
                            </button>
                        ))}
                    </div>
                </div>
            </main>
        </div>
    )
}
