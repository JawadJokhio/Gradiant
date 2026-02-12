import { useAuth } from './context/AuthContext'
import { Login } from './components/Auth/Login'
import { Signup } from './components/Auth/Signup'
import HistoryExaminer from './components/HistoryExaminer'
import { useState } from 'react'
import { AnimatePresence } from 'framer-motion'

function App() {
    const { token, isLoading } = useAuth()
    const [authMode, setAuthMode] = useState<'login' | 'signup'>('login')

    if (isLoading) {
        return (
            <div className="h-screen w-full bg-slate-950 flex items-center justify-center">
                <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        )
    }

    if (!token) {
        return (
            <div className="h-screen w-full bg-slate-950 flex items-center justify-center p-4">
                <AnimatePresence mode="wait">
                    {authMode === 'login' ? (
                        <Login key="login" onToggle={() => setAuthMode('signup')} />
                    ) : (
                        <Signup key="signup" onToggle={() => setAuthMode('login')} />
                    )}
                </AnimatePresence>
            </div>
        )
    }

    return (
        <HistoryExaminer />
    )
}
export default App
