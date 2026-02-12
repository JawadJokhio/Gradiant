import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Camera, Upload, ArrowLeft, Send, CheckCircle2, Copy, RefreshCw, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

interface VisionAnsweringProps {
    onBack: () => void;
    initialSubject?: string;
}

export default function VisionAnswering({ onBack, initialSubject }: VisionAnsweringProps) {
    const { token } = useAuth()
    const [selectedImage, setSelectedImage] = useState<string | null>(null)
    const [imageFile, setImageFile] = useState<File | null>(null)
    const [subject] = useState(initialSubject || 'history')
    const [marks, setMarks] = useState(4)
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [answer, setAnswer] = useState<string | null>(null)

    const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) {
            setImageFile(file)
            const reader = new FileReader()
            reader.onload = (event) => setSelectedImage(event.target?.result as string)
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
            const response = await fetch('http://127.0.0.1:8000/ask-ai', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData,
            })
            const data = await response.json()
            setAnswer(data.answer)
        } catch (error) {
            console.error("Analysis error:", error)
            setAnswer("**Error:** Failed to connect to the AI engine. Please ensure the backend is running.\n\n### Sample Marking Scheme Answer (Simulation)\n- **Point 1:** Identifying the key historical event shown.\n- **Explanation:** Detailing the impact on the subcontinent (2 marks).\n- **Context:** Linking to the wider O-Level syllabus requirements.")
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
                        <Camera size={18} className="text-indigo-400" /> Vision Scanner
                    </h2>
                </div>

                <div className="flex items-center gap-3">
                    <div className={`px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-black uppercase tracking-widest`}>
                        {subject}
                    </div>
                </div>

                <div className="flex items-center gap-2 bg-slate-800 border border-white/10 rounded-lg px-2 py-1">
                    <span className="text-[10px] font-black text-slate-500 uppercase">Marks</span>
                    <select
                        value={marks}
                        onChange={(e) => setMarks(Number(e.target.value))}
                        className="bg-transparent text-xs font-bold focus:outline-none text-indigo-400 cursor-pointer"
                    >
                        {subject === 'history' ? (
                            [3, 4, 5, 7, 10, 14].map(m => <option key={m} value={m} className="bg-slate-900">{m}</option>)
                        ) : (
                            [1, 2, 3, 4, 5, 6, 8, 10, 12, 14].map(m => <option key={m} value={m} className="bg-slate-900">{m}</option>)
                        )}
                    </select>
                </div>
            </header>

            <main className="flex-1 flex flex-col lg:flex-row divide-y lg:divide-y-0 lg:divide-x divide-white/5 overflow-y-auto lg:overflow-hidden custom-scrollbar">
                {/* Upload/Preview Section */}
                <section className="flex-1 flex flex-col p-6 overflow-y-auto custom-scrollbar bg-slate-900/40 min-h-0">
                    <div className="flex-1 flex flex-col items-center justify-center">
                        <AnimatePresence mode="wait">
                            {!selectedImage ? (
                                <motion.div
                                    key="upload"
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.9 }}
                                    className="w-full max-w-md aspect-video border-2 border-dashed border-white/10 rounded-3xl flex flex-col items-center justify-center gap-4 group hover:border-indigo-500/50 hover:bg-indigo-500/5 transition-all cursor-pointer relative"
                                >
                                    <input type="file" className="absolute inset-0 opacity-0 cursor-pointer" onChange={handleImageUpload} accept="image/*" />
                                    <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center group-hover:bg-indigo-600 transition-colors">
                                        <Upload size={24} className="text-slate-400 group-hover:text-white" />
                                    </div>
                                    <div className="text-center">
                                        <p className="font-bold">Click to scan image</p>
                                        <p className="text-xs text-slate-500">Upload a picture of a past paper question</p>
                                    </div>
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="preview"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="w-full flex flex-col gap-4"
                                >
                                    <div className="relative w-full rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-black">
                                        <img src={selectedImage} alt="Preview" className="w-full h-auto" />
                                        <button
                                            onClick={() => { setSelectedImage(null); setAnswer(null); }}
                                            className="absolute top-4 right-4 p-2 bg-black/50 backdrop-blur-md rounded-full hover:bg-rose-600 transition-colors"
                                        >
                                            <X size={18} />
                                        </button>
                                    </div>
                                    <button
                                        onClick={handleAnalyze}
                                        disabled={isAnalyzing}
                                        className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 active:scale-[0.98] transition-all disabled:opacity-50"
                                    >
                                        {isAnalyzing ? (
                                            <>
                                                <RefreshCw size={18} className="animate-spin" />
                                                Analyzing with AI Answering Engine...
                                            </>
                                        ) : (
                                            <>
                                                <Send size={18} />
                                                Generate Marking Scheme Answer
                                            </>
                                        )}
                                    </button>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </section>

                {/* Answer Section */}
                <section className="w-full lg:w-[450px] flex flex-col bg-slate-950 overflow-hidden min-h-0 h-full">
                    <div className="p-6 border-b border-white/5 flex items-center justify-between">
                        <h3 className="text-xs font-black uppercase tracking-widest text-slate-500">AI Generated Solution</h3>
                        {answer && (
                            <button className="p-2 hover:bg-white/5 rounded-lg text-slate-400 hover:text-white transition-colors" title="Copy to clipboard">
                                <Copy size={16} />
                            </button>
                        )}
                    </div>

                    <div className="flex-1 overflow-y-auto p-6 custom-scrollbar text-[15px] leading-relaxed max-h-[calc(100vh-160px)]">
                        {isAnalyzing ? (
                            <div className="space-y-6 animate-pulse">
                                <div className="h-4 bg-white/5 rounded w-3/4"></div>
                                <div className="space-y-3">
                                    <div className="h-4 bg-white/5 rounded"></div>
                                    <div className="h-4 bg-white/5 rounded"></div>
                                    <div className="h-4 bg-white/5 rounded w-5/6"></div>
                                </div>
                                <div className="h-4 bg-white/5 rounded w-1/2"></div>
                            </div>
                        ) : answer ? (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="space-y-4"
                            >
                                <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold mb-4">
                                    <CheckCircle2 size={14} /> O-Level Expert Analysis Ready
                                </div>
                                <div className="prose prose-invert max-w-none">
                                    {answer.split('\n').map((line, i) => {
                                        if (line.startsWith('### [1]')) return (
                                            <div key={i} className="mt-6 mb-4 p-3 bg-amber-500/10 border-l-4 border-amber-500 rounded-r-lg">
                                                <h4 className="text-lg font-black text-amber-400 uppercase tracking-tighter">1. Marking Scheme Breakdown</h4>
                                            </div>
                                        )
                                        if (line.startsWith('### [2]')) return (
                                            <div key={i} className="mt-8 mb-4 p-3 bg-indigo-500/10 border-l-4 border-indigo-500 rounded-r-lg">
                                                <h4 className="text-lg font-black text-indigo-400 uppercase tracking-tighter">2. Perfect O-Level Script</h4>
                                            </div>
                                        )
                                        if (line.startsWith('### [3]')) return (
                                            <div key={i} className="mt-10 mb-4 p-3 bg-rose-500/10 border-l-4 border-rose-500 rounded-r-lg">
                                                <h4 className="text-lg font-black text-rose-400 uppercase tracking-tighter">3. Common Pitfalls (Mark-Loss Areas)</h4>
                                            </div>
                                        )
                                        if (line.startsWith('### [4]')) return (
                                            <div key={i} className="mt-10 mb-4 p-3 bg-purple-500/10 border-l-4 border-purple-500 rounded-r-lg">
                                                <h4 className="text-lg font-black text-purple-400 uppercase tracking-tighter">4. Tutor Wisdom</h4>
                                            </div>
                                        )
                                        if (line.startsWith('###')) return <h4 key={i} className="text-lg font-bold text-white mt-6 mb-3">{line.replace('###', '')}</h4>
                                        if (line.startsWith('- **')) return <p key={i} className="mb-2 pl-4 border-l-2 border-indigo-500/30 font-medium text-slate-200">{line.replace('- ', '')}</p>
                                        return <p key={i} className={`${line ? 'mb-4' : 'h-2'} text-slate-400`}>{line}</p>
                                    })}
                                </div>
                            </motion.div>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-30">
                                <div className="p-4 rounded-full bg-white/5">
                                    <Camera size={40} />
                                </div>
                                <p className="text-sm font-medium">Upload a question image to begin AI analysis</p>
                            </div>
                        )}
                    </div>

                    {answer && (
                        <div className="p-6 bg-slate-900 border-t border-white/5 space-y-4">
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Ask a follow-up question..."
                                    className="w-full bg-slate-800 border border-white/10 rounded-xl py-3 px-4 pr-12 text-sm focus:outline-none focus:border-indigo-500/50"
                                />
                                <button className="absolute right-2 top-2 p-1.5 bg-indigo-600 rounded-lg hover:bg-indigo-500 transition-colors">
                                    <Send size={16} />
                                </button>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                        <div className="h-full bg-indigo-500 w-[94%] shadow-[0_0_10px_rgba(99,102,241,0.5)]"></div>
                                    </div>
                                    <span className="text-[10px] font-bold text-indigo-400">94% Confidence</span>
                                </div>
                                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Interactive Mode Active</span>
                            </div>
                        </div>
                    )}
                </section>
            </main>
        </div >
    )
}
