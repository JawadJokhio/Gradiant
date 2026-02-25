import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BrainCircuit, BookOpen, UserPlus, Mail, Key, Sparkles, ArrowLeft, Loader2 } from 'lucide-react';

export const Signup = ({ onToggle }) => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:8000/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password }),
            });

            if (response.ok) {
                setSuccess(true);
                setTimeout(onToggle, 2500);
            } else {
                const errData = await response.json();
                setError(errData.detail || 'Academic registration failed.');
            }
        } catch (err) {
            setError('Neural link error. Check your connection.');
        } finally {
            setIsLoading(false);
        }
    };

    if (success) {
        return (
            <div className="min-h-screen bg-[var(--bg-cream)] flex items-center justify-center p-6 transition-colors duration-500">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="w-full max-w-[480px] bg-[var(--bg-card)] rounded-[3.5rem] shadow-2xl shadow-emerald-900/10 dark:shadow-black/40 border border-emerald-50 dark:border-emerald-900/20 p-12 text-center space-y-8"
                >
                    <div className="w-24 h-24 rounded-full bg-emerald-50 dark:bg-emerald-900/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto shadow-inner">
                        <UserPlus size={48} />
                    </div>
                    <div>
                        <h2 className="text-3xl font-black text-[var(--primary-purple)] uppercase tracking-tighter">Registration Complete</h2>
                        <p className="text-[var(--text-muted)] mt-3 font-medium">Synchronizing your credentials...</p>
                    </div>
                    <div className="flex justify-center">
                        <Loader2 className="animate-spin text-emerald-500" size={32} />
                    </div>
                </motion.div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[var(--bg-cream)] flex items-center justify-center p-6 relative overflow-hidden transition-colors duration-500">
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[var(--primary-purple-light)]/20 dark:bg-[var(--primary-purple-light)]/10 rounded-full blur-[120px]"></div>
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-[var(--accent-gold)]/10 rounded-full blur-[120px]"></div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-[480px] bg-[var(--bg-card)] rounded-[3.5rem] shadow-2xl shadow-purple-900/10 dark:shadow-black/40 border border-[var(--border-color)] p-10 md:p-14 relative z-10 transition-colors duration-500"
            >
                <div className="flex flex-col items-center text-center space-y-6 mb-12">
                    <div className="w-20 h-20 rounded-[2rem] bg-[var(--primary-purple-light)]/10 text-[var(--primary-purple)] flex items-center justify-center shadow-inner">
                        <UserPlus size={40} />
                    </div>
                    <div>
                        <h2 className="text-4xl font-black text-[var(--primary-purple)] tracking-tighter uppercase mb-2">New Examiner</h2>
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-[var(--accent-gold)]">Registration Protocol</p>
                    </div>
                </div>

                {error && (
                    <div className="p-4 mb-8 bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/20 text-red-600 dark:text-red-400 rounded-2xl text-xs font-bold uppercase tracking-wider text-center font-mono">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-[10px] font-black uppercase tracking-[0.3em] text-[var(--text-muted)] ml-2 transition-colors duration-500">Public Handle</label>
                        <div className="relative">
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full px-8 py-5 pl-14 rounded-[1.5rem] bg-[var(--primary-purple-light)]/5 dark:bg-[var(--bg-cream)]/5 border-2 border-transparent focus:border-[var(--primary-purple)] focus:bg-[var(--bg-card)] text-[var(--primary-purple)] font-bold transition-all placeholder:text-[var(--primary-purple-light)]/30"
                                placeholder="john_doe"
                                required
                            />
                            <BookOpen size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-[var(--primary-purple-light)]/30" />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black uppercase tracking-[0.3em] text-[var(--text-muted)] ml-2 transition-colors duration-500">Digital Post</label>
                        <div className="relative">
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-8 py-5 pl-14 rounded-[1.5rem] bg-[var(--primary-purple-light)]/5 dark:bg-[var(--bg-cream)]/5 border-2 border-transparent focus:border-[var(--primary-purple)] focus:bg-[var(--bg-card)] text-[var(--primary-purple)] font-bold transition-all placeholder:text-[var(--primary-purple-light)]/30"
                                placeholder="name@clifton.edu"
                                required
                            />
                            <Mail size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-[var(--primary-purple-light)]/30" />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black uppercase tracking-[0.3em] text-[var(--text-muted)] ml-2 transition-colors duration-500">Access Key</label>
                        <div className="relative">
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-8 py-5 pl-14 rounded-[1.5rem] bg-[var(--primary-purple-light)]/5 dark:bg-[var(--bg-cream)]/5 border-2 border-transparent focus:border-[var(--primary-purple)] focus:bg-[var(--bg-card)] text-[var(--primary-purple)] font-bold transition-all placeholder:text-[var(--primary-purple-light)]/30"
                                placeholder="••••••••"
                                required
                            />
                            <Key size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-[var(--primary-purple-light)]/30" />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full py-6 bg-[var(--primary-purple)] hover:bg-[var(--primary-purple)]/90 text-white dark:text-[#0f0a1e] font-black uppercase tracking-[0.2em] rounded-[1.5rem] shadow-2xl shadow-purple-900/20 dark:shadow-black/40 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 flex items-center justify-center gap-3 mt-4"
                    >
                        {isLoading ? (
                            <Loader2 size={24} className="animate-spin text-[var(--accent-gold)]" />
                        ) : (
                            'Establish Identity'
                        )}
                    </button>
                </form>

                <div className="mt-12 pt-8 border-t border-[var(--border-color)] flex flex-col items-center transition-colors duration-500">
                    <button
                        onClick={onToggle}
                        className="flex items-center gap-2 text-[var(--primary-purple)] font-black text-[10px] uppercase tracking-widest hover:text-[var(--accent-gold)] transition-colors"
                    >
                        <ArrowLeft size={14} />
                        Return to Authentication
                    </button>
                </div>
            </motion.div>
        </div>
    );
};
