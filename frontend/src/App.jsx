import { useState, useEffect } from 'react'
import { AnimatePresence } from 'framer-motion'
import { Sun, Moon } from 'lucide-react'

// New Component Imports
import SubjectDashboard from './components/SubjectDashboard'
import SubjectHub from './components/SubjectHub'
import HistoryExaminer from './components/HistoryExaminer'
import GeographyModule from './components/GeographyModule'
import TextAnswering from './components/TextAnswering'
import VisionAnswering from './components/VisionAnswering'
import WeaknessAnalysis from './components/WeaknessAnalysis'
import PaperExplorer from './components/PaperExplorer'

const subjectsData = {
    history: { id: 'history', name: 'History', color: 'from-purple-600 to-purple-800' },
    geography: { id: 'geography', name: 'Geography', color: 'from-blue-600 to-blue-800' },
    economics: { id: 'economics', name: 'Economics', color: 'from-emerald-600 to-teal-800' },
    islamiat: { id: 'islamiat', name: 'Islamiat', color: 'from-green-600 to-emerald-800' },
    physics: { id: 'physics', name: 'Physics', color: 'from-indigo-600 to-purple-800' },
    chemistry: { id: 'chemistry', name: 'Chemistry', color: 'from-rose-600 to-pink-800' }
}

function App() {
    const [activeSubject, setActiveSubject] = useState(null)
    const [activeMode, setActiveMode] = useState(null)
    const [darkMode, setDarkMode] = useState(() => {
        const saved = localStorage.getItem('darkMode')
        return saved === 'true'
    })

    useEffect(() => {
        localStorage.setItem('darkMode', darkMode)
    }, [darkMode])

    const handleBack = () => setActiveMode(null)

    const renderToggle = () => (
        <button
            onClick={() => setDarkMode(!darkMode)}
            className="fixed bottom-8 right-8 z-[9999] w-14 h-14 rounded-2xl bg-white dark:bg-[#1a142e] border-2 border-[#4d3e77]/10 dark:border-[#a594f9]/20 shadow-2xl flex items-center justify-center text-[#4d3e77] dark:text-[#a594f9] hover:scale-110 active:scale-90 transition-all group"
            title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
        >
            {darkMode ? <Sun size={24} className="group-hover:rotate-45 transition-transform" /> : <Moon size={24} className="group-hover:-rotate-12 transition-transform" />}
        </button>
    )

    const renderContent = () => {
        if (!activeSubject) {
            return (
                <SubjectDashboard
                    onSelectSubject={(id) => setActiveSubject(id)}
                    onSelectMode={(mode) => setActiveMode(mode)}
                />
            )
        }

        if (!activeMode) {
            return (
                <SubjectHub
                    subject={subjectsData[activeSubject]}
                    onSelectMode={(mode) => setActiveMode(mode)}
                    onBack={() => setActiveSubject(null)}
                />
            )
        }

        if (activeSubject === 'geography' && activeMode === 'geography') {
            return <GeographyModule onBack={handleBack} />
        }

        if (activeMode === 'vision') {
            return <VisionAnswering onBack={handleBack} initialSubject={activeSubject} />
        }

        if (activeMode === 'text') {
            if (activeSubject === 'history') {
                return <HistoryExaminer onBack={handleBack} />
            }
            return <TextAnswering onBack={handleBack} initialSubject={activeSubject} />
        }

        if (activeMode === 'weakness') {
            return <WeaknessAnalysis onBack={handleBack} />
        }

        if (activeMode === 'papers') {
            return <PaperExplorer initialSubject={activeSubject} onBack={handleBack} />
        }

        return (
            <div className="h-screen w-full flex flex-col items-center justify-center text-[#2d2645] dark:text-[#f3f4f6] p-8 text-center">
                <h2 className="text-4xl font-black mb-4">Module Under Construction</h2>
                <p className="text-[#645c84] dark:text-[#94a3b8] mb-8 text-xl">The {activeMode} mode for {activeSubject} is coming soon.</p>
                <button onClick={handleBack} className="px-8 py-3 bg-[#4d3e77] dark:bg-[#a594f9] text-white dark:text-[#0f0a1e] rounded-2xl font-black uppercase tracking-widest shadow-xl">Back to Hub</button>
            </div>
        )
    }

    return (
        <div className={`h-screen w-full font-sans transition-colors duration-500 overflow-y-auto custom-scrollbar ${darkMode ? 'dark bg-[#0f0a1e]' : 'bg-[#fdf9f6]'}`}>
            {renderContent()}
            {renderToggle()}
        </div>
    )
}

export default App
