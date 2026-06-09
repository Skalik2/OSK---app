import { motion } from 'motion/react';
import { Calendar, Timer, User, MapPin, Car, BookOpen, Plus } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import AddLessonModal from '../components/AddLessonModal';

interface InstructorProfile {
  id: string;
  first_name: string;
  last_name: string;
}

interface Student {
  id: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

interface Lesson {
  id: string;
  start_time: string;
  end_time: string;
  status: string;
  student: Student;
}

export default function InstructorDashboard() {
  const {  } = useAuth();
  const [profile, setProfile] = useState<InstructorProfile | null>(null);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchLessons = async (instructorId: string) => {
    try {
      const lessonsRes = await api.get(`/calendar/instructor/${instructorId}/lessons`);
      setLessons(lessonsRes.data);
    } catch (err) {
      console.error("Error fetching lessons:", err);
    }
  };

  const handleLessonAdded = () => {
    setIsModalOpen(false);
    if (profile?.id) {
      fetchLessons(profile.id);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const profileRes = await api.get('/instructor/profile/me');
        setProfile(profileRes.data);
        await fetchLessons(profileRes.data.id);
      } catch (err) {
        console.error("Error fetching instructor data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    const handleGlobalLessonAdded = () => {
      if (profile?.id) {
        fetchLessons(profile.id);
      }
    };

    window.addEventListener('lessonAdded', handleGlobalLessonAdded);
    return () => window.removeEventListener('lessonAdded', handleGlobalLessonAdded);
  }, [profile]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  const now = new Date();
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const schedule = lessons
    .filter(l => {
        const lessonDate = new Date(l.start_time);
        lessonDate.setHours(0, 0, 0, 0);
        return lessonDate.getTime() === today.getTime();
    })
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
    .map(l => {
      const start = new Date(l.start_time);
      return {
        time: start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }),
        period: start.getHours() >= 12 ? 'PM' : 'AM',
        title: `${l.student.first_name} ${l.student.last_name}`,
        desc: 'Driving Lesson',
        location: 'Standard Route',
        status: l.status === 'STARTED' ? 'Started' : (l.status === 'SCHEDULED' ? 'Upcoming' : l.status),
        type: 'car',
        initial: `${l.student.first_name[0]}${l.student.last_name[0]}`
      };
    });

  // Calculate stats
  const oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
  const lessonsThisWeek = lessons.filter(l => new Date(l.start_time) > oneWeekAgo).length;

  return (
    <div className="space-y-10">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h1 className="text-3xl font-bold text-on-surface">Good morning, {profile?.first_name || 'Sarah'}.</h1>
          <p className="text-lg text-on-surface-variant font-medium mt-1">
            You have {schedule.length} driving sessions scheduled for today.
          </p>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={() => setIsModalOpen(true)}
            className="bg-primary text-white font-bold px-6 py-2.5 rounded-xl hover:bg-primary/90 transition-all shadow-sm flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Add Lesson
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-white border border-outline-variant rounded-2xl p-8 shadow-sm">
            <div className="flex justify-between items-center border-b border-outline-variant pb-6 mb-8">
              <h2 className="text-xl font-bold text-on-surface">Today's Schedule</h2>
              <span className="bg-primary-container/20 text-on-primary-container font-bold text-xs px-4 py-1.5 rounded-full ring-1 ring-primary/20 uppercase tracking-widest">
                {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
              </span>
            </div>

            <div className="space-y-0 relative">
              <div className="absolute left-[3.45rem] top-6 bottom-6 w-0.5 bg-surface-container-high z-0" />
              
              {schedule.length > 0 ? schedule.map((item, i) => (
                <motion.div 
                  key={`${item.title}-${item.time}`}
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
              )) : (
                <div className="py-10 text-center text-on-surface-variant font-medium">
                  No lessons scheduled for today.
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="lg:col-span-4 flex flex-col gap-8">
          <div className="grid grid-cols-1 gap-4">
            <div className="bg-white border border-outline-variant rounded-2xl p-6 flex flex-col justify-center items-center text-center shadow-sm">
              <Timer className="text-primary w-8 h-8 mb-3" />
              <span className="text-3xl font-bold text-on-surface">{lessonsThisWeek * 2}h</span>
              <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mt-1">Driving This Week</span>
            </div>
          </div>
        </div>
      </div>
      {isModalOpen && profile && (
        <AddLessonModal 
          instructorId={profile.id}
          onClose={() => setIsModalOpen(false)}
          onSuccess={handleLessonAdded}
        />
      )}
    </div>
  );
}
