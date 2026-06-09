import { useState, useEffect, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, Mail, Lock, ArrowRight } from 'lucide-react';
import { motion } from 'motion/react';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../api/axios';

export default function AdminLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login, isAuthenticated, user } = useAuth();

  useEffect(() => {
    if (isAuthenticated && user && user.role === 'admin') {
      navigate('/admin');
    }
  }, [isAuthenticated, user, navigate]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await authApi.post('/auth/login', {
        email: email,
        password: password,
        role: 'admin',
      });

      const data = response.data;
      await login(data.access_token, 'admin');
      navigate('/admin');
    } catch (err: any) {
      let message = 'Nieprawidłowe dane logowania administratora';
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          message = err.response.data.detail;
        } else {
          message = JSON.stringify(err.response.data.detail);
        }
      }
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute inset-0 z-0 bg-gradient-to-br from-slate-900 via-slate-800 to-primary/20 opacity-50" />
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative z-10 w-full max-w-[420px] bg-white border border-outline-variant rounded-2xl shadow-2xl p-10 flex flex-col gap-8"
      >
        <header className="flex flex-col items-center text-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 uppercase tracking-tight">Admin</h1>
            <p className="text-xs text-slate-500 font-bold mt-1 uppercase tracking-widest">Login panel</p>
          </div>
        </header>

        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          <div className="space-y-4">
            {error && (
              <div className="p-3 text-xs text-red-600 bg-red-50 rounded-lg font-bold border border-red-100 text-center uppercase tracking-wide">
                {error}
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-1" htmlFor="email">Admin ID (Email)</label>
              <div className="relative group">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-slate-800 transition-colors" />
                <input 
                  id="email"
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@system.local"
                  className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-slate-200 focus:border-slate-400 transition-all font-medium text-sm"
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-1" htmlFor="password">Security Token (Password)</label>
              <div className="relative group">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-slate-800 transition-colors" />
                <input 
                  id="password"
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-slate-200 focus:border-slate-400 transition-all font-medium text-sm"
                  required
                />
              </div>
            </div>
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full py-4 bg-slate-900 text-white font-black uppercase tracking-widest text-xs rounded-xl flex items-center justify-center gap-2 hover:bg-black transition-all shadow-xl disabled:opacity-70 active:scale-95"
          >
            {isLoading ? 'Authenticating...' : 'Authorize Login'}
            {!isLoading && <ArrowRight className="w-4 h-4" />}
          </button>
        </form>

        <footer className="text-center pt-4 border-t border-slate-100">
          <button 
            onClick={() => navigate('/')}
            className="text-[10px] font-bold text-slate-400 hover:text-slate-600 uppercase tracking-widest transition-colors"
          >
            &larr; Return to Public Portal
          </button>
        </footer>
      </motion.div>
    </div>
  );
}
