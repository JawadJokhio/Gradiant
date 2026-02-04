import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import SubjectDashboard from './components/SubjectDashboard'
import GeographyModule from './components/GeographyModule'
import VisionAnswering from './components/VisionAnswering'
import TextAnswering from './components/TextAnswering'
import SubjectHub from './components/SubjectHub'

type Page = 'dashboard' | 'hub' | 'geography' | 'vision' | 'text'

function App() {
    const [currentPage, setCurrentPage] = useState<Page>('dashboard')
    const [selectedSubject, setSelectedSubject] = useState<string>('history')

    const subjects = [
        { id: 'geography', name: 'Geography', color: 'from-blue-500 to-cyan-500', description: 'Environment of Pakistan & GIS Mapping' },
        { id: 'history', name: 'History', color: 'from-amber-500 to-orange-600', description: 'Pakistan Studies & World History' },
        { id: 'economics', name: 'Economics', color: 'from-emerald-500 to-teal-600', description: 'Market Dynamics & Macroeconomics' },
        { id: 'islamiat', name: 'Islamiat', color: 'from-green-500 to-emerald-700', description: 'Quranic Studies & Islamic History' },
        { id: 'physics', name: 'Physics', color: 'from-indigo-500 to-purple-600', description: 'Mechanics, Waves & Nuclear Physics' },
        { id: 'chemistry', name: 'Chemistry', color: 'from-rose-500 to-pink-600', description: 'Organic & Inorganic Chemistry' },
    ]

    const currentSubjectObj = subjects.find(s => s.id === selectedSubject) || subjects[1]

    const handleSelectSubject = (subjectId: string) => {
        setSelectedSubject(subjectId)
        setCurrentPage('hub')
    }

    const handleSelectMode = (mode: 'vision' | 'text' | 'geography') => {
        setCurrentPage(mode as Page)
    }

    const handleBackToDashboard = () => {
        setCurrentPage('dashboard')
    }

    const handleBackToHub = () => {
        setCurrentPage('hub')
    }

    return (
        <div className="h-screen w-full bg-slate-950 transition-colors duration-500 font-sans selection:bg-indigo-500/30 overflow-hidden">
            <AnimatePresence mode="wait">
                {currentPage === 'dashboard' && (
                    <motion.div
                        key="dashboard"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        transition={{ duration: 0.3 }}
                        className="h-full overflow-y-auto custom-scrollbar"
                    >
                        <SubjectDashboard
                            onSelectSubject={handleSelectSubject}
                            onSelectMode={handleSelectMode}
                        />
                    </motion.div>
                )}

                {currentPage === 'hub' && (
                    <motion.div
                        key="hub"
                        initial={{ opacity: 0, scale: 1.05 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="h-full overflow-y-auto custom-scrollbar"
                    >
                        <SubjectHub
                            subject={currentSubjectObj}
                            onSelectMode={handleSelectMode}
                            onBack={handleBackToDashboard}
                        />
                    </motion.div>
                )}

                {currentPage === 'geography' && (
                    <motion.div
                        key="geography"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="h-full"
                    >
                        <GeographyModule onBack={handleBackToHub} />
                    </motion.div>
                )}

                {currentPage === 'vision' && (
                    <motion.div
                        key="vision"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="h-full overflow-y-auto custom-scrollbar lg:overflow-hidden"
                    >
                        <VisionAnswering
                            onBack={handleBackToHub}
                            initialSubject={selectedSubject}
                        />
                    </motion.div>
                )}

                {currentPage === 'text' && (
                    <motion.div
                        key="text"
                        initial={{ opacity: 0, scale: 1.1 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="h-full overflow-y-auto custom-scrollbar"
                    >
                        <TextAnswering
                            onBack={handleBackToHub}
                            initialSubject={selectedSubject}
                        />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}

export default App
