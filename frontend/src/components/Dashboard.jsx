import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

const subjects = [
    { id: 'history', name: 'Pakistan History', icon: '🏛️', color: 'from-amber-500 to-orange-600', description: 'Cambridge 2059/01 - Cultural & Historical Background' },
    { id: 'geography', name: 'Pakistan Geography', icon: '🌍', color: 'from-emerald-500 to-teal-600', description: 'Cambridge 2059/02 - Environment of Pakistan' },
    { id: 'economics', name: 'Economics', icon: '📈', color: 'from-blue-500 to-indigo-600', description: 'O-Level Economics - Principles & Applications' },
    { id: 'islamiat', name: 'Islamiat', icon: '🌙', color: 'from-purple-500 to-fuchsia-600', description: 'Cambridge 2058 - Islamic Religion & Culture' },
];

export const Dashboard = ({ onSelectSubject }) => {
    const { user, logout, token } = useAuth();
    const [performance, setPerformance] = useState(null);

    useEffect(() => {
        const fetchPerformance = async () => {
            if (token) {
                const res = await fetch('http://127.0.0.1:8000/user/performance', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) setPerformance(await res.json());
            }
        };
        fetchPerformance();
    }, [token]);

    return (
        <div className="min-h-screen bg-slate-950 text-white p-8">
            <header className="flex justify-between items-center mb-12">
                <div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                        Welcome, {user?.username}
                    </h1>
                    <p className="text-slate-400 mt-2">Continue your journey to O-Level mastery.</p>
                </div>
                <button
                    onClick={logout}
                    className="px-6 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 transition-all font-medium"
                >
                    Sign Out
                </button>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
                {/* Performance Stats */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="lg:col-span-2 p-8 rounded-3xl bg-indigo-600/10 border border-indigo-500/20"
                >
                    <h2 className="text-2xl font-bold mb-6 flex items-center">
                        <span className="mr-3">📊</span> Your Performance Profile
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-4">
                            <h3 className="text-sm font-uppercase tracking-wider text-slate-500 font-bold">WEAK AREAS</h3>
                            <div className="flex flex-wrap gap-2">
                                {performance?.weak_areas?.length > 0 ? performance.weak_areas.map((wa) => (
                                    <span key={wa} className="px-3 py-1 bg-red-500/10 border border-red-500/30 text-red-400 rounded-full text-xs">
                                        {wa}
                                    </span>
                                )) : (
                                    <p className="text-slate-500 italic">No weaknesses detected yet. Keep practicing!</p>
                                )}
                            </div>
                        </div>

                        <div className="space-y-4">
                            <h3 className="text-sm font-uppercase tracking-wider text-slate-500 font-bold">EXAMINER ESTIMATE</h3>
                            <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                                <div className="text-3xl font-bold text-indigo-400">{performance?.profile?.skill_level || 'Developing'}</div>
                                <div className="text-xs text-slate-500 mt-1">Based on previous {performance?.profile?.total_marks_attempted || 0} marks</div>
                            </div>
                        </div>
                    </div>
                </motion.div>

                {/* Quick History */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="p-8 rounded-3xl bg-slate-900 border border-slate-800"
                >
                    <h2 className="text-2xl font-bold mb-4">Activity</h2>
                    <p className="text-slate-400 text-sm mb-6">Your recent interactions will appear here once you start studying.</p>
                    <div className="h-40 flex items-center justify-center border-2 border-dashed border-slate-800 rounded-2xl">
                        <span className="text-slate-600 text-sm">No recent history</span>
                    </div>
                </motion.div>
            </div>

            <h2 className="text-3xl font-bold mb-8">Select Your Course</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                {subjects.map((s, index) => (
                    <motion.button
                        key={s.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        onClick={() => onSelectSubject(s.id)}
                        className="group relative p-8 rounded-3xl bg-slate-900 border border-slate-800 hover:border-indigo-500/50 transition-all text-left overflow-hidden"
                    >
                        <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${s.color} opacity-5 group-hover:opacity-20 transition-all blur-3xl rounded-full -mr-8 -mt-8`}></div>
                        <div className="text-4xl mb-4">{s.icon}</div>
                        <h3 className="text-2xl font-bold mb-2 group-hover:text-indigo-400 transition-colors">{s.name}</h3>
                        <p className="text-slate-500 text-sm">{s.description}</p>
                        <div className="mt-6 flex items-center text-indigo-400 text-sm font-semibold">
                            Enter Module <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
                        </div>
                    </motion.button>
                ))}
            </div>
        </div>
    );
};
