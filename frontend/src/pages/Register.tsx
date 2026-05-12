import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus, Mail, Lock, ArrowRight } from 'lucide-react';
import { motion } from 'motion/react';

type RegisterRole = 'instructor' | 'student';

export default function Register() {
  const [activeRole, setActiveRole] = useState<RegisterRole>('student');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Hasła nie są identyczne");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          role: activeRole,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Błąd rejestracji');
      }

      // Po pomyślnej rejestracji przekieruj do logowania
      navigate('/');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute inset-0 z-0 bg-[url('https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?q=80&w=2670&auto=format&fit=crop')] bg-cover bg-center opacity-25" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 w-full max-w-[460px] bg-white border border-outline-variant rounded-2xl shadow-xl p-10 flex flex-col gap-8"
      >
        <header className="flex flex-col items-center text-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-primary-container flex items-center justify-center shadow-sm">
            <UserPlus className="w-9 h-9 text-on-primary-container" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-on-surface">Dołącz do DrivePro</h1>
            <p className="text-sm text-on-surface-variant font-medium mt-1">Stwórz konto w portalu</p>
          </div>
        </header>

        <div className="bg-surface-container-low p-1 rounded-xl flex items-center shadow-inner">
          {(['instructor', 'student'] as RegisterRole[]).map((role) => (
            <button
              key={role}
              type="button"
              onClick={() => setActiveRole(role)}
              className={`flex-1 py-2 px-4 text-center rounded-lg font-semibold text-xs tracking-wide transition-all uppercase
                ${activeRole === role 
                  ? 'bg-white text-primary shadow-sm ring-1 ring-primary/10' 
                  : 'text-on-surface-variant hover:text-on-surface'
                }
              `}
            >
              {role === 'instructor' ? 'Instruktor' : 'Kursant'}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          {error && (
            <div className="p-3 text-sm text-red-600 bg-red-50 rounded-lg font-medium border border-red-100 text-center">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-on-surface uppercase tracking-wider ml-1">Email</label>
              <div className="relative group">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-on-surface-variant group-focus-within:text-primary transition-colors" />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="twoj@email.com"
                  className="w-full pl-11 pr-4 py-3 bg-white border border-outline-variant rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all font-medium text-sm"
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-on-surface uppercase tracking-wider ml-1">Hasło</label>
              <div className="relative group">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-on-surface-variant group-focus-within:text-primary transition-colors" />
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-11 pr-4 py-3 bg-white border border-outline-variant rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all font-medium text-sm"
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-on-surface uppercase tracking-wider ml-1">Potwierdź hasło</label>
              <div className="relative group">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-on-surface-variant group-focus-within:text-primary transition-colors" />
                <input 
                  type="password" 
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
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
            className="w-full py-4 bg-primary text-white font-bold rounded-xl flex items-center justify-center gap-2 hover:bg-surface-tint transition-all shadow-lg disabled:opacity-70"
          >
            {isLoading ? 'Tworzenie konta...' : 'Zarejestruj się'}
            {!isLoading && <ArrowRight className="w-5 h-5" />}
          </button>
        </form>

        <footer className="text-center pt-6 border-t border-outline-variant/30">
          <p className="text-xs font-medium text-on-surface-variant">
            Masz już konto? 
            <Link to="/" className="text-primary hover:underline ml-1 font-bold">Zaloguj się</Link>
          </p>
        </footer>
      </motion.div>
    </div>
  );
}