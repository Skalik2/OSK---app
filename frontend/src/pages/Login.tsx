import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Car, Mail, Lock, ArrowRight } from 'lucide-react';
import { motion } from 'motion/react';

type Role = 'admin' | 'instructor' | 'student';

export default function Login() {
  const [activeRole, setActiveRole] = useState<Role>('admin');
  const navigate = useNavigate();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (activeRole === 'admin') navigate('/admin');
    if (activeRole === 'instructor') navigate('/instructor');
    if (activeRole === 'student') navigate('/student');
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
          {(['admin', 'instructor', 'student'] as Role[]).map((role) => (
            <button
              key={role}
              onClick={() => setActiveRole(role)}
              className={`flex-1 py-2 px-4 text-center rounded-lg font-semibold text-xs tracking-wide transition-all uppercase
                ${activeRole === role 
                  ? 'bg-white text-primary shadow-sm ring-1 ring-primary/10' 
                  : 'text-on-surface-variant hover:text-on-surface'
                }
              `}
            >
              {role}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-8">
          <div className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-on-surface uppercase tracking-wider ml-1" htmlFor="email">Email Address</label>
              <div className="relative group">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-on-surface-variant group-focus-within:text-primary transition-colors" />
                <input 
                  id="email"
                  type="email" 
                  placeholder="name@example.com"
                  className="w-full pl-11 pr-4 py-3 bg-white border border-outline-variant rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all font-medium text-sm"
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between items-center ml-1">
                <label className="text-xs font-bold text-on-surface uppercase tracking-wider" htmlFor="password">Password</label>
                <button type="button" className="text-xs font-bold text-primary hover:underline">Forgot password?</button>
              </div>
              <div className="relative group">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-on-surface-variant group-focus-within:text-primary transition-colors" />
                <input 
                  id="password"
                  type="password" 
                  placeholder="••••••••"
                  className="w-full pl-11 pr-4 py-3 bg-white border border-outline-variant rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all font-medium text-sm"
                  required
                />
              </div>
            </div>
          </div>

          <button 
            type="submit" 
            className="w-full py-4 bg-primary text-white font-bold rounded-xl flex items-center justify-center gap-2 hover:bg-surface-tint focus:ring-4 focus:ring-primary/20 transition-all shadow-lg active:scale-[0.98]"
          >
            Sign In to Portal
            <ArrowRight className="w-5 h-5" />
          </button>
        </form>

        <footer className="text-center pt-8 border-t border-outline-variant/30">
          <p className="text-xs font-medium text-on-surface-variant">
            Having trouble accessing your account? 
            <button className="text-primary hover:underline ml-1 font-bold">Contact Support</button>
          </p>
        </footer>
      </motion.div>
    </div>
  );
}
