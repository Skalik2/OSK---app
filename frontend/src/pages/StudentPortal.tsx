import { motion } from 'motion/react';
import { BookOpen, Car, Flag } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';

interface StudentProfile {
  id: string;
  first_name: string;
  last_name: string;
}

interface Course {
  id: string;
  category: string;
  required_hours: number;
  completed_hours: number;
  payment_status: string;
}

export default function StudentPortal() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const profileRes = await api.get('/student/profile/me');
        setProfile(profileRes.data);
        
        const coursesRes = await api.get('/student/courses/my_all');
        setCourses(coursesRes.data);
      } catch (err) {
        console.error("Error fetching student data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const activeCourse = courses[0];

  const courseProgress = activeCourse && activeCourse.required_hours > 0 
    ? Math.round((activeCourse.completed_hours / activeCourse.required_hours) * 100) 
    : 0;

  const progressCards = [
    { 
      title: activeCourse ? `${activeCourse.category} Category` : 'Theory', 
      desc: activeCourse ? `Currently attending ${activeCourse.category} course` : 'No active course found.', 
      type: 'Cat', 
      icon: BookOpen, 
      color: 'bg-surface-container-high text-primary' 
    },
    { 
      title: activeCourse ? `${activeCourse.completed_hours} / ${activeCourse.required_hours} hrs` : '0 / 0 hrs', 
      desc: 'Active session progress. Keep it up!', 
      type: 'Active', 
      icon: Car, 
      progress: courseProgress, 
      color: 'bg-primary-container text-on-primary-container' 
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <div className="mb-10">
        <h2 className="text-3xl font-bold text-on-surface">Hello, {profile?.first_name || 'Student'}!</h2>
        <p className="text-lg text-on-surface-variant font-medium mt-1">Track your hours and prepare for your exam.</p>
      </div>

      {courses.length === 0 ? (
        <div className="bg-white border border-outline-variant rounded-2xl p-12 text-center shadow-sm">
          <BookOpen className="w-16 h-16 text-primary/40 mx-auto mb-6" />
          <h3 className="text-xl font-bold text-on-surface mb-2">No Active Courses</h3>
          <p className="text-on-surface-variant max-w-md mx-auto">
            You are not currently enrolled in any active courses. Please contact the administrator to get started.
          </p>
        </div>
      ) : (
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
      )}
    </div>
  );
}
