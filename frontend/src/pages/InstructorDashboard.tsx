import { motion } from 'motion/react';
import { Calendar, Timer, CheckCircle2, User, MapPin, Car, BookOpen } from 'lucide-react';

export default function InstructorDashboard() {
  const schedule = [
    { time: '09:00', period: 'AM', title: 'Michael Johnson', desc: 'In-Car Lesson', location: 'Downtown Training Route A', status: 'Started', type: 'car', initial: 'MJ' },
    { time: '11:30', period: 'AM', title: 'Emily Chen', desc: 'Classroom Theory', location: 'Main Office, Room 2B', status: 'Upcoming', type: 'class', initial: 'ES' },
    { time: '02:00', period: 'PM', title: 'David Bowles', desc: 'Highway Practice', location: 'North Suburbs Route', status: 'Upcoming', type: 'car', initial: 'DB' },
  ];

  const students = [
    { name: 'Sarah Connor', hrs: '18/20', progress: 90, status: 'Ready for Final Exam', color: 'bg-primary' },
    { name: 'John Smith', hrs: '5/20', progress: 25, status: 'Needs parallel parking focus', color: 'bg-tertiary' },
    { name: 'Alicia Keys', hrs: '12/20', progress: 60, status: 'Progressing well', color: 'bg-primary' },
    { name: 'Tom Hardy', hrs: '2/20', progress: 10, status: 'Just started', color: 'bg-outline' },
  ];

  return (
    <div className="space-y-10">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h1 className="text-3xl font-bold text-on-surface">Good morning, Sarah.</h1>
          <p className="text-lg text-on-surface-variant font-medium mt-1">You have 4 driving sessions scheduled for today.</p>
        </div>
        <button className="bg-white border border-outline text-on-surface font-bold px-6 py-2.5 rounded-xl hover:bg-surface-container transition-all shadow-sm flex items-center gap-2">
          <Calendar className="w-5 h-5 text-primary" />
          View Full Calendar
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-white border border-outline-variant rounded-2xl p-8 shadow-sm">
            <div className="flex justify-between items-center border-b border-outline-variant pb-6 mb-8">
              <h2 className="text-xl font-bold text-on-surface">Today's Schedule</h2>
              <span className="bg-primary-container/20 text-on-primary-container font-bold text-xs px-4 py-1.5 rounded-full ring-1 ring-primary/20 uppercase tracking-widest">
                Oct 24, 2023
              </span>
            </div>

            <div className="space-y-0 relative">
              <div className="absolute left-[3.45rem] top-6 bottom-6 w-0.5 bg-surface-container-high z-0" />
              
              {schedule.map((item, i) => (
                <motion.div 
                  key={item.time}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="flex gap-8 relative z-10 group"
                >
                  <div className="flex flex-col items-end w-16 pt-4 shrink-0 bg-white">
                    <span className="text-lg font-bold text-on-surface">{item.time}</span>
                    <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">{item.period}</span>
                  </div>
                  
                  <div className={`mt-6 w-3 h-3 rounded-full border-2 border-white shadow-sm shrink-0 transition-colors ${
                    item.status === 'Started' ? 'bg-primary' : 'bg-outline group-hover:bg-primary'
                  }`} />

                  <div className="flex-1 bg-surface-container-low border border-outline-variant rounded-2xl p-5 mb-6 hover:shadow-lg hover:border-primary/30 transition-all cursor-pointer">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm shadow-md ring-2 ring-white
                          ${item.type === 'car' ? 'bg-tertiary-container text-on-tertiary-container' : 'bg-secondary-container text-on-secondary-container'}
                        `}>
                          {item.initial}
                        </div>
                        <div>
                          <h3 className="text-base font-bold text-on-surface">{item.title}</h3>
                          <div className="text-xs font-medium text-on-surface-variant flex items-center gap-1.5 mt-0.5">
                            {item.type === 'car' ? <Car className="w-3.5 h-3.5" /> : <BookOpen className="w-3.5 h-3.5" />}
                            <span>{item.desc}</span>
                          </div>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider ${
                        item.status === 'Started' ? 'bg-primary text-white' : 'bg-white text-on-surface-variant'
                      }`}>
                        {item.status}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-xs font-medium text-on-surface-variant pt-2 border-t border-outline-variant/30">
                      <MapPin className="w-4 h-4 text-primary" />
                      <span>{item.location}</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        <div className="lg:col-span-4 flex flex-col gap-8">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white border border-outline-variant rounded-2xl p-6 flex flex-col justify-center items-center text-center shadow-sm">
              <Timer className="text-primary w-8 h-8 mb-3" />
              <span className="text-3xl font-bold text-on-surface">12h</span>
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mt-1">Driving This Week</span>
            </div>
            <div className="bg-white border border-outline-variant rounded-2xl p-6 flex flex-col justify-center items-center text-center shadow-sm">
              <CheckCircle2 className="text-tertiary w-8 h-8 mb-3" />
              <span className="text-3xl font-bold text-on-surface">85%</span>
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mt-1">Pass Rate</span>
            </div>
          </div>

          <section className="bg-white border border-outline-variant rounded-2xl p-8 shadow-sm flex-grow">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-lg font-bold text-on-surface">Assigned Students</h2>
              <button className="text-primary font-bold text-xs uppercase tracking-widest hover:underline">View All</button>
            </div>
            <div className="space-y-8">
              {students.map((student) => (
                <div key={student.name} className="flex flex-col gap-2.5">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-bold text-on-surface">{student.name}</span>
                    <span className="text-xs font-bold text-on-surface-variant">{student.hrs} Hrs</span>
                  </div>
                  <div className="w-full bg-surface-container h-2 rounded-full overflow-hidden shadow-inner">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${student.progress}%` }}
                      transition={{ duration: 1, ease: 'easeOut' }}
                      className={`${student.color} h-full rounded-full`} 
                    />
                  </div>
                  <p className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wide">{student.status}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
