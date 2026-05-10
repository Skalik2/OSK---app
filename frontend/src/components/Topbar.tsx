import { Search, Bell, HelpCircle, Menu } from 'lucide-react';

interface TopbarProps {
  title: string;
}

export default function Topbar({ title }: TopbarProps) {
  return (
    <header className="h-16 border-b border-outline-variant bg-white flex items-center justify-between px-6 md:px-10 sticky top-0 z-30 ml-0 md:ml-[280px]">
      <div className="flex items-center gap-4">
        <button className="md:hidden p-2 hover:bg-surface-container rounded-lg">
          <Menu className="w-6 h-6 text-secondary" />
        </button>
        <h2 className="text-lg font-semibold text-on-surface">{title}</h2>
      </div>

      <div className="flex items-center gap-6">
        <div className="hidden md:flex items-center gap-2 bg-surface-container-low px-4 py-2 rounded-full border border-outline-variant focus-within:border-primary transition-all">
          <Search className="w-4 h-4 text-secondary" />
          <input 
            type="text" 
            placeholder="Search students, instructors..." 
            className="bg-transparent border-none focus:ring-0 text-sm outline-none w-64"
          />
        </div>

        <div className="flex items-center gap-4 text-secondary">
          <button className="relative p-1 hover:text-primary transition-colors">
            <Bell className="w-5 h-5" />
            <span className="absolute top-0 right-0 w-2 h-2 bg-error rounded-full ring-2 ring-white"></span>
          </button>
          <button className="p-1 hover:text-primary transition-colors">
            <HelpCircle className="w-5 h-5" />
          </button>
        </div>

        <div className="flex items-center gap-2 pl-4 border-l border-outline-variant">
          <img 
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuCc7Hd9I5a2AY0-CcQIwdlYY_bFFMswOOtwP5FPL88BAQfq9ltX639-GmS6Y4XSr6JCx4JOQ8CJYLhtkBZwvO7Dd2nK4dteesovdtFHXXlGHBKU-6gzuqHKEY-H0zdqSZ_b_nDd1xCBL8HY-UWagxuQjcJCO-1wrJ_kPUd5hHon--5J2B9jBlagaZP499dPNdjlBUhqBwfNy9_xvy31TFwMdCQgLFNr6DuRRRYMItiODUaaTmfRXCKHsgWjJcGkTW3OISs7QYekvD8" 
            alt="User" 
            className="w-8 h-8 rounded-full object-cover ring-1 ring-outline-variant"
          />
        </div>
      </div>
    </header>
  );
}
