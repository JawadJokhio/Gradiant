import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Brain, BookOpen, User, Award, ShieldCheck, Info, Sparkles, ChevronRight, AlertTriangle } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function HistoryExaminer() {
    const { token } = useAuth()
    const [query, setQuery] = useState('')
    const [selectedMarks, setSelectedMarks] = useState<number | null>(null)
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [messages, setMessages] = useState<any[]>([])
    const chatEndRef = useRef<HTMLDivElement>(null)

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
            const response = await fetch('http://127.0.0.1:8000/ask-ai', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData,
            })
            const data = await response.json()
            setMessages(prev => [...prev, { role: 'ai', content: data.answer, marks: selectedMarks }])
        } catch (error) {
            setMessages(prev => [...prev, { role: 'ai', content: "Error connecting to Examiner Engine. Please ensure the backend is running.", isError: true }])
        } finally {
            setIsAnalyzing(false)
        }
    }

    const renderAudit = (content: string) => {
        const auditIndex = content.indexOf('[EXAMINER AUDIT]')
        if (auditIndex === -1) return null
        
        const auditText = content.substring(auditIndex + 16).trim()
        return (
            <div className="mt-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-start gap-3">
                <ShieldCheck className="text-emerald-400 mt-1 shrink-0" size={20} />
                <div>
                    <h4 className="text-emerald-400 text-xs font-black uppercase tracking-tighter mb-1">Examiner Audit Detail</h4>
                    <p className="text-sm text-emerald-100/80 leading-relaxed font-mono whitespace-pre-wrap">{auditText}</p>
                </div>
            </div>
        )
    }

    const renderContent = (content: string) => {
        const auditIndex = content.indexOf('[EXAMINER AUDIT]')
        const cleanContent = auditIndex !== -1 ? content.substring(0, auditIndex) : content

        return cleanContent.split('\n').map((line, i) => {
            if (line.match(/^REASON \d:|^POINT:|^INTRODUCTION:|^AGREE SECTION:|^DISAGREE SECTION:|^FINAL JUDGEMENT:/i)) {
                return (
                    <div key={i} className="mt-4 mb-2 p-3 bg-indigo-500/10 border-l-4 border-indigo-500 rounded-r-lg group">
                        <span className="text-xs font-black text-indigo-400 uppercase tracking-widest">{line}</span>
                    </div>
                )
            }
            if (line.match(/^EVIDENCE:/i)) {
                return (
                    <div key={i} className="mt-2 pl-4 py-1 border-l-2 border-amber-500/30 flex items-start gap-2">
                        <Award size={14} className="text-amber-400 mt-1 shrink-0" />
                        <span className="text-sm text-slate-300 font-medium"><span className="text-amber-400 font-bold">EVIDENCE:</span> {line.replace(/EVIDENCE:/i, '')}</span>
                    </div>
                )
            }
            if (line.match(/^EXPLANATION:/i)) {
                return (
                    <div key={i} className="mt-2 pl-4 py-1 border-l-2 border-cyan-500/30 flex items-start gap-2 text-sm text-slate-400 italic">
                        <Brain size={14} className="text-cyan-400 mt-1 shrink-0" />
                        <span><span className="text-cyan-400 font-bold not-italic">EXPLANATION:</span> {line.replace(/EXPLANATION:/i, '')}</span>
                    </div>
                )
            }
            if (line.startsWith('###')) return <h4 key={i} className="text-lg font-bold text-white mt-8 mb-4">{line.replace('###', '')}</h4>
            return line ? <p key={i} className="mb-3 text-slate-300 leading-relaxed">{line}</p> : <div key={i} className="h-2" />
        })
    }

    return (
        <div className="h-screen bg-slate-950 flex flex-col md:flex-row overflow-hidden font-sans">
            {/* Sidebar - Mark Schemes & Reference */}
            <aside className="hidden lg:flex w-80 bg-slate-900/50 border-r border-white/5 flex-col p-6 overflow-y-auto custom-scrollbar">
                <div className="flex items-center gap-3 mb-8">
                    <div className="p-2 bg-indigo-500 rounded-xl shadow-lg shadow-indigo-500/20">
                        <BookOpen className="text-white" size={24} />
                    </div>
                    <h1 className="text-xl font-black bg-gradient-to-r from-white to-slate-500 bg-clip-text text-transparent">EXAMINER</h1>
                </div>

                <div className="space-y-6">
                    <div>
                        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[2px] mb-4">Marking Criteria</h3>
                        <div className="space-y-2">
                            {[4, 7, 14].map(m => (
                                <div key={m} className={`p-3 rounded-2xl border transition-all ${selectedMarks === m ? 'bg-indigo-500/10 border-indigo-500/50' : 'bg-white/5 border-white/5 opacity-50'}`}>
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="text-xs font-bold">{m} Markers</span>
                                        <Award size={14} className={selectedMarks === m ? 'text-indigo-400' : 'text-slate-600'} />
                                    </div>
                                    <p className="text-[10px] text-slate-400 font-medium">
                                        {m === 4 && "Requires 2 PEEL paragraphs. Factual depth (dates/names) is critical."}
                                        {m === 7 && "3 Analytical paragraphs. Focused on consequences and impact."}
                                        {m === 14 && "Full evaluation essay. Balanced debate + sustained judgement."}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="p-4 bg-amber-500/5 border border-amber-500/10 rounded-2xl">
                        <div className="flex items-center gap-2 mb-2 text-amber-500">
                            <Info size={16} />
                            <span className="text-xs font-black uppercase tracking-widest">Tutor Wisdom</span>
                        </div>
                        <p className="text-[10px] text-amber-100/60 leading-relaxed italic">
                            "Focus on command words like 'Why' (4/7) and 'Describe' (4). For 14 marks, your judgement must match the evidence provided in the essay body."
                        </p>
                    </div>
                </div>
            </aside>

            {/* Main Chat Area */}
            <main className="flex-1 flex flex-col relative bg-slate-950/40">
                {/* Header */}
                <header className="h-20 border-b border-white/5 flex items-center justify-between px-8 bg-slate-950/80 backdrop-blur-xl z-20">
                    <div>
                        <h2 className="text-sm font-black text-slate-400 uppercase tracking-[3px]">Pakistan History</h2>
                        <p className="text-[10px] font-medium text-emerald-500 flex items-center gap-1.5 uppercase font-mono tracking-tighter">
                            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                            Examiner Simulation Engine Online
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="hidden sm:flex bg-slate-900 border border-white/5 rounded-full p-1">
                            {[4, 7, 14].map(m => (
                                <button
                                    key={m}
                                    onClick={() => setSelectedMarks(m)}
                                    className={`px-4 py-1.5 rounded-full text-xs font-black transition-all ${selectedMarks === m ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
                                >
                                    {m}M
                                </button>
                            ))}
                        </div>
                        <div className="w-8 h-8 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center">
                            <User size={16} className="text-slate-400" />
                        </div>
                    </div>
                </header>

                <div className="flex-1 overflow-y-auto p-4 md:p-10 space-y-8 custom-scrollbar">
                    {messages.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center opacity-20 text-center max-w-sm mx-auto">
                            <Sparkles size={64} className="mb-4" />
                            <h3 className="text-xl font-black uppercase tracking-[4px]">History Engine</h3>
                            <p className="text-xs font-medium mt-2">Select mark allocation above and input your query to generate a professional Cambridge script.</p>
                        </div>
                    )}

                    <AnimatePresence>
                        {messages.map((msg, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div className={`max-w-[85%] md:max-w-[75%] rounded-3xl p-6 shadow-2xl ${msg.role === 'user' ? 'bg-indigo-600 text-white shadow-indigo-500/20' : 'bg-slate-900/80 border border-white/5 text-slate-100 shadow-black/40'}`}>
                                    {msg.role === 'ai' && (
                                        <div className="flex items-center gap-2 mb-4 text-[10px] font-black uppercase tracking-widest text-indigo-400 border-b border-indigo-400/10 pb-2">
                                            <Brain size={14} /> Cambridge Examiner (History 2059)
                                        </div>
                                    )}
                                    <div className="whitespace-pre-wrap">
                                        {msg.role === 'ai' ? renderContent(msg.content) : msg.content}
                                    </div>
                                    {msg.role === 'ai' && renderAudit(msg.content)}
                                    {msg.role === 'user' && (
                                        <div className="mt-3 pt-2 border-t border-white/10 flex justify-end">
                                            <span className="text-[10px] font-black uppercase tracking-tighter opacity-70 border border-white/20 px-2 py-0.5 rounded-full">{msg.marks} Marks Allocated</span>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                    {isAnalyzing && (
                        <div className="flex justify-start">
                            <div className="bg-slate-900 border border-white/5 rounded-3xl p-6 flex items-center gap-4">
                                <div className="flex gap-1.5">
                                    <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                                    <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                                    <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" />
                                </div>
                                <span className="text-xs font-black text-indigo-400 uppercase tracking-widest animate-pulse">Analyzing Sources...</span>
                            </div>
                        </div>
                    )}
                    <div ref={chatEndRef} />
                </div>

                {/* Input Controls */}
                <div className="p-6 bg-slate-950/80 backdrop-blur-xl border-t border-white/5 space-y-4">
                    {selectedMarks === null && (
                        <motion.div 
                            initial={{ opacity: 0, y: 10 }} 
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-amber-500/10 border border-amber-500/20 rounded-2xl p-4 flex items-center gap-3 text-amber-400 shadow-2xl"
                        >
                            <AlertTriangle size={20} className="shrink-0" />
                            <p className="text-xs font-bold uppercase tracking-widest">Select Question Marks (4, 7, or 14) to enable intelligence input.</p>
                            <div className="flex gap-2 ml-auto">
                                {[4, 7, 14].map(m => (
                                    <button key={m} onClick={() => setSelectedMarks(m)} className="px-4 py-2 bg-amber-500 text-black text-[10px] font-black rounded-lg hover:bg-amber-400 active:scale-95 transition-all">
                                        {m}M
                                    </button>
                                ))}
                            </div>
                        </motion.div>
                    )}

                    <div className={`relative group transition-opacity duration-300 ${selectedMarks === null ? 'pointer-events-none opacity-40 grayscale' : 'opacity-100'}`}>
                        <div className="absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent" />
                        <textarea
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault()
                                    handleAsk()
                                }
                            }}
                            placeholder={selectedMarks ? `Type your ${selectedMarks}-mark history question...` : "Select marks above first"}
                            className="w-full bg-slate-900/50 border border-white/5 rounded-[2rem] p-6 pr-16 h-20 text-md focus:outline-none focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/5 transition-all shadow-2xl resize-none placeholder:text-slate-700 font-medium"
                        />
                        <button
                            onClick={handleAsk}
                            disabled={isAnalyzing || !query.trim() || selectedMarks === null}
                            className="absolute right-4 bottom-4 p-3.5 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-xl shadow-indigo-600/20 active:scale-95 disabled:opacity-0 disabled:scale-90 scale-100"
                        >
                            <Send size={20} />
                        </button>
                    </div>

                    <div className="flex gap-3 overflow-x-auto pb-2 custom-scrollbar">
                        {[
                            "Explain the main causes of the Mughal decline.",
                            "Why was the Simon Commission rejected?",
                            "Was the Khilafat Movement successful?",
                            "Evaluate the role of Sir Syed Ahmad Khan."
                        ].map((suggestion, i) => (
                            <button 
                                key={i} 
                                onClick={() => setQuery(suggestion)}
                                disabled={selectedMarks === null}
                                className="whitespace-nowrap px-4 py-2 rounded-full bg-white/5 border border-white/5 text-[10px] font-bold text-slate-500 hover:text-white hover:bg-white/10 hover:border-indigo-500/50 transition-all disabled:opacity-0"
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
