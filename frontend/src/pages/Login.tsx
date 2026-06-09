import { useState, useEffect, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Car, Mail, Lock, ArrowRight } from 'lucide-react';
import { motion } from 'motion/react';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../api/axios';

type Role = 'instructor' | 'student';

export default function Login() {
  const [activeRole, setActiveRole] = useState<Role>('student'); 
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login, isAuthenticated, user } = useAuth();

  useEffect(() => {
    if (isAuthenticated && user) {
      navigate(`/${user.role}`);
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
        role: activeRole,
      });

      const data = response.data;
      
      // Use login from AuthContext to handle token and profile status
      await login(data.access_token, activeRole);

      // Redirect after successful login
      navigate(`/${activeRole}`);
    } catch (err: any) {
      let message = 'Nieprawidłowe dane logowania';
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          message = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          message = err.response.data.detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ');
        } else {
          message = JSON.stringify(err.response.data.detail);
        }
      } else if (err.message) {
        message = err.message;
      }
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 z-0 bg-[url('https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?q=80&w=2670&auto=format&fit=crop')] bg-cover bg-center opacity-5" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 w-full max-w-[460px] bg-white border border-outline-variant rounded-2xl shadow-xl p-10 flex flex-col gap-10"
      >
        <header className="flex flex-col items-center text-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-primary-container flex items-center justify-center shadow-sm">
            <Car className="w-9 h-9 text-on-primary-container" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-on-surface">OSK DrivePro</h1>
            <p className="text-sm text-on-surface-variant font-medium mt-1">Secure Management Portal</p>
          </div>
        </header>

        <div className="bg-surface-container-low p-1 rounded-xl flex items-center shadow-inner">
          {(['instructor', 'student'] as Role[]).map((role) => (
            <button
              key={role}
              type="button"
              onClick={() => {
                setActiveRole(role);
                setError(null);
              }}
              className={`flex-1 py-2 px-4 text-center rounded-lg font-semibold text-xs tracking-wide transition-all uppercase
                ${activeRole === role 
                  ? 'bg-white text-primary shadow-sm ring-1 ring-primary/10' 
                  : 'text-on-surface-variant hover:text-on-surface'
                }
              `}
            >
              {role === 'instructor' ? 'Instructor' : 'Student'}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-8">
          <div className="space-y-4">
            
            {/* Wyświetlanie błędu */}
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 rounded-lg font-medium border border-red-100 text-center">
                {error}
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-on-surface uppercase tracking-wider ml-1" htmlFor="email">Email Address</label>
              <div className="relative group">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-on-surface-variant group-focus-within:text-primary transition-colors" />
                <input 
                  id="email"
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full pl-11 pr-4 py-3 bg-white border border-outline-variant rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all font-medium text-sm"
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between items-center ml-1">
                <label className="text-xs font-bold text-on-surface uppercase tracking-wider" htmlFor="password">Password</label>
              </div>
              <div className="relative group">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-on-surface-variant group-focus-within:text-primary transition-colors" />
                <input 
                  id="password"
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-11 pr-4 py-3 bg-white border border-outline-variant rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all font-medium text-sm"
                  required
                />
              </div>
            </div>
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full py-4 bg-primary text-white font-bold rounded-xl flex items-center justify-center gap-2 hover:bg-surface-tint focus:ring-4 focus:ring-primary/20 transition-all shadow-lg active:scale-[0.98] disabled:opacity-70"
          >
            {isLoading ? 'Logowanie...' : 'Sign In to Portal'}
            {!isLoading && <ArrowRight className="w-5 h-5" />}
          </button>
        </form>

        <footer className="text-center pt-8 border-t border-outline-variant/30">
          <p className="text-xs font-medium text-on-surface-variant">
            No account? 
            <Link to="/register" className="text-primary hover:underline ml-1 font-bold">Register now</Link>
          </p>
        </footer>
      </motion.div>
    </div>
  );
}