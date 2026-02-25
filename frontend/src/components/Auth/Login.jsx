import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import { BrainCircuit, ShieldCheck, Eye, EyeOff, Loader2, Sparkles, ArrowRight, BookOpen } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const Login = ({ onToggle }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const { login } = useAuth();
    const usernameInputRef = useRef(null);

    useEffect(() => {
        usernameInputRef.current?.focus();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        if (username.length < 3 || password.length < 6) {
            setError('Please verify your academic credentials.');
            return;
        }
        setIsLoading(true);
        try {
            const formData = new FormData();
            formData.append('username', username.trim());
            formData.append('password', password);
            const response = await fetch(`${API_URL}/login`, { method: 'POST', body: formData });
            if (response.ok) {
                const data = await response.json();
                login(data.access_token);
            } else {
                const errData = await response.json();
                setError(errData.detail || 'Authentication failure. Check your credentials.');
                setPassword('');
            }
        } catch (err) {
            setError('Neural link error. Check your connection.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[var(--bg-cream)] flex items-center justify-center p-6 relative overflow-hidden transition-colors duration-500">
            {/* Background Decorative Elements */}
            <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-[var(--primary-purple-light)]/20 dark:bg-[var(--primary-purple-light)]/10 rounded-full blur-[120px]"></div>
            <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-[var(--accent-gold)]/10 rounded-full blur-[120px]"></div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-[480px] bg-[var(--bg-card)] rounded-[3.5rem] shadow-2xl shadow-purple-900/10 dark:shadow-black/40 border border-[var(--border-color)] p-10 md:p-14 relative z-10 transition-colors duration-500"
            >
                <div className="flex flex-col items-center text-center space-y-6 mb-12">
                    <div className="relative">
                        <div className="w-20 h-20 rounded-[2rem] bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] flex items-center justify-center shadow-xl shadow-purple-900/40 dark:shadow-black/20">
                            <BrainCircuit size={40} />
                        </div>
                        <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-[var(--accent-gold)] text-white dark:text-[#0f0a1e] flex items-center justify-center border-4 border-[var(--bg-card)] shadow-lg transition-colors duration-500">
                            <ShieldCheck size={14} />
                        </div>
                    </div>

                    <div>
                        <h2 className="text-4xl font-black text-[var(--primary-purple)] tracking-tighter uppercase mb-2">Examiner Portal</h2>
                        <div className="flex items-center gap-2 justify-center">
                            <div className="h-[1px] w-8 bg-[var(--border-color)]"></div>
                            <span className="text-[10px] font-black uppercase tracking-[0.3em] text-[var(--accent-gold)]">Academic Intelligence</span>
                            <div className="h-[1px] w-8 bg-[var(--border-color)]"></div>
                        </div>
                    </div>
                </div>

                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="p-4 mb-8 bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/20 text-red-600 dark:text-red-400 rounded-2xl text-xs font-bold uppercase tracking-wider text-center"
                    >
                        {error}
                    </motion.div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-[10px] font-black uppercase tracking-[0.3em] text-[var(--text-muted)] ml-2 transition-colors duration-500">Academic Identifier</label>
                        <input
                            ref={usernameInputRef}
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full px-8 py-5 rounded-[1.5rem] bg-[var(--primary-purple-light)]/5 dark:bg-[var(--bg-cream)]/5 border-2 border-transparent focus:border-[var(--primary-purple)] focus:bg-[var(--bg-card)] text-[var(--primary-purple)] font-bold transition-all placeholder:text-[var(--primary-purple-light)]/30"
                            placeholder="username_or_id"
                            required
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black uppercase tracking-[0.3em] text-[var(--text-muted)] ml-2 transition-colors duration-500">Secure Pass-Key</label>
                        <div className="relative">
                            <input
                                type={showPassword ? 'text' : 'password'}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-8 py-5 rounded-[1.5rem] bg-[var(--primary-purple-light)]/5 dark:bg-[var(--bg-cream)]/5 border-2 border-transparent focus:border-[var(--primary-purple)] focus:bg-[var(--bg-card)] text-[var(--primary-purple)] font-bold transition-all placeholder:text-[var(--primary-purple-light)]/30"
                                placeholder="••••••••"
                                required
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-6 top-1/2 -translate-y-1/2 text-[var(--primary-purple-light)]/40 hover:text-[var(--primary-purple)] transition-colors"
                            >
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
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
                            <>
                                <span>Initialize Session</span>
                                <ArrowRight size={20} className="text-[var(--accent-gold)]" />
                            </>
                        )}
                    </button>
                </form>

                <div className="mt-12 pt-8 border-t border-[var(--border-color)] flex flex-col items-center gap-6 transition-colors duration-500">
                    <p className="text-[11px] font-black text-[var(--primary-purple-light)]/40 uppercase tracking-widest text-center">
                        Unauthorized access is strictly prohibited
                    </p>
                    <button
                        onClick={onToggle}
                        className="flex items-center gap-3 px-8 py-3 rounded-full bg-[var(--primary-purple-light)]/10 dark:bg-[var(--primary-purple-light)]/5 text-[var(--primary-purple)] font-black text-[10px] uppercase tracking-widest hover:bg-[var(--primary-purple-light)]/20 transition-colors"
                    >
                        <Sparkles size={14} className="text-[var(--accent-gold)]" />
                        Create New Credentials
                    </button>
                </div>
            </motion.div>
        </div>
    );
};
