// frontend/src/App.tsx
import { BrowserRouter, Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import AdminDashboard from './pages/AdminDashboard';
import AdminLogin from './pages/AdminLogin';
import InstructorDashboard from './pages/InstructorDashboard';
import StudentPortal from './pages/StudentPortal';
import ScheduleView from './pages/ScheduleView';
import StudentsView from './pages/StudentsView';
import { useAuth } from './context/AuthContext';

const ProtectedRoute = ({ allowedRoles }: { allowedRoles: string[] }) => {
  const { user, isLoading } = useAuth();
  const location = useLocation();
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (!user) {
    // If we are trying to access admin pages and not logged in, redirect to admin login
    if (location.pathname.startsWith('/admin')) {
      return <Navigate to="/admin/login" state={{ from: location }} replace />;
    }
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  // Handle role-based access
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return <Navigate to={`/${user.role}`} replace />;
  }

  return <Outlet />;
};

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/admin/login" element={<AdminLogin />} />
        
        <Route element={<Layout />}>
          
          <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
            <Route path="/admin" element={<AdminDashboard />} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['admin', 'instructor']} />}>
            <Route path="/instructor" element={<InstructorDashboard />} />
            <Route path="/students" element={<StudentsView />} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
            <Route path="/instructors" element={<div className="flex items-center justify-center h-full text-secondary font-bold uppercase tracking-widest">Instructors Management Content</div>} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['student']} />}>
            <Route path="/student" element={<StudentPortal />} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['admin', 'instructor', 'student']} />}>
            <Route path="/schedules" element={<ScheduleView />} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['admin', 'instructor']} />}>
            <Route path="/payments" element={<div className="flex items-center justify-center h-full text-secondary font-bold uppercase tracking-widest">Payments Content</div>} />
          </Route>
          
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}