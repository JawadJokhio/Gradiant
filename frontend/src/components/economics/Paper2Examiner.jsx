import { useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import {
    AlertTriangle, ArrowLeft, BookOpen, CheckCircle, ChevronRight,
    FileText, Image as ImageIcon, Layers, RefreshCw, Target, Upload, X
} from 'lucide-react'

function sanitizeSvg(svg) {
    if (typeof svg !== 'string') return ''
    const trimmed = svg.trim()
    if (!trimmed.startsWith('<svg') || !trimmed.endsWith('</svg>')) return ''
    if (/<script|<\/script|foreignObject|on\w+=|javascript:/i.test(trimmed)) return ''
    return trimmed
}

function Paper2Result({ result }) {
    const parts = Array.isArray(result.detected_parts) ? result.detected_parts : []

    return (
        <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, ease: 'easeOut' }} className="space-y-5">
            <div className="flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                        <FileText size={20} className="text-emerald-400" />
                    </div>
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-widest text-emerald-400">Paper 2 Answer</p>
                        <p className="text-lg font-black text-[var(--primary-purple)]">Section {result.section || 'A'}</p>
                    </div>
                </div>
                <span className="px-3 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border bg-emerald-500/10 text-emerald-400 border-emerald-500/30">
                    {result.marks_source || 'Mark Aligned'}
                </span>
            </div>

            {parts.map((part, index) => (
                <div key={`${part.part || 'part'}-${index}`} className="p-5 rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)] space-y-4">
                    <div className="flex items-start justify-between gap-4">
                        <div>
                            <p className="text-[10px] font-black uppercase tracking-widest text-[var(--primary-purple)]">{part.part || `Part ${index + 1}`}</p>
                            {part.question && <p className="text-sm font-bold text-[var(--text-dark)] mt-1">{part.question}</p>}
                        </div>
                        {part.marks !== null && part.marks !== undefined && (
                            <span className="shrink-0 px-3 py-1 rounded-full bg-amber-500/10 text-amber-500 border border-amber-500/25 text-[10px] font-black uppercase tracking-widest">
                                {part.marks} marks
                            </span>
                        )}
                    </div>
                    <p className="text-sm leading-relaxed text-[var(--text-dark)] font-medium whitespace-pre-line">{part.answer}</p>
                    {sanitizeSvg(part.diagram_svg) && (
                        <div className="rounded-2xl border border-[var(--border-color)] bg-white p-4 overflow-x-auto space-y-3">
                            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Diagram</p>
                            <div
                                className="min-w-[360px] text-slate-900 [&_svg]:w-full [&_svg]:max-w-[720px] [&_svg]:h-auto [&_svg]:mx-auto"
                                dangerouslySetInnerHTML={{ __html: sanitizeSvg(part.diagram_svg) }}
                            />
                        </div>
                    )}
                </div>
            ))}

            {result.examiner_tip && (
                <div className="p-5 rounded-2xl border border-amber-500/25 bg-amber-500/5">
                    <p className="text-[10px] font-black uppercase tracking-widest text-amber-400 mb-3">Examiner Tip</p>
                    <p className="text-sm leading-relaxed text-[var(--text-dark)] font-medium">{result.examiner_tip}</p>
                </div>
            )}
        </motion.div>
    )
}

export default function Paper2Examiner({ onBack }) {
    const [section, setSection] = useState('A')
    const [inputMode, setInputMode] = useState('image')
    const [textQuery, setTextQuery] = useState('')
    const [note, setNote] = useState('')
    const [images, setImages] = useState([])
    const [isLoading, setIsLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)
    const fileRef = useRef()

    const readImagePreview = (file) => new Promise((resolve) => {
        const reader = new FileReader()
        reader.onload = () => resolve({ file, preview: reader.result })
        reader.readAsDataURL(file)
    })

    const clearImages = () => {
        setImages([])
        if (fileRef.current) fileRef.current.value = ''
    }

    const handleSectionChange = (nextSection) => {
        setSection(nextSection)
        setInputMode(nextSection === 'A' ? 'image' : inputMode)
        setTextQuery('')
        setNote('')
        clearImages()
        setResult(null)
        setError(null)
    }

    const handleInputModeChange = (nextMode) => {
        setInputMode(nextMode)
        setTextQuery('')
        setNote('')
        clearImages()
        setResult(null)
        setError(null)
    }

    const handleImageUpload = async (e) => {
        const files = Array.from(e.target.files || [])
        if (!files.length) return

        const maxImages = section === 'A' ? 3 : 1
        const nextFiles = section === 'A'
            ? [...images.map(item => item.file), ...files].slice(0, maxImages)
            : files.slice(0, 1)
        const nextImages = await Promise.all(nextFiles.map(readImagePreview))
        setImages(nextImages)
        setResult(null)
        setError(null)
        if (fileRef.current) fileRef.current.value = ''
    }

    const removeImage = (index) => {
        setImages(current => current.filter((_, currentIndex) => currentIndex !== index))
        setResult(null)
        setError(null)
    }

    const handleSubmit = async () => {
        if (section === 'A' && images.length === 0) return
        if (section === 'B' && inputMode === 'text' && !textQuery.trim()) return
        if (section === 'B' && inputMode === 'image' && images.length === 0) return

        setIsLoading(true)
        setResult(null)
        setError(null)

        const formData = new FormData()
        formData.append('section', section)

        if (section === 'B' && inputMode === 'text') {
            formData.append('query', textQuery.trim())
        } else {
            images.forEach(({ file }) => formData.append('images', file))
            if (note.trim()) formData.append('query', note.trim())
        }

        try {
            const res = await fetch('http://localhost:8000/economics/paper2/answer', { method: 'POST', body: formData })
            const data = await res.json()
            if (data.error) { setError(data.error); return }
            setResult(data)
        } catch {
            setError('Could not reach the backend. Please ensure the server is running.')
        } finally {
            setIsLoading(false)
        }
    }

    const canSubmit = section === 'A'
        ? images.length > 0
        : (inputMode === 'text' ? textQuery.trim().length > 0 : images.length > 0)

    return (
        <div className="min-h-screen bg-[var(--bg-cream)] text-[var(--text-dark)] flex flex-col transition-colors duration-500">
            <header className="h-20 flex-shrink-0 bg-[var(--bg-card)]/70 backdrop-blur-xl border-b border-[var(--border-color)] px-6 flex items-center justify-between z-10 sticky top-0">
                <div className="flex items-center gap-4">
                    <button onClick={onBack} className="p-2 hover:bg-[var(--primary-purple-light)]/10 rounded-xl transition-colors text-[var(--primary-purple)] group">
                        <ArrowLeft size={22} className="group-hover:-translate-x-1 transition-transform" />
                    </button>
                    <div className="h-8 w-px bg-[var(--border-color)]" />
                    <div>
                        <p className="text-[9px] font-black uppercase tracking-widest text-emerald-500 mb-0.5">Cambridge 2281</p>
                        <h2 className="text-lg font-black text-[var(--primary-purple)] uppercase tracking-tighter">Economics Paper 2 Examiner</h2>
                    </div>
                </div>
                <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                    <BookOpen size={12} className="text-emerald-400" />
                    <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Structured Answers</span>
                </div>
            </header>

            <main className="flex-1 flex flex-col lg:flex-row lg:divide-x divide-[var(--border-color)] overflow-y-auto lg:overflow-hidden">
                <section className="flex-1 flex flex-col p-8 md:p-12 space-y-8 overflow-y-auto">
                    <div className="flex flex-wrap gap-3">
                        {[
                            { key: 'A', label: 'Section A', icon: <Layers size={15} /> },
                            { key: 'B', label: 'Section B', icon: <FileText size={15} /> },
                        ].map(({ key, label, icon }) => (
                            <button
                                key={key}
                                onClick={() => handleSectionChange(key)}
                                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black uppercase tracking-wider border transition-all ${section === key ? 'bg-[var(--primary-purple)] text-white border-[var(--primary-purple)] shadow-lg shadow-purple-900/25' : 'bg-[var(--bg-card)] text-[var(--text-muted)] border-[var(--border-color)] hover:text-[var(--primary-purple)]'}`}
                            >
                                {icon} {label}
                            </button>
                        ))}
                    </div>

                    {section === 'B' && (
                        <div className="flex flex-wrap gap-3 p-1 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl w-fit">
                            {[
                                { key: 'text', label: 'Type Question', icon: <FileText size={15} /> },
                                { key: 'image', label: 'Upload Image', icon: <Upload size={15} /> },
                            ].map(({ key, label, icon }) => (
                                <button
                                    key={key}
                                    onClick={() => handleInputModeChange(key)}
                                    className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black uppercase tracking-wider transition-all ${inputMode === key ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/25' : 'text-[var(--text-muted)] hover:text-emerald-600'}`}
                                >
                                    {icon} {label}
                                </button>
                            ))}
                        </div>
                    )}

                    {section === 'B' && inputMode === 'text' ? (
                        <div>
                            <label className="text-[10px] font-black uppercase tracking-widest text-[var(--primary-purple)] mb-3 block">Section B Typed Question</label>
                            <textarea
                                value={textQuery}
                                onChange={e => setTextQuery(e.target.value)}
                                onKeyDown={e => { if (e.ctrlKey && e.key === 'Enter') handleSubmit() }}
                                placeholder={`Type the full Section B question.\n\nDefine opportunity cost.\nExplain two reasons why demand may increase.\nAnalyze the effects of inflation on consumers.\nDiscuss whether a fall in exchange rate benefits an economy.`}
                                rows={11}
                                className="w-full p-5 rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)] text-sm font-medium text-[var(--text-dark)] placeholder:text-[var(--text-muted)]/50 focus:outline-none focus:border-[var(--primary-purple)] resize-none transition-colors leading-relaxed"
                            />
                            <p className="text-[10px] text-[var(--text-muted)] mt-2">Define = 2, Explain = 4, Analyze = 6, Discuss = 8.</p>
                        </div>
                    ) : (
                        <div className="space-y-5">
                            <label className="flex flex-col items-center justify-center w-full min-h-64 border-4 border-dashed border-[var(--border-color)] rounded-3xl cursor-pointer hover:border-emerald-500/50 hover:bg-emerald-500/5 transition-all group p-8">
                                <input ref={fileRef} type="file" className="hidden" accept="image/*" multiple={section === 'A'} onChange={handleImageUpload} />
                                <div className="w-20 h-20 rounded-2xl bg-emerald-500/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                                    <ImageIcon size={36} className="text-emerald-400" />
                                </div>
                                <p className="text-xl font-black text-[var(--primary-purple)]">{section === 'A' ? 'Upload Section A Images' : 'Upload Section B Image'}</p>
                                <p className="text-sm text-[var(--text-muted)] mt-2">{section === 'A' ? `Upload 1 to 3 images. Selected: ${images.length}/3` : `Upload 1 image. Selected: ${images.length}/1`}</p>
                                <p className="text-[10px] font-black uppercase tracking-widest text-emerald-400 mt-4">Marks will be read from the question image</p>
                            </label>

                            {images.length > 0 && (
                                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                                    {images.map((image, index) => (
                                        <div key={`${image.file.name}-${index}`} className="relative rounded-2xl overflow-hidden border border-[var(--border-color)] bg-[var(--bg-card)] p-2">
                                            <img src={image.preview} alt={`Paper 2 upload ${index + 1}`} className="w-full aspect-video object-cover rounded-xl" />
                                            <button onClick={() => removeImage(index)} className="absolute top-4 right-4 p-2 bg-[var(--bg-card)]/90 backdrop-blur-sm rounded-xl text-rose-400 hover:bg-rose-500 hover:text-white transition-all shadow-xl">
                                                <X size={16} />
                                            </button>
                                            <p className="mt-2 px-1 text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)] truncate">Image {index + 1}: {image.file.name}</p>
                                        </div>
                                    ))}
                                </div>
                            )}

                            <textarea
                                value={note}
                                onChange={e => setNote(e.target.value)}
                                placeholder="Optional: add question number or topic note."
                                rows={3}
                                className="w-full p-4 rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)] text-sm font-medium text-[var(--text-dark)] placeholder:text-[var(--text-muted)]/50 focus:outline-none focus:border-[var(--primary-purple)] resize-none transition-colors"
                            />
                        </div>
                    )}

                    <motion.button
                        onClick={handleSubmit}
                        disabled={!canSubmit || isLoading}
                        whileTap={{ scale: 0.97 }}
                        className="w-full py-5 rounded-2xl bg-[var(--primary-purple)] text-white font-black text-sm uppercase tracking-widest flex items-center justify-center gap-3 shadow-2xl shadow-purple-900/30 disabled:opacity-30 hover:opacity-90 transition-all"
                    >
                        {isLoading ? <><RefreshCw size={18} className="animate-spin" /> Analyzing Paper 2...</> : <><Target size={18} /> Answer Paper 2 Question</>}
                    </motion.button>

                    <div className="p-5 rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)]/50">
                        <p className="text-[9px] font-black uppercase tracking-widest text-[var(--primary-purple)] mb-3">Paper 2 Rules</p>
                        <ul className="space-y-2 text-xs text-[var(--text-muted)] font-medium">
                            <li className="flex gap-2"><ChevronRight size={12} className="text-emerald-400 mt-0.5 shrink-0" />Section A keeps context across up to 3 images</li>
                            <li className="flex gap-2"><ChevronRight size={12} className="text-emerald-400 mt-0.5 shrink-0" />Section B image mode accepts 1 image only</li>
                            <li className="flex gap-2"><ChevronRight size={12} className="text-emerald-400 mt-0.5 shrink-0" />Typed Section B uses command-word marks</li>
                            <li className="flex gap-2"><ChevronRight size={12} className="text-emerald-400 mt-0.5 shrink-0" />Answers stay inside O-Level Economics syllabus boundaries</li>
                        </ul>
                    </div>
                </section>

                <section className="flex-1 flex flex-col p-8 md:p-12 overflow-y-auto bg-[var(--bg-card)]/30">
                    <h3 className="text-[9px] font-black uppercase tracking-widest text-[var(--primary-purple)] mb-8">Structured Answer</h3>
                    <AnimatePresence mode="wait">
                        {isLoading && (
                            <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
                                {[80, 60, 90, 50].map((w, i) => (
                                    <div key={i} className="space-y-3">
                                        <div className={`h-3 bg-[var(--primary-purple-light)]/10 rounded-full w-${w === 80 ? '1/2' : w === 60 ? '1/3' : w === 90 ? '2/3' : '1/4'} animate-pulse`} />
                                        <div className="h-16 bg-[var(--primary-purple-light)]/5 rounded-2xl w-full animate-pulse" />
                                    </div>
                                ))}
                            </motion.div>
                        )}

                        {error && !isLoading && (
                            <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center h-full gap-5 text-center">
                                <div className="w-16 h-16 rounded-2xl bg-rose-500/10 flex items-center justify-center">
                                    <AlertTriangle size={28} className="text-rose-400" />
                                </div>
                                <p className="text-sm font-bold text-rose-400">{error}</p>
                            </motion.div>
                        )}

                        {result && !isLoading && !error && (
                            <motion.div key="result" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                                <div className="flex items-center gap-3 text-emerald-400 bg-emerald-500/10 px-5 py-3 rounded-2xl border border-emerald-500/20 text-xs font-black uppercase tracking-tighter mb-8">
                                    <CheckCircle size={16} /> Analysis Complete - Paper 2
                                </div>
                                <Paper2Result result={result} />
                            </motion.div>
                        )}

                        {!result && !isLoading && !error && (
                            <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-1 flex flex-col items-center justify-center gap-6 text-center opacity-30 px-8 py-20">
                                <div className="w-20 h-20 rounded-3xl bg-emerald-500/10 flex items-center justify-center">
                                    <FileText size={36} className="text-emerald-400" />
                                </div>
                                <p className="text-2xl font-black text-[var(--primary-purple)]">Ready for Paper 2</p>
                                <p className="text-sm text-[var(--text-muted)] font-medium max-w-xs">Choose Section A or B, then upload images or type a Section B question.</p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </section>
            </main>
        </div>
    )
}
