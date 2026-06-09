import { Car, User, Phone, CloudSun, Trash2 } from 'lucide-react';
import { motion } from 'motion/react';
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';

const getDuration = (start: string, end: string) => {
  const diff = new Date(end).getTime() - new Date(start).getTime();
  const hours = diff / (1000 * 60 * 60);
  return `${hours % 1 === 0 ? hours : hours.toFixed(1)}h`;
};

const formatTime = (date: string) => {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
};

interface Weather {
  max_temp?: { parsedValue: number };
  description?: string;
}

interface UserDetails {
  first_name: string;
  last_name: string;
  phone?: string;
}

interface Lesson {
  id: string;
  start_time: string;
  end_time: string;
  status: string;
  student: UserDetails;
  instructor: UserDetails;
  weather?: Weather;
}

export default function ScheduleView() {
  const { user } = useAuth();
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchLessons = async () => {
    if (!user) return;
    
    try {
      setIsLoading(true);
      const response = await api.get('/calendar/my_lessons');
      setLessons(response.data || []);
    } catch (error) {
      console.error("Failed to fetch schedule", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLessons();
  }, [user]);

  const handleDeleteLesson = async (lessonId: string) => {
    if (!window.confirm("Are you sure you want to delete this scheduled lesson?")) {
      return;
    }

    try {
      await api.delete(`/calendar/lessons/${lessonId}`);
      fetchLessons();
    } catch (error) {
      console.error("Failed to delete lesson", error);
      alert("Failed to delete lesson.");
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-on-surface">Harmonogram</h1>
        <p className="text-lg text-on-surface-variant font-medium mt-1">
          Lista wszystkich zaplanowanych lekcji.
        </p>
      </div>

      <div className="flex flex-col gap-4">
        {lessons.length === 0 ? (
          <div className="bg-white border border-outline-variant rounded-2xl p-12 text-center shadow-sm">
            <p className="text-on-surface-variant font-medium">Brak zaplanowanych lekcji.</p>
          </div>
        ) : (
          lessons.map((lesson, i) => (
            <motion.div 
              key={lesson.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-white border border-outline-variant rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:shadow-md transition-all"
            >
              <div className="flex items-center gap-6">
                <div className="flex flex-col items-center justify-center bg-surface-container-high rounded-lg p-3 min-w-[120px]">
                  <span className="text-xs font-bold text-on-surface-variant uppercase tracking-tighter">
                    {new Date(lesson.start_time).toLocaleDateString([], { day: 'numeric', month: 'short' })}
                  </span>
                  <span className="text-lg font-bold text-primary">
                    {formatTime(lesson.start_time)} - {formatTime(lesson.end_time)}
                  </span>
                  <span className="text-[10px] font-bold text-on-surface-variant/70 uppercase">
                    Duration: {getDuration(lesson.start_time, lesson.end_time)}
                  </span>
                </div>
                
                <div>
                  <h3 className="text-base font-bold text-on-surface">
                    {lesson.student?.first_name} {lesson.student?.last_name}
                  </h3>
                  <div className="flex items-center gap-4 mt-1">
                    <div className="flex items-center gap-2 text-sm text-on-surface-variant">
                      <User className="w-4 h-4 text-primary/60" />
                      <span>Instruktor: {lesson.instructor?.first_name} {lesson.instructor?.last_name}</span>
                    </div>
                    {lesson.instructor?.phone && (
                      <div className="flex items-center gap-2 text-sm text-on-surface-variant">
                        <Phone className="w-3.5 h-3.5 text-primary/60" />
                        <span className="font-medium text-xs">{lesson.instructor.phone}</span>
                      </div>
                    )}
                  </div>
                  {lesson.weather && (
                    <div className="flex items-center gap-2 text-[10px] font-bold text-on-surface-variant/60 mt-2 bg-primary/5 px-2 py-0.5 rounded-full w-fit">
                      <CloudSun className="w-3 h-3" />
                      <span>{lesson.weather.max_temp?.parsedValue}°C • {lesson.weather.description}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between md:justify-end gap-6 border-t md:border-t-0 pt-4 md:pt-0">
                <div className="flex items-center gap-2 text-sm text-on-surface-variant">
                  <Car className="w-4 h-4 text-primary/60" />
                  <span>Status: {lesson.status}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-widest ring-1 ring-inset ${
                    lesson.status === 'COMPLETED' ? 'bg-green-50 text-green-700 ring-green-600/20' : 
                    lesson.status === 'STARTED' ? 'bg-primary/10 text-primary ring-primary/20' :
                    'bg-surface-container-high text-on-surface-variant ring-outline-variant'
                  }`}>
                    {lesson.status}
                  </span>
                  {user?.role === 'instructor' && lesson.status === 'SCHEDULED' && (
                    <button 
                      onClick={() => handleDeleteLesson(lesson.id)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50 p-2 rounded-full transition-colors"
                      title="Delete scheduled lesson"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
}

