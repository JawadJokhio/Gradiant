import { useState } from 'react'
import { FileText, Loader2, CheckCircle2, AlertCircle, Edit3 } from 'lucide-react'

const BASE_URL = 'http://localhost:8000'

/**
 * OCRViewer - Displays extracted text from an uploaded image.
 * Allows the student to review and correct OCR output before submission.
 *
 * Props:
 *   imageFile       {File}     - The File object from an <input type="file">
 *   mode            {string}   - "auto" | "printed" | "handwriting" | "math"
 *   onTextExtracted {Function} - Callback receiving the final extracted text string
 */
export default function OCRViewer({ imageFile, mode = 'auto', onTextExtracted }) {
    const [ocrText, setOcrText] = useState('')
    const [loading, setLoading] = useState(false)
    const [confidence, setConfidence] = useState(null)
    const [language, setLanguage] = useState(null)
    const [error, setError] = useState(null)
    const [edited, setEdited] = useState(false)

    const runOCR = async () => {
        if (!imageFile) return
        setLoading(true)
        setError(null)
        setEdited(false)

        const formData = new FormData()
        formData.append('image', imageFile)
        formData.append('mode', mode)

        try {
            const res = await fetch(`${BASE_URL}/api/ocr/extract`, {
                method: 'POST',
                body: formData,
            })
            if (!res.ok) throw new Error(`Server error ${res.status}`)
            const data = await res.json()
            setOcrText(data.raw_text || '')
            setConfidence(data.confidence)
            setLanguage(data.language_detected)
            onTextExtracted?.(data.raw_text || '')
        } catch (err) {
            setError('OCR extraction failed. The AI vision model will be used instead.')
        } finally {
            setLoading(false)
        }
    }

    const handleTextChange = (e) => {
        setOcrText(e.target.value)
        setEdited(true)
        onTextExtracted?.(e.target.value)
    }

    const confidenceColor =
        confidence === null ? ''
        : confidence > 0.75 ? 'text-emerald-500'
        : confidence > 0.45 ? 'text-amber-500'
        : 'text-rose-500'

    const confidenceLabel =
        confidence === null ? ''
        : confidence > 0.75 ? 'High'
        : confidence > 0.45 ? 'Medium'
        : 'Low'

    return (
        <div className="bg-[var(--bg-card)] rounded-2xl p-5 border border-[var(--border-color)] space-y-4 transition-colors duration-300">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <FileText size={18} className="text-[var(--primary-purple)]" />
                    <span className="text-sm font-black text-[var(--primary-purple)] uppercase tracking-widest">
                        OCR Text Extraction
                    </span>
                </div>
                <button
                    onClick={runOCR}
                    disabled={!imageFile || loading}
                    className="px-4 py-1.5 bg-[var(--primary-purple)] text-white rounded-xl text-xs font-black uppercase tracking-widest
                               hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center gap-2"
                >
                    {loading
                        ? <><Loader2 size={14} className="animate-spin" /> Extracting…</>
                        : 'Extract Text'}
                </button>
            </div>

            {/* Confidence + Language badges */}
            {confidence !== null && !error && (
                <div className="flex items-center gap-4 text-xs">
                    <span className={`flex items-center gap-1 font-bold ${confidenceColor}`}>
                        <CheckCircle2 size={13} />
                        Confidence: {Math.round(confidence * 100)}% ({confidenceLabel})
                    </span>
                    {language && (
                        <span className="text-[var(--text-muted)] font-medium">
                            Language: {language === 'ur' ? '🇵🇰 Urdu' : language === 'mixed' ? '🌐 Mixed' : '🇬🇧 English'}
                        </span>
                    )}
                    {edited && (
                        <span className="flex items-center gap-1 text-amber-500 font-bold">
                            <Edit3 size={12} /> Edited
                        </span>
                    )}
                </div>
            )}

            {/* Error state */}
            {error && (
                <div className="flex items-start gap-2 p-3 rounded-xl bg-rose-50 dark:bg-rose-900/10 border border-rose-200 dark:border-rose-900/20 text-rose-600 dark:text-rose-400 text-xs font-medium">
                    <AlertCircle size={14} className="mt-0.5 shrink-0" />
                    {error}
                </div>
            )}

            {/* Extracted text editor */}
            {ocrText !== '' && !error && (
                <div className="space-y-1">
                    <p className="text-[10px] font-black text-[var(--text-muted)] uppercase tracking-widest">
                        Extracted Text (editable — correct any errors before submitting)
                    </p>
                    <textarea
                        value={ocrText}
                        onChange={handleTextChange}
                        rows={5}
                        className="w-full p-3 text-sm rounded-xl border border-[var(--border-color)]
                                   bg-[var(--bg-cream)] font-mono resize-y text-[var(--text-dark)]
                                   focus:outline-none focus:ring-2 focus:ring-[var(--primary-purple)]/30
                                   transition-all"
                    />
                </div>
            )}

            {/* Empty state hint */}
            {!ocrText && !loading && !error && (
                <p className="text-xs text-[var(--text-muted)] font-medium italic">
                    Click "Extract Text" to extract printed text from your uploaded image.
                    Supports English and Urdu. High-confidence text is passed directly to the solver,
                    saving vision API calls.
                </p>
            )}
        </div>
    )
}

