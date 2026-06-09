import { Menu } from 'lucide-react';

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
    </header>
  );
}
