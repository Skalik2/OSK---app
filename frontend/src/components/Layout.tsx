import { Outlet, useLocation, Navigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

export default function Layout() {
  const location = useLocation();
  
  const userRole = localStorage.getItem('userRole') as 'admin' | 'instructor' | 'student' | null;

  if (!userRole) {
    return <Navigate to="/" replace />;
  }
  
  const getTitle = () => {
    const path = location.pathname;
    if (path.includes('admin')) return 'Dashboard Overview';
    if (path.includes('instructor')) return 'Instructor Hub';
    if (path.includes('student')) return 'Your Progress Hub';
    if (path.includes('schedules')) return 'Calendar & Schedules';
    return 'DrivePro Portal';
  };

  return (
    <div className="min-h-screen bg-background">
      <Sidebar role={userRole} />
      <div className="flex flex-col min-h-screen">
        <Topbar title={getTitle()} />
        <main className="flex-1 ml-0 md:ml-[280px] p-6 md:p-10">
          <Outlet />
        </main>
      </div>
    </div>
  );
}