import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import AdminDashboard from './pages/AdminDashboard';
import InstructorDashboard from './pages/InstructorDashboard';
import StudentPortal from './pages/StudentPortal';
import ScheduleView from './pages/ScheduleView';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        
        <Route element={<Layout />}>
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/instructor" element={<InstructorDashboard />} />
          <Route path="/student" element={<StudentPortal />} />
          <Route path="/schedules" element={<ScheduleView />} />
          
          {/* Fallback routes for other nav items */}
          <Route path="/students" element={<div className="flex items-center justify-center h-full text-secondary font-bold uppercase tracking-widest">Students Management Content</div>} />
          <Route path="/instructors" element={<div className="flex items-center justify-center h-full text-secondary font-bold uppercase tracking-widest">Instructors Management Content</div>} />
          <Route path="/fleet" element={<div className="flex items-center justify-center h-full text-secondary font-bold uppercase tracking-widest">Fleet Management Content</div>} />
          <Route path="/payments" element={<div className="flex items-center justify-center h-full text-secondary font-bold uppercase tracking-widest">Payments Content</div>} />
          <Route path="/settings" element={<div className="flex items-center justify-center h-full text-secondary font-bold uppercase tracking-widest">Settings Content</div>} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
