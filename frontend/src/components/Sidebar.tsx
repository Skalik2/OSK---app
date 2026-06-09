import { LayoutDashboard, Calendar, Users, Briefcase, Car, CreditCard, LogOut, Plus } from 'lucide-react';
import { NavLink, useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';
import AddLessonModal from './AddLessonModal';

interface SidebarProps {
  role: 'admin' | 'instructor' | 'student';
}

export default function Sidebar({ role }: SidebarProps) {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Handle logout
  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Definiujemy wszystkie elementy i role, które mają do nich dostęp
  const allNavItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: `/${role}`, roles: ['admin', 'instructor', 'student'] },
    { icon: Calendar, label: 'Schedules', path: '/schedules', roles: ['admin', 'instructor', 'student'] },
    { icon: Users, label: 'Students', path: '/students', roles: ['admin', 'instructor'] },
    { icon: Briefcase, label: 'Instructors', path: '/instructors', roles: ['admin'] },
    { icon: CreditCard, label: 'Payments', path: '/payments', roles: ['admin'] },
  ];

  // Filtrujemy elementy, aby zostawić tylko te dozwolone dla obecnej roli
  const navItems = allNavItems.filter(item => item.roles.includes(role));

  const handleLessonAdded = () => {
    setIsModalOpen(false);
    // Dispath an event so other components (like InstructorDashboard) can refresh if they want
    window.dispatchEvent(new Event('lessonAdded'));
  };

  return (
    <>
      <aside className="hidden md:flex flex-col w-[280px] bg-secondary text-white fixed left-0 top-0 h-full z-40 overflow-y-auto">
        <div className="p-8 mb-4">
          <div className="flex items-center gap-3">
            <motion.div 
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className="p-2 bg-surface-container-lowest rounded-xl"
            >
              <Car className="text-primary w-6 h-6" />
            </motion.div>
            <div>
              <h1 className="text-xl font-bold leading-tight">OSK WGW Co.</h1>
              <p className="text-xs text-secondary-fixed-dim">App</p>
            </div>
          </div>
        </div>

        {/* Przycisk akcji pokazujemy tylko jeśli nie jest to admin lub student */}
        {role !== 'admin' && role !== 'student' && (
          <div className="px-4 mb-8">
            <button 
              onClick={() => setIsModalOpen(true)}
              className="w-full bg-primary hover:bg-surface-tint text-white font-semibold py-3 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Book New Lesson
            </button>
          </div>
        )}

        <nav className="flex-1 px-2 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `
                flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200
                ${isActive 
                  ? 'bg-primary text-white shadow-md' 
                  : 'text-secondary-fixed-dim hover:bg-white/10 hover:text-white'
                }
              `}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium text-sm">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 mt-auto border-t border-white/10 space-y-1">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-4 px-4 py-3 text-secondary-fixed-dim hover:bg-white/10 hover:text-white rounded-xl transition-all"
          >
            <LogOut className="w-5 h-5" />
            <span className="font-medium text-sm">Logout</span>
          </button>
        </div>
      </aside>

      {isModalOpen && (
        <AddLessonModal 
          onClose={() => setIsModalOpen(false)}
          onSuccess={handleLessonAdded}
        />
      )}
    </>
  );
}