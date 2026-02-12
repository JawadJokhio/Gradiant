import React, { useState } from 'react';
import { motion } from 'framer-motion';

export const Signup: React.FC<{ onToggle: () => void }> = ({ onToggle }) => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        try {
            const response = await fetch('http://127.0.0.1:8000/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password }),
            });

            if (response.ok) {
                setSuccess(true);
                setTimeout(onToggle, 2000);
            } else {
                const errData = await response.json();
                setError(errData.detail || 'Signup failed');
            }
        } catch (err) {
            setError('Connection error');
        }
    };

    if (success) {
        return (
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-md p-8 rounded-3xl bg-green-500/10 backdrop-blur-xl border border-green-500/30 text-center"
            >
                <h2 className="text-3xl font-bold text-green-400 mb-4">Account Created!</h2>
                <p className="text-slate-300">Redirecting to login...</p>
            </motion.div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-md p-8 rounded-3xl bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl"
        >
            <h2 className="text-3xl font-bold text-white mb-6 text-center">Official Examiner Account</h2>
            {error && <div className="p-3 mb-4 bg-red-500/20 border border-red-500/50 text-red-200 rounded-lg text-sm">{error}</div>}
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Username</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                        placeholder="john_doe"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                        placeholder="john@example.com"
                        required
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                        placeholder="••••••••"
                        required
                    />
                </div>
                <button
                    type="submit"
                    className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-500/30 transition-all transform hover:scale-[1.02]"
                >
                    Register as Examiner
                </button>
            </form>
            <p className="mt-6 text-center text-slate-400">
                Already have an account? {' '}
                <button onClick={onToggle} className="text-indigo-400 hover:underline">Login</button>
            </p>
        </motion.div>
    );
};
