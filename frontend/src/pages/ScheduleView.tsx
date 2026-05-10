import { ChevronLeft, ChevronRight, Filter, Plus, Clock, Car, User, Group } from 'lucide-react';
import { motion } from 'motion/react';

export default function ScheduleView() {
  const hours = ['8 AM', '9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM'];
  const days = [
    { name: 'Mon', date: '16' },
    { name: 'Tue', date: '17' },
    { name: 'Wed', date: '18', active: true },
    { name: 'Thu', date: '19' },
    { name: 'Fri', date: '20' },
    { name: 'Sat', date: '21', weekend: true },
    { name: 'Sun', date: '22', weekend: true },
  ];

  return (
    <div className="bg-white border border-outline-variant rounded-2xl overflow-hidden shadow-sm flex flex-col h-[calc(100vh-140px)]">
      <div className="px-8 py-5 border-b border-outline-variant bg-white flex flex-col md:flex-row justify-between items-start md:items-center gap-6 sticky top-0 z-10">
        <div className="flex items-center gap-8">
          <h1 className="text-2xl font-bold text-on-surface">October 2023</h1>
          <div className="flex items-center rounded-xl border border-outline-variant overflow-hidden bg-white shadow-sm ring-1 ring-black/5">
            <button className="px-5 py-2 hover:bg-surface-container font-bold text-xs uppercase tracking-widest text-on-surface-variant border-r border-outline-variant transition-colors">Month</button>
            <button className="px-5 py-2 bg-primary/10 text-primary font-bold text-xs uppercase tracking-widest border-r border-outline-variant transition-colors">Week</button>
            <button className="px-5 py-2 hover:bg-surface-container font-bold text-xs uppercase tracking-widest text-on-surface-variant transition-colors">Day</button>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 mr-2 rounded-xl border border-outline-variant text-on-surface font-bold text-xs uppercase tracking-widest hover:bg-surface-container transition-all">Today</button>
            <button className="p-1.5 rounded-lg hover:bg-surface-container text-on-surface-variant ring-1 ring-transparent hover:ring-outline-variant/30 transition-all">
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button className="p-1.5 rounded-lg hover:bg-surface-container text-on-surface-variant ring-1 ring-transparent hover:ring-outline-variant/30 transition-all">
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="relative group">
            <Filter className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant group-focus-within:text-primary transition-colors" />
            <select className="appearance-none bg-white border border-outline-variant rounded-xl pl-10 pr-10 py-2.5 font-bold text-xs text-on-surface-variant focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all uppercase tracking-widest">
              <option>All Instructors</option>
              <option>John Smith</option>
              <option>Sarah Davis</option>
              <option>Mike Johnson</option>
            </select>
          </div>
          <div className="relative group">
            <Car className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant group-focus-within:text-primary transition-colors" />
            <select className="appearance-none bg-white border border-outline-variant rounded-xl pl-10 pr-10 py-2.5 font-bold text-xs text-on-surface-variant focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all uppercase tracking-widest">
              <option>All Vehicles</option>
              <option>Car 1 (Sedan)</option>
              <option>Car 2 (SUV)</option>
              <option>Car 3 (Manual)</option>
            </select>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <div className="min-w-[1000px]">
          {/* Days Header */}
          <div className="grid grid-cols-[80px_repeat(7,1fr)] bg-white sticky top-0 z-10 border-b border-outline-variant">
            <div className="p-4 border-r border-outline-variant" />
            {days.map((day) => (
              <div 
                key={day.date} 
                className={`p-5 text-center border-r border-outline-variant flex flex-col items-center gap-1.5
                  ${day.active ? 'bg-primary/5' : ''}
                  ${day.weekend ? 'bg-surface-container-low/30' : ''}
                `}
              >
                <span className={`text-[10px] font-bold uppercase tracking-widest ${day.active ? 'text-primary' : 'text-on-surface-variant'}`}>{day.name}</span>
                <span className={`text-2xl font-bold ${day.active ? 'text-primary' : 'text-on-surface'}`}>{day.date}</span>
                {day.active && <div className="w-1.5 h-1.5 rounded-full bg-primary" />}
              </div>
            ))}
          </div>

          {/* Grid Body */}
          <div className="relative grid grid-cols-[80px_repeat(7,1fr)]">
            {hours.map((hour) => (
              <>
                <div key={`${hour}-label`} className="p-4 pt-4 border-r border-b border-outline-variant text-right bg-white">
                  <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-tighter">{hour}</span>
                </div>
                {[0, 1, 2, 3, 4, 5, 6].map((dayIndex) => (
                  <div 
                    key={`${hour}-${dayIndex}`} 
                    className={`border-r border-b border-outline-variant relative h-32
                      ${days[dayIndex].active ? 'bg-primary/5' : ''}
                      ${days[dayIndex].weekend ? 'bg-surface-container-low/10' : ''}
                    `}
                  />
                ))}
              </>
            ))}

            {/* Overlays */}
            {/* Event: Mon 8-10 AM */}
            <div className="absolute left-[80px] top-0 w-[calc((100%-80px)/7)] h-64 p-1.5">
              <motion.div 
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="bg-primary/10 border-l-4 border-primary rounded-xl p-4 h-full shadow-sm hover:shadow-lg transition-all cursor-pointer group relative overflow-hidden"
              >
                <div className="bg-primary/5 absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                <p className="text-[10px] font-bold text-primary uppercase tracking-widest mb-1.5">8:00 AM - 10:00 AM</p>
                <h4 className="text-sm font-bold text-on-surface mb-2 leading-tight">In-Car: Jane Doe</h4>
                <div className="space-y-1.5 border-t border-primary/20 pt-2.5">
                  <div className="flex items-center gap-2 text-xs font-medium text-on-surface-variant">
                    <Car className="w-3.5 h-3.5 text-primary" /> Car 1
                  </div>
                  <div className="flex items-center gap-2 text-xs font-medium text-on-surface-variant">
                    <User className="w-3.5 h-3.5 text-primary" /> M. Johnson
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Event: Tue 9-12 AM */}
            <div className="absolute left-[calc(80px+(100%-80px)/7)] top-32 w-[calc((100%-80px)/7)] h-96 p-1.5">
              <motion.div 
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="bg-tertiary-container/20 border-l-4 border-tertiary rounded-xl p-4 h-full shadow-sm hover:shadow-lg transition-all cursor-pointer group"
              >
                <p className="text-[10px] font-bold text-tertiary uppercase tracking-widest mb-1.5">9:00 AM - 12:00 PM</p>
                <h4 className="text-sm font-bold text-on-surface mb-2 leading-tight">Classroom Module A</h4>
                <div className="space-y-1.5 border-t border-tertiary/20 pt-2.5">
                  <div className="flex items-center gap-2 text-xs font-medium text-on-surface-variant">
                    <User className="w-3.5 h-3.5 text-tertiary" /> Room 101
                  </div>
                  <div className="flex items-center gap-2 text-xs font-medium text-on-surface-variant">
                    <Group className="w-3.5 h-3.5 text-tertiary" /> 12 Students
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Event: Wed 10-11 AM (Dashed/Dragging) */}
            <div className="absolute left-[calc(80px+(100%-80px)/7*2)] top-64 w-[calc((100%-80px)/7)] h-32 p-1.5 z-20">
              <div className="bg-primary-container/10 border-2 border-dashed border-primary/50 rounded-xl p-4 h-full flex flex-col justify-center items-center text-center">
                <p className="text-[10px] font-bold text-primary uppercase tracking-widest mb-1">10:00 - 11:00 AM</p>
                <h4 className="text-xs font-bold text-on-surface uppercase">Evaluation</h4>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="px-8 py-4 border-t border-outline-variant bg-surface-container-low flex gap-10 items-center justify-center">
        <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Legend:</span>
        <div className="flex items-center gap-2.5">
          <div className="w-3 h-3 rounded-full bg-primary" />
          <span className="text-xs font-bold text-on-surface uppercase tracking-wide">In-Car Lesson</span>
        </div>
        <div className="flex items-center gap-2.5">
          <div className="w-3 h-3 rounded-full bg-tertiary" />
          <span className="text-xs font-bold text-on-surface uppercase tracking-wide">Classroom Session</span>
        </div>
        <div className="flex items-center gap-2.5">
          <div className="w-3 h-3 rounded-full bg-secondary" />
          <span className="text-xs font-bold text-on-surface uppercase tracking-wide">Admin/Maintenance</span>
        </div>
      </div>
    </div>
  );
}
