import { useEffect } from 'react'

const BASE_URL = 'http://localhost:8000'

/**
 * Get or create a persistent session ID stored in localStorage.
 * This is the key that links all interactions to a single student profile.
 */
function getSessionId() {
    let id = localStorage.getItem('gradiant_session_id')
    if (!id) {
        // crypto.randomUUID() is available in all modern browsers
        id = typeof crypto !== 'undefined' && crypto.randomUUID
            ? crypto.randomUUID()
            : Math.random().toString(36).slice(2) + Date.now().toString(36)
        localStorage.setItem('gradiant_session_id', id)
    }
    return id
}

export const sessionId = getSessionId()

/**
 * Log a student interaction to the backend weakness tracker.
 * This is a fire-and-forget call — it never blocks or throws to the caller.
 *
 * @param {object} params
 * @param {string} params.subject         - "history" | "geography" | "math" | "economics"
 * @param {string} [params.topic]         - topic key, or "auto" for backend classification
 * @param {string} params.questionText    - the question the student asked
 * @param {number} params.marksAvailable  - marks value selected in the UI
 * @param {number} [params.marksObtained] - optional; backend extracts from LLM response if absent
 * @param {string} [params.mode]          - "text" | "vision" | "mcq"
 * @param {string} [params.llmResponse]   - raw LLM answer text (for examiner band extraction)
 */
export async function logInteraction({
    subject,
    topic = 'auto',
    questionText,
    marksAvailable,
    marksObtained = null,
    mode = 'text',
    llmResponse = null,
}) {
    try {
        await fetch(`${BASE_URL}/api/weakness/log`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-ID': sessionId,
            },
            body: JSON.stringify({
                subject,
                topic,
                question_text: questionText || '',
                marks_available: marksAvailable || 4,
                marks_obtained: marksObtained,
                mode,
                llm_response: llmResponse,
            }),
        })
    } catch {
        // Silent fail — weakness tracking should NEVER break the main UX
    }
}

/**
 * Invisible component mounted at App.jsx level to ensure the session ID
 * is initialised as early as possible.
 */
export default function SessionTracker() {
    useEffect(() => {
        // Ensure session ID is created on first render
        getSessionId()
    }, [])
    return null
}

