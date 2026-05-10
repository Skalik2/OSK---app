import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

export default function Layout() {
  const location = useLocation();
  
  const getTitle = () => {
    const path = location.pathname;
    if (path.includes('admin')) return 'Dashboard Overview';
    if (path.includes('instructor')) return 'Instructor Hub';
    if (path.includes('student')) return 'Your Progress Hub';
    if (path.includes('schedules')) return 'Calendar & Schedules';
    return 'DrivePro Portal';
  };

  const getRole = (): 'admin' | 'instructor' | 'student' => {
    const path = location.pathname;
    if (path.includes('admin')) return 'admin';
    if (path.includes('instructor')) return 'instructor';
    if (path.includes('student')) return 'student';
    return 'admin';
  };

  return (
    <div className="min-h-screen bg-background">
      <Sidebar role={getRole()} />
      <div className="flex flex-col min-h-screen">
        <Topbar title={getTitle()} />
        <main className="flex-1 ml-0 md:ml-[280px] p-6 md:p-10">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
