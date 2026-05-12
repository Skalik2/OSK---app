// frontend/src/App.tsx
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import AdminDashboard from './pages/AdminDashboard';
import InstructorDashboard from './pages/InstructorDashboard';
import StudentPortal from './pages/StudentPortal';
import ScheduleView from './pages/ScheduleView';

const ProtectedRoute = ({ allowedRoles }: { allowedRoles: string[] }) => {
  const userRole = localStorage.getItem('userRole');
  
  if (!userRole) {
    return <Navigate to="/" replace />;
  }

  if (!allowedRoles.includes(userRole)) {
    return <Navigate to={`/${userRole}`} replace />;
  }

  return <Outlet />;
};

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        
        <Route element={<Layout />}>
          
          <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/settings" element={<div className="flex items-center justify-center h-full text-secondary font-bold uppercase tracking-widest">Settings Content</div>} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['admin', 'instructor']} />}>
            <Route path="/instructor" element={<InstructorDashboard />} />
            <Route path="/students" element={<div className="flex items-center justify-center h-full text-secondary font-bold uppercase tracking-widest">Students Management Content</div>} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['admin', 'student']} />}>
            <Route path="/instructors" element={<div className="flex items-center justify-center h-full text-secondary font-bold uppercase tracking-widest">Instructors Management Content</div>} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['student']} />}>
            <Route path="/student" element={<StudentPortal />} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['admin', 'instructor', 'student']} />}>
            <Route path="/schedules" element={<ScheduleView />} />
            <Route path="/payments" element={<div className="flex items-center justify-center h-full text-secondary font-bold uppercase tracking-widest">Payments Content</div>} />
          </Route>
          
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}