import { motion } from 'motion/react';
import { BookOpen, Car, Flag, ChevronLeft, ChevronRight, CheckCircle2, Wallet, ArrowRight, Calendar, User, Clock } from 'lucide-react';
import { useState } from 'react';

export default function StudentPortal() {
  const [selectedDate, setSelectedDate] = useState(7);
  const [selectedTime, setSelectedTime] = useState<string | null>('02:00 PM');

  const progressCards = [
    { title: 'Passed', desc: 'Completed on Oct 12, 2023. You are cleared for practical exams.', type: 'Theory', icon: BookOpen, color: 'bg-surface-container-high text-primary' },
    { title: '14 / 20 hrs', desc: 'Active session progress. Keep it up!', type: 'Active', icon: Car, progress: 70, color: 'bg-primary-container text-on-primary-container' },
    { title: 'Night Driving', desc: 'Required: 2 hours of post-sunset instruction. Not yet started.', type: 'Milestone', icon: Flag, color: 'bg-surface-container-high text-on-surface' },
  ];

  const upcomingDrives = [
    { date: 'Nov 12', title: 'City Driving Practice', time: '10:00 AM - 12:00 PM', instructor: 'Sarah Jenkins' },
    { date: 'Nov 18', title: 'Highway Intro', time: '01:00 PM - 03:00 PM', instructor: 'Mike Davis' },
  ];

  const lessonHistory = [
    { date: 'Oct 28, 2023', type: 'Parallel Parking Basics', instructor: 'Sarah Jenkins', status: 'Completed' },
    { date: 'Oct 21, 2023', type: 'Residential Navigation', instructor: 'Sarah Jenkins', status: 'Completed' },
    { date: 'Oct 14, 2023', type: 'Vehicle Familiarization', instructor: 'Mike Davis', status: 'Completed' },
  ];

  return (
    <div className="space-y-10">
      <div className="mb-10">
        <h2 className="text-3xl font-bold text-on-surface">Your Progress Hub</h2>
        <p className="text-lg text-on-surface-variant font-medium mt-1">Track your hours, book sessions, and prepare for your exam.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {progressCards.map((card, i) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-white border border-outline-variant rounded-2xl p-8 flex flex-col justify-between hover:shadow-lg transition-all"
          >
            <div className="flex justify-between items-start mb-8">
              <div className={`w-14 h-14 rounded-full flex items-center justify-center shadow-md ${card.color}`}>
                <card.icon className="w-7 h-7" />
              </div>
              <span className="bg-surface-container-high text-on-surface-variant font-bold text-[10px] uppercase tracking-widest px-4 py-1.5 rounded-full ring-1 ring-outline-variant/30">
                {card.type}
              </span>
            </div>
            <div>
              <h3 className="text-xl font-bold text-on-surface mb-2">{card.title}</h3>
              {card.progress !== undefined ? (
                <div className="space-y-3">
                  <div className="flex justify-between items-end">
                    <p className="text-sm font-medium text-on-surface-variant leading-relaxed">{card.desc}</p>
                    <span className="text-xs font-bold text-primary">{card.progress}%</span>
                  </div>
                  <div className="w-full bg-surface-container h-2 rounded-full overflow-hidden shadow-inner">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${card.progress}%` }}
                      transition={{ duration: 1 }}
                      className="bg-primary h-full rounded-full" 
                    />
                  </div>
                </div>
              ) : (
                <p className="text-sm font-medium text-on-surface-variant leading-relaxed">{card.desc}</p>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white border border-outline-variant rounded-2xl p-8 shadow-sm">
          <div className="flex justify-between items-center mb-8 pb-6 border-b border-outline-variant">
            <div>
              <h3 className="text-xl font-bold text-on-surface">Book a Lesson</h3>
              <p className="text-sm font-medium text-on-surface-variant mt-1">Select an available slot with your instructor.</p>
            </div>
            <div className="flex items-center gap-6">
              <button className="w-10 h-10 flex items-center justify-center rounded-xl border border-outline-variant hover:bg-surface-container transition-all">
                <ChevronLeft className="w-5 h-5 text-on-surface" />
              </button>
              <span className="text-lg font-bold text-on-surface">November 2023</span>
              <button className="w-10 h-10 flex items-center justify-center rounded-xl border border-outline-variant hover:bg-surface-container transition-all">
                <ChevronRight className="w-5 h-5 text-on-surface" />
              </button>
            </div>
          </div>

          <div className="grid grid-cols-7 gap-2 mb-10">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="text-center font-bold text-[10px] text-on-surface-variant uppercase tracking-widest py-3">{day}</div>
            ))}
            {[...Array(3)].map((_, i) => <div key={`empty-${i}`} className="aspect-square" />)}
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14].map(day => (
              <button
                key={day}
                onClick={() => setSelectedDate(day)}
                className={`aspect-square flex flex-col items-center justify-center rounded-xl border transition-all relative overflow-hidden group
                  ${selectedDate === day 
                    ? 'bg-primary border-primary text-white shadow-lg scale-105' 
                    : 'bg-white border-outline-variant text-on-surface hover:border-primary/50 hover:bg-surface-container-low'
                  }
                `}
              >
                <span className={`text-base font-bold ${selectedDate === day ? 'text-white' : 'text-on-surface'}`}>{day}</span>
                {(day === 5 || day === 10) && (
                  <div className={`w-1.5 h-1.5 rounded-full mt-1.5 ${selectedDate === day ? 'bg-white' : 'bg-primary'}`} />
                )}
              </button>
            ))}
          </div>

          <div className="bg-surface-container-low rounded-2xl p-6 border border-outline-variant shadow-inner">
            <h4 className="text-lg font-bold text-on-surface mb-6 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-primary" />
              Available on Nov {selectedDate}
            </h4>
            <div className="flex flex-wrap gap-4">
              {['09:00 AM', '11:30 AM', '02:00 PM', '04:00 PM'].map(time => (
                <button
                  key={time}
                  onClick={() => setSelectedTime(time)}
                  className={`px-6 py-2.5 rounded-xl border-2 font-bold text-sm transition-all
                    ${selectedTime === time 
                      ? 'bg-primary border-primary text-white shadow-md' 
                      : 'bg-white border-primary text-primary hover:bg-primary/5'
                    }
                  `}
                >
                  {time}
                </button>
              ))}
            </div>
            <div className="mt-8 flex justify-end">
              <button className="bg-primary-container text-on-primary-container font-bold text-sm px-10 py-3 rounded-full shadow-lg hover:shadow-xl hover:brightness-105 transition-all">
                Confirm Booking
              </button>
            </div>
          </div>
        </div>

        <section className="bg-white border border-outline-variant rounded-2xl p-8 flex flex-col shadow-sm">
          <h3 className="text-lg font-bold text-on-surface mb-8 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-primary" />
            Upcoming Drives
          </h3>
          <div className="flex flex-col gap-5 flex-1">
            {upcomingDrives.map((drive) => (
              <div key={drive.date} className="p-5 rounded-2xl bg-surface-container-low border border-outline-variant flex gap-5 items-start hover:shadow-md transition-shadow cursor-pointer">
                <div className="flex flex-col items-center justify-center bg-white border border-outline-variant/50 text-on-surface rounded-xl w-14 h-14 shrink-0 shadow-sm">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-primary">{drive.date.split(' ')[0]}</span>
                  <span className="text-lg font-bold leading-none">{drive.date.split(' ')[1]}</span>
                </div>
                <div className="space-y-1.5">
                  <h4 className="text-base font-bold text-on-surface leading-tight">{drive.title}</h4>
                  <p className="text-xs font-medium text-on-surface-variant flex items-center gap-2">
                    <Clock className="w-3.5 h-3.5 text-primary" /> {drive.time}
                  </p>
                  <p className="text-xs font-medium text-on-surface-variant flex items-center gap-2 text-primary font-bold">
                    <User className="w-3.5 h-3.5" /> Inst: {drive.instructor}
                  </p>
                </div>
              </div>
            ))}
          </div>
          <button className="mt-8 w-full py-3 border border-outline text-on-surface font-bold text-xs uppercase tracking-widest rounded-xl hover:bg-surface-container transition-all">
            View Full Schedule
          </button>
        </section>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white border border-outline-variant rounded-2xl overflow-hidden shadow-sm">
          <div className="p-8 border-b border-outline-variant flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-primary" />
            <h3 className="text-lg font-bold text-on-surface">Lesson History</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-surface-container-low border-b border-outline-variant text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">
                  <th className="px-8 py-5">Date</th>
                  <th className="px-8 py-5">Lesson Type</th>
                  <th className="px-8 py-5">Instructor</th>
                  <th className="px-8 py-5">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30">
                {lessonHistory.map((item) => (
                  <tr key={item.date} className="hover:bg-surface-container-low transition-colors">
                    <td className="px-8 py-5 text-sm font-bold text-on-surface">{item.date}</td>
                    <td className="px-8 py-5 text-sm font-medium text-on-surface-variant">{item.type}</td>
                    <td className="px-8 py-5 text-sm font-bold text-primary">{item.instructor}</td>
                    <td className="px-8 py-5">
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-variant text-on-surface text-[10px] font-bold border border-outline-variant shadow-sm uppercase tracking-wider">
                        <CheckCircle2 className="w-3 h-3 text-primary" /> Completed
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white border border-outline-variant rounded-2xl p-8 flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex items-center gap-3 mb-8">
              <div className="p-2.5 bg-primary-container/20 rounded-xl">
                <Wallet className="text-primary w-7 h-7" />
              </div>
              <h3 className="text-lg font-bold text-on-surface">Payment Status</h3>
            </div>
            <p className="text-xs font-medium text-on-surface-variant mb-8 leading-relaxed">Your account is currently up to date. Next installment due prior to final exam booking.</p>
            <div className="bg-surface-container-high rounded-2xl p-6 space-y-4 shadow-inner border border-outline-variant/30">
              <div className="flex justify-between items-center">
                <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Total Package</span>
                <span className="text-xl font-bold text-on-surface">$1,200</span>
              </div>
              <div className="flex justify-between items-center pt-4 border-t border-outline-variant/30">
                <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Paid to Date</span>
                <span className="text-xl font-bold text-primary">$800</span>
              </div>
            </div>
          </div>
          <button className="mt-8 w-full py-4 bg-inverse-surface text-inverse-on-surface font-bold text-sm rounded-xl shadow-lg hover:brightness-110 transition-all flex items-center justify-center gap-2">
            Make a Payment 
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
