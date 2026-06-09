import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';

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

interface InstructorProfile {
  id: string;
  first_name: string;
  last_name: string;
}

export default function StudentsView() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<InstructorProfile | null>(null);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (user?.role === 'instructor') {
          const profileRes = await api.get('/instructor/profile/me');
          setProfile(profileRes.data);
          
          const lessonsRes = await api.get(`/calendar/instructor/${profileRes.data.id}/lessons`);
          setLessons(lessonsRes.data);
        } else if (user?.role === 'admin') {
          // Admin could see all students, but for now we'll just show the lessons endpoint which is open for admins
          const lessonsRes = await api.get('/calendar/lessons');
          setLessons(lessonsRes.data);
        }
      } catch (err) {
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Extract unique students from lessons
  const studentsMap = new Map();
  lessons.forEach(l => {
    if (!studentsMap.has(l.student.id)) {
        const studentLessons = lessons.filter(sl => sl.student.id === l.student.id);
        
        // Sum actual duration of completed lessons in hours
        const completedHours = studentLessons
          .filter(sl => sl.status === 'COMPLETED')
          .reduce((totalTime, sl) => {
            const start = new Date(sl.start_time).getTime();
            const end = new Date(sl.end_time).getTime();
            const durationHours = (end - start) / (1000 * 60 * 60);
            return totalTime + durationHours;
          }, 0);

        const total = 30; // Updated target to 30 hours
        const completedFormatted = Number.isInteger(completedHours) ? completedHours : completedHours.toFixed(1);
        
        studentsMap.set(l.student.id, {
            name: `${l.student.first_name} ${l.student.last_name}`,
            hrs: `${completedFormatted}/${total}`,
            progress: Math.min(Math.round((completedHours / total) * 100), 100),
            status: completedHours >= total ? 'Ready for Final Exam' : 'Progressing well',
            color: completedHours >= total ? 'bg-primary' : 'bg-tertiary'
        });
    }
  });
  const students = Array.from(studentsMap.values());

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-on-surface">Assigned Students</h1>
        <p className="text-lg text-on-surface-variant font-medium mt-1">
          Monitor the progress of your assigned students.
        </p>
      </div>

      <section className="bg-white border border-outline-variant rounded-2xl p-8 shadow-sm">
        <div className="space-y-8">
          {students.length > 0 ? students.map((student) => (
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
          )) : (
            <p className="text-sm font-medium text-on-surface-variant text-center py-10">No students assigned.</p>
          )}
        </div>
      </section>
    </div>
  );
}