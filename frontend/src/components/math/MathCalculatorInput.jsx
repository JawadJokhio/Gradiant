import { useRef } from 'react'
import { Delete, RotateCcw } from 'lucide-react'

// Calculator button groups
const ROWS = [
    [
        { label: 'AC',  value: 'AC',   type: 'action', wide: false },
        { label: '⌫',  value: 'DEL',  type: 'action', wide: false },
        { label: '( )', value: '()',   type: 'paren',  wide: false },
        { label: 'π',   value: 'π',   type: 'fn',     wide: false },
    ],
    [
        { label: 'sin', value: 'sin(', type: 'fn',  wide: false },
        { label: 'cos', value: 'cos(', type: 'fn',  wide: false },
        { label: 'tan', value: 'tan(', type: 'fn',  wide: false },
        { label: 'log', value: 'log(', type: 'fn',  wide: false },
    ],
    [
        { label: '√',  value: '√(',  type: 'fn',  wide: false },
        { label: 'xⁿ', value: '^',   type: 'op',  wide: false },
        { label: 'x²', value: '²',   type: 'fn',  wide: false },
        { label: '%',  value: '%',   type: 'op',  wide: false },
    ],
    [
        { label: '7', value: '7', type: 'num', wide: false },
        { label: '8', value: '8', type: 'num', wide: false },
        { label: '9', value: '9', type: 'num', wide: false },
        { label: '÷', value: '÷', type: 'op',  wide: false },
    ],
    [
        { label: '4', value: '4', type: 'num', wide: false },
        { label: '5', value: '5', type: 'num', wide: false },
        { label: '6', value: '6', type: 'num', wide: false },
        { label: '×', value: '×', type: 'op',  wide: false },
    ],
    [
        { label: '1', value: '1', type: 'num', wide: false },
        { label: '2', value: '2', type: 'num', wide: false },
        { label: '3', value: '3', type: 'num', wide: false },
        { label: '−', value: '−', type: 'op',  wide: false },
    ],
    [
        { label: '0',  value: '0',  type: 'num', wide: false },
        { label: '.',  value: '.',  type: 'num', wide: false },
        { label: '=',  value: '=',  type: 'eq',  wide: false },
        { label: '+',  value: '+',  type: 'op',  wide: false },
    ],
]

const TYPE_STYLES = {
    num:    { bg: '#1e1530', hover: '#2a1e42', color: 'rgba(255,255,255,0.9)',  border: 'rgba(255,255,255,0.06)' },
    op:     { bg: '#1a1228', hover: '#251840', color: '#f59e0b',               border: 'rgba(245,158,11,0.2)'  },
    fn:     { bg: '#160f24', hover: '#211540', color: '#a78bfa',               border: 'rgba(167,139,250,0.18)' },
    action: { bg: '#1a0f0a', hover: '#2a1410', color: '#ef4444',               border: 'rgba(239,68,68,0.2)'   },
    paren:  { bg: '#0f1720', hover: '#152330', color: '#60a5fa',               border: 'rgba(96,165,250,0.2)'  },
    eq:     { bg: '#1a0f00', hover: '#2a1800', color: '#f59e0b',               border: 'rgba(245,158,11,0.3)'  },
}

/**
 * MathCalculatorInput
 * Props:
 *   textareaRef — ref to the parent textarea (for cursor-position insertion)
 *   value       — current textarea string value
 *   onChange    — setter for value
 */
export default function MathCalculatorInput({ textareaRef, value, onChange }) {

    function insertAtCursor(text) {
        const el = textareaRef?.current
        if (!el) {
            onChange((v) => v + text)
            return
        }

        const start = el.selectionStart ?? value.length
        const end   = el.selectionEnd   ?? value.length
        const newVal = value.slice(0, start) + text + value.slice(end)
        onChange(newVal)

        // Restore cursor position after React re-render
        requestAnimationFrame(() => {
            el.focus()
            const pos = start + text.length
            el.setSelectionRange(pos, pos)
        })
    }

    function handleKey(btn) {
        if (btn.value === 'AC') {
            onChange('')
            textareaRef?.current?.focus()
            return
        }
        if (btn.value === 'DEL') {
            const el = textareaRef?.current
            if (el) {
                const start = el.selectionStart
                const end   = el.selectionEnd
                if (start !== end) {
                    // Delete selection
                    const newVal = value.slice(0, start) + value.slice(end)
                    onChange(newVal)
                    requestAnimationFrame(() => {
                        el.focus()
                        el.setSelectionRange(start, start)
                    })
                } else if (start > 0) {
                    const newVal = value.slice(0, start - 1) + value.slice(start)
                    onChange(newVal)
                    requestAnimationFrame(() => {
                        el.focus()
                        el.setSelectionRange(start - 1, start - 1)
                    })
                }
            } else {
                onChange((v) => v.slice(0, -1))
            }
            return
        }
        if (btn.value === '()') {
            // Smart bracket: open if balanced, close otherwise
            const open  = (value.match(/\(/g) || []).length
            const close = (value.match(/\)/g) || []).length
            insertAtCursor(open > close ? ')' : '(')
            return
        }
        insertAtCursor(btn.value)
    }

    return (
        <div className="w-full rounded-2xl overflow-hidden"
            style={{
                background: '#100c1e',
                border: '1px solid rgba(245,158,11,0.12)',
                boxShadow: 'inset 0 2px 20px rgba(0,0,0,0.4)',
            }}>

            {/* Pad header */}
            <div className="flex items-center justify-between px-4 py-2"
                style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <span className="text-xs font-bold uppercase tracking-widest"
                    style={{ color: 'rgba(245,158,11,0.5)' }}>
                    Calculator Pad
                </span>
                <span className="text-xs" style={{ color: 'rgba(255,255,255,0.2)' }}>
                    click to insert at cursor
                </span>
            </div>

            {/* Key grid */}
            <div className="p-3 space-y-2">
                {ROWS.map((row, ri) => (
                    <div key={ri} className="grid grid-cols-4 gap-2">
                        {row.map((btn, bi) => {
                            const s = TYPE_STYLES[btn.type] || TYPE_STYLES.num
                            return (
                                <button
                                    key={bi}
                                    id={`calc-btn-${btn.label.replace(/[^a-z0-9]/gi, '_')}`}
                                    onClick={() => handleKey(btn)}
                                    className="rounded-xl py-3 text-sm font-bold transition-all duration-100 active:scale-90 select-none"
                                    style={{
                                        background: s.bg,
                                        color: s.color,
                                        border: `1px solid ${s.border}`,
                                    }}
                                    onMouseEnter={e => { e.currentTarget.style.background = s.hover }}
                                    onMouseLeave={e => { e.currentTarget.style.background = s.bg   }}
                                    title={btn.label}
                                >
                                    {btn.label}
                                </button>
                            )
                        })}
                    </div>
                ))}
            </div>
        </div>
    )
}
