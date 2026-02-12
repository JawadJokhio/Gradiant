import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { motion } from 'framer-motion';

// API Configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// Type definitions for better type safety
interface LoginResponse {
    access_token: string;
}

interface ErrorResponse {
    detail?: string;
}

export const Login: React.FC<{ onToggle: () => void }> = ({ onToggle }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const { login } = useAuth();
    const usernameInputRef = useRef<HTMLInputElement>(null);

    // Auto-focus username field on mount
    useEffect(() => {
        usernameInputRef.current?.focus();
    }, []);

    // Clear error when user starts typing
    const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setUsername(e.target.value);
        if (error) setError('');
    };

    const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setPassword(e.target.value);
        if (error) setError('');
    };

    // Validate inputs before submission
    const validateInputs = (): boolean => {
        const trimmedUsername = username.trim();

        if (trimmedUsername.length < 3) {
            setError('Username must be at least 3 characters long');
            return false;
        }

        if (password.length < 6) {
            setError('Password must be at least 6 characters long');
            return false;
        }

        return true;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Client-side validation
        if (!validateInputs()) {
            return;
        }

        setIsLoading(true);

        try {
            const formData = new FormData();
            formData.append('username', username.trim());
            formData.append('password', password);

            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data: LoginResponse = await response.json();
                login(data.access_token);
            } else {
                const errData: ErrorResponse = await response.json();
                setError(errData.detail || 'Login failed. Please check your credentials.');
                // Clear password on error for security
                setPassword('');
            }
        } catch (err) {
            if (err instanceof TypeError) {
                setError('Cannot connect to server. Please check your network connection.');
            } else {
                setError('An unexpected error occurred. Please try again.');
            }
            console.error('Login error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-md p-8 rounded-3xl bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl"
        >
            <h2 className="text-3xl font-bold text-white mb-6 text-center">Examiner Portal</h2>

            {error && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    role="alert"
                    aria-live="assertive"
                    className="p-3 mb-4 bg-red-500/20 border border-red-500/50 text-red-200 rounded-lg text-sm"
                >
                    {error}
                </motion.div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
                <div>
                    <label htmlFor="username-input" className="block text-sm font-medium text-slate-300 mb-1">
                        Username
                    </label>
                    <input
                        id="username-input"
                        ref={usernameInputRef}
                        type="text"
                        value={username}
                        onChange={handleUsernameChange}
                        className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all font-mono"
                        placeholder="john_doe"
                        autoComplete="username"
                        aria-invalid={error ? 'true' : 'false'}
                        aria-describedby={error ? 'login-error' : undefined}
                        disabled={isLoading}
                        required
                    />
                </div>

                <div>
                    <label htmlFor="password-input" className="block text-sm font-medium text-slate-300 mb-1">
                        Password
                    </label>
                    <div className="relative">
                        <input
                            id="password-input"
                            type={showPassword ? 'text' : 'password'}
                            value={password}
                            onChange={handlePasswordChange}
                            className="w-full px-4 py-3 pr-12 rounded-xl bg-slate-900/50 border border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all font-mono"
                            placeholder="••••••••"
                            autoComplete="current-password"
                            aria-invalid={error ? 'true' : 'false'}
                            aria-describedby={error ? 'login-error' : undefined}
                            disabled={isLoading}
                            required
                        />
                        <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 transition-colors"
                            aria-label={showPassword ? 'Hide password' : 'Show password'}
                            disabled={isLoading}
                        >
                            {showPassword ? (
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                                </svg>
                            ) : (
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                            )}
                        </button>
                    </div>
                </div>

                <button
                    type="submit"
                    className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-500/30 transition-all transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                    disabled={isLoading}
                >
                    {isLoading ? (
                        <span className="flex items-center justify-center gap-2">
                            <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Logging in...
                        </span>
                    ) : (
                        'Login to Examiner'
                    )}
                </button>
            </form>

            <p className="mt-6 text-center text-slate-400">
                Don't have an account?{' '}
                <button
                    onClick={onToggle}
                    className="text-indigo-400 hover:underline focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded"
                    disabled={isLoading}
                >
                    Sign up
                </button>
            </p>
        </motion.div>
    );
};
