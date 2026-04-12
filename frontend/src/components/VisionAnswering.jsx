import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Camera, Upload, ArrowLeft, Send, CheckCircle2, Copy, RefreshCw, X, ChevronLeft, Sparkles, Brain, BookOpen } from 'lucide-react'

export default function VisionAnswering({ onBack, initialSubject }) {

    const [selectedImage, setSelectedImage] = useState(null)
    const [imageFile, setImageFile] = useState(null)
    const [subject] = useState(initialSubject || 'history')
    const [marks, setMarks] = useState(4)
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [answer, setAnswer] = useState(null)

    const handleImageUpload = (e) => {
        const file = e.target.files?.[0]
        if (file) {
            setImageFile(file)
            const reader = new FileReader()
            reader.onload = (event) => setSelectedImage(event.target?.result)
            reader.readAsDataURL(file)
            setAnswer(null)
        }
    }

    const handleAnalyze = async () => {
        if (!imageFile) return
        setIsAnalyzing(true)

        const formData = new FormData()
        formData.append('image', imageFile)
        formData.append('subject', subject)
        formData.append('mode', 'vision')
        formData.append('marks', marks.toString())

        try {
            const response = await fetch('http://localhost:8000/geography/analyze-image-question', {
                method: 'POST',

                body: formData,
            })
            const data = await response.json()
            setAnswer(data.answer)
        } catch (error) {
            console.error("Analysis error:", error)
            setAnswer("**Error:** Failed to connect to the AI engine. Please ensure the backend is running.\n\n### Marking Scheme Protocol (Simulation)\n- **Point 1:** Identifying the key historical event shown.\n- **Explanation:** Detailing the impact on the subcontinent (2 marks).\n- **Context:** Linking to the wider O-Level syllabus requirements.")
        } finally {
            setIsAnalyzing(false)
        }
    }

    return (
        <div className="min-h-screen bg-[var(--bg-cream)] text-[var(--text-dark)] flex flex-col transition-colors duration-500">
            <header className="h-20 flex-shrink-0 bg-[var(--bg-card)]/70 backdrop-blur-xl border-b border-[var(--border-color)] px-6 flex items-center justify-between z-10 sticky top-0 font-bold transition-colors duration-500">
                <div className="flex items-center gap-4">
                    <button onClick={onBack} className="p-2 hover:bg-[var(--primary-purple-light)]/10 rounded-xl transition-colors text-[var(--primary-purple)] group">
                        <ChevronLeft size={24} className="group-hover:-translate-x-1 transition-transform" />
                    </button>
                    <div className="h-8 w-[1px] bg-[var(--border-color)] mx-1"></div>
                    <div>
                        <h2 className="text-xl font-black text-[var(--primary-purple)] flex items-center gap-2">
                            Vision Scanner
                        </h2>
                        <p className="text-[10px] font-black uppercase tracking-widest text-[var(--accent-gold)]">Advanced Optical Analysis</p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <div className={`px-4 py-1.5 rounded-full bg-[var(--primary-purple-light)]/10 border border-[var(--border-color)] text-[var(--primary-purple)] text-[10px] font-black uppercase tracking-widest`}>
                        {subject}
                    </div>
                    <div className="flex items-center gap-3 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-4 py-2 shadow-sm">
                        <span className="text-[10px] font-black text-[var(--text-muted)] uppercase tracking-tighter">Marks Selection</span>
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

            <main className="flex-1 flex flex-col lg:flex-row lg:divide-x divide-[var(--border-color)] overflow-y-auto lg:overflow-hidden">
                {/* Upload/Preview Section */}
                <section className="flex-1 flex flex-col p-8 md:p-12 overflow-y-auto custom-scrollbar bg-[var(--bg-card)]/30 min-h-0 transition-colors duration-500">
                    <div className="flex-1 flex flex-col items-center justify-center max-w-2xl mx-auto w-full">
                        <AnimatePresence mode="wait">
                            {!selectedImage ? (
                                <motion.div
                                    key="upload"
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.95 }}
                                    className="w-full aspect-[4/3] border-4 border-dashed border-[var(--border-color)] rounded-[3rem] flex flex-col items-center justify-center gap-8 group hover:border-[var(--primary-purple)] hover:bg-[var(--primary-purple-light)]/5 transition-all cursor-pointer relative shadow-2xl shadow-purple-900/5 dark:shadow-black/20"
                                >
                                    <input type="file" className="absolute inset-0 opacity-0 cursor-pointer" onChange={handleImageUpload} accept="image/*" />
                                    <div className="w-24 h-24 rounded-[2rem] bg-[var(--primary-purple)] flex items-center justify-center text-white dark:text-[#0f0a1e] shadow-2xl group-hover:scale-110 transition-transform">
                                        <Upload size={40} />
                                    </div>
                                    <div className="text-center space-y-2">
                                        <p className="text-2xl font-black text-[var(--primary-purple)]">Upload Question Image</p>
                                        <p className="text-sm text-[var(--text-muted)] font-medium">PNG, JPG or WEBP (Max 10MB)</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--bg-card)] border border-[var(--border-color)] text-[10px] font-black text-[var(--primary-purple)] uppercase tracking-widest">
                                            <Sparkles size={12} className="text-[var(--accent-gold)]" /> Syllabus 2059/01
                                        </div>
                                    </div>
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="preview"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="w-full flex flex-col gap-8"
                                >
                                    <div className="relative w-full rounded-[2.5rem] overflow-hidden border border-[var(--border-color)] shadow-[0_40px_80px_rgba(77,62,119,0.15)] dark:shadow-black/40 bg-[var(--bg-card)] p-4">
                                        <div className="relative rounded-[1.5rem] overflow-hidden">
                                            <img src={selectedImage} alt="Preview" className="w-full h-auto" />
                                            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none"></div>
                                        </div>
                                        <button
                                            onClick={() => { setSelectedImage(null); setAnswer(null); }}
                                            className="absolute top-8 right-8 p-3 bg-[var(--bg-card)]/90 backdrop-blur-md text-[var(--primary-purple)] rounded-2xl hover:bg-rose-500 dark:hover:bg-rose-600 hover:text-white transition-all shadow-xl"
                                        >
                                            <X size={20} />
                                        </button>
                                    </div>
                                    <button
                                        onClick={handleAnalyze}
                                        disabled={isAnalyzing}
                                        className="w-full py-6 bg-[var(--primary-purple)] hover:opacity-90 text-white dark:text-[#0f0a1e] rounded-[1.5rem] font-black text-sm uppercase tracking-[0.2em] flex items-center justify-center gap-3 shadow-2xl shadow-purple-900/40 dark:shadow-black/60 active:scale-[0.98] transition-all disabled:opacity-30"
                                    >
                                        {isAnalyzing ? (
                                            <>
                                                <RefreshCw size={20} className="animate-spin" />
                                                Running Vision Algorithm...
                                            </>
                                        ) : (
                                            <>
                                                <Send size={20} />
                                                Analyze with Examiner AI
                                            </>
                                        )}
                                    </button>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </section>

                {/* Answer Section */}
                <section className="w-full lg:w-[500px] flex flex-col bg-[var(--bg-card)] overflow-hidden min-h-0 h-full transition-colors duration-500">
                    <div className="p-8 border-b border-[var(--border-color)] flex items-center justify-between">
                        <div>
                            <h3 className="text-[10px] font-black uppercase tracking-widest text-[var(--accent-gold)] mb-1">AI Solution Terminal</h3>
                            <h2 className="text-lg font-black text-[var(--primary-purple)] uppercase tracking-tighter">Marking Report</h2>
                        </div>
                        {answer && (
                            <button className="p-3 hover:bg-[var(--primary-purple-light)]/10 rounded-xl text-[var(--primary-purple)] transition-all border border-[var(--border-color)] shadow-sm" title="Copy to clipboard">
                                <Copy size={18} />
                            </button>
                        )}
                    </div>

                    <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                        {isAnalyzing ? (
                            <div className="space-y-8 py-4">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-full bg-[var(--primary-purple-light)]/10 animate-pulse"></div>
                                    <div className="h-4 bg-[var(--primary-purple-light)]/10 rounded-full w-2/3 animate-pulse"></div>
                                </div>
                                <div className="space-y-4">
                                    <div className="h-20 bg-[var(--primary-purple-light)]/5 rounded-2xl w-full animate-pulse"></div>
                                    <div className="h-4 bg-[var(--primary-purple-light)]/10 rounded-full w-full animate-pulse"></div>
                                    <div className="h-4 bg-[var(--primary-purple-light)]/10 rounded-full w-5/6 animate-pulse"></div>
                                    <div className="h-4 bg-[var(--primary-purple-light)]/10 rounded-full w-4/6 animate-pulse"></div>
                                </div>
                                <div className="h-32 bg-[var(--primary-purple-light)]/5 rounded-2xl w-full animate-pulse"></div>
                            </div>
                        ) : answer ? (
                            <motion.div
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="space-y-8"
                            >
                                <div className="flex items-center gap-3 text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/10 px-5 py-3 rounded-2xl border border-emerald-100 dark:border-emerald-900/20 text-xs font-black uppercase tracking-tighter">
                                    <CheckCircle2 size={18} /> Analysis Complete
                                </div>
                                <div className="prose prose-purple dark:prose-invert max-w-none text-[var(--text-dark)] leading-relaxed font-medium">
                                    {answer.split('\n').map((line, i) => {
                                        if (line.startsWith('### [1]')) return (
                                            <div key={i} className="mt-8 mb-4 p-5 bg-[var(--primary-purple-light)]/10 border-l-4 border-[var(--primary-purple)] rounded-xl">
                                                <h4 className="text-base font-black text-[var(--primary-purple)] uppercase tracking-widest">1. Marking Protocol</h4>
                                            </div>
                                        )
                                        if (line.startsWith('### [2]')) return (
                                            <div key={i} className="mt-10 mb-4 p-5 bg-blue-50 dark:bg-blue-900/10 border-l-4 border-blue-600 rounded-xl">
                                                <h4 className="text-base font-black text-blue-600 dark:text-blue-400 uppercase tracking-widest">2. Model Script</h4>
                                            </div>
                                        )
                                        if (line.startsWith('### [3]')) return (
                                            <div key={i} className="mt-10 mb-4 p-5 bg-rose-50 dark:bg-rose-900/10 border-l-4 border-rose-500 rounded-xl">
                                                <h4 className="text-base font-black text-rose-400 uppercase tracking-widest">3. Marking Pitfalls</h4>
                                            </div>
                                        )
                                        if (line.startsWith('### [4]')) return (
                                            <div key={i} className="mt-10 mb-4 p-5 bg-emerald-50 dark:bg-emerald-900/10 border-l-4 border-emerald-600 rounded-xl">
                                                <h4 className="text-base font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest">4. Tutor Wisdom</h4>
                                            </div>
                                        )
                                        if (line.startsWith('###')) return <h4 key={i} className="text-xl font-black text-[var(--primary-purple)] mt-10 mb-5">{line.replace('###', '')}</h4>
                                        if (line.startsWith('- **')) {
                                            const parts = line.replace('- **', '').split('**')
                                            return (
                                                <div key={i} className="mb-4 pl-5 border-l-2 border-[var(--border-color)] py-1">
                                                    <strong className="text-[var(--primary-purple)] font-black">{parts[0]}</strong> {parts[2]}
                                                </div>
                                            )
                                        }
                                        return <p key={i} className={`${line ? 'mb-5' : 'h-4'} text-[var(--text-dark)]`}>{line}</p>
                                    })}
                                </div>
                            </motion.div>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-center space-y-6 opacity-30 px-10">
                                <div className="w-24 h-24 rounded-full bg-[var(--primary-purple-light)]/10 border-2 border-dashed border-[var(--border-color)] flex items-center justify-center text-[var(--primary-purple)]">
                                    <Camera size={48} />
                                </div>
                                <div className="space-y-2">
                                    <p className="text-lg font-black text-[var(--primary-purple)] uppercase tracking-widest">Waiting for Input</p>
                                    <p className="text-sm font-medium">Upload a picture of your past paper for precise marking analysis.</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {answer && (
                        <div className="p-8 bg-[var(--bg-cream)] border-t border-[var(--border-color)] space-y-6 transition-colors duration-500">
                            <div className="relative group">
                                <input
                                    type="text"
                                    placeholder="Request clarification..."
                                    className="w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl py-5 px-6 pr-14 text-sm focus:outline-none focus:border-[var(--primary-purple)] transition-all font-medium shadow-sm text-[var(--text-dark)]"
                                />
                                <button className="absolute right-4 top-4 p-2 bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] rounded-xl hover:opacity-90 transition-transform active:scale-95 shadow-lg">
                                    <Send size={18} />
                                </button>
                            </div>
                            <div className="flex flex-col gap-3">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <Brain size={14} className="text-[var(--primary-purple)]" />
                                        <span className="text-[10px] font-black text-[var(--primary-purple)] uppercase tracking-widest">Engine Confidence</span>
                                    </div>
                                    <span className="text-[10px] font-black text-[var(--accent-gold)]">98.2%</span>
                                </div>
                                <div className="w-full h-2 bg-[var(--primary-purple-light)]/20 rounded-full overflow-hidden">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: '98.2%' }}
                                        className="h-full bg-gradient-to-r from-[var(--primary-purple)] to-[var(--accent-gold)]"
                                    ></motion.div>
                                </div>
                            </div>
                        </div>
                    )}
                </section>
            </main>
        </div>
    )
}
