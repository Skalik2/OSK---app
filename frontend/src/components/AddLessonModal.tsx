import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import api from '../api/axios';

interface Student {
  id: string;
  first_name: string;
  last_name: string;
}

interface AddLessonModalProps {
  instructorId?: string;
  onClose: () => void;
  onSuccess: () => void;
}

export default function AddLessonModal({ instructorId, onClose, onSuccess }: AddLessonModalProps) {
  const [students, setStudents] = useState<Student[]>([]);
  const [studentId, setStudentId] = useState('');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [duration, setDuration] = useState('1');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [fetchedInstructorId, setFetchedInstructorId] = useState<string | null>(null);

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const response = await api.get('/student/profiles');
        setStudents(response.data);
      } catch (err) {
        console.error("Failed to fetch students", err);
      }
    };

    const fetchInstructor = async () => {
      if (!instructorId) {
        try {
          const response = await api.get('/instructor/profile/me');
          setFetchedInstructorId(response.data.id);
        } catch (err) {
          console.error("Failed to fetch instructor profile", err);
          setError("Failed to fetch instructor profile");
        }
      }
    };

    fetchStudents();
    fetchInstructor();
  }, [instructorId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!studentId || !date || !time) {
      setError('Please fill in all fields');
      return;
    }

    const finalInstructorId = instructorId || fetchedInstructorId;
    if (!finalInstructorId) {
      setError('Instructor profile not found');
      return;
    }

    setLoading(true);
    setError('');

    const startDateTime = new Date(`${date}T${time}:00`);
    const endDateTime = new Date(startDateTime.getTime() + parseFloat(duration) * 60 * 60 * 1000);

    try {
      await api.post('/calendar/lessons', {
        instructor_profile_id: finalInstructorId,
        student_profile_id: studentId,
        start_time: startDateTime.toISOString(),
        end_time: endDateTime.toISOString(),
        status: 'SCHEDULED'
      });
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to schedule lesson');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-xl overflow-hidden">
        <div className="flex justify-between items-center p-6 border-b border-outline-variant">
          <h2 className="text-xl font-bold text-on-surface">Add New Lesson</h2>
          <button onClick={onClose} className="text-on-surface-variant hover:text-on-surface">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && <div className="text-red-500 text-sm font-medium">{error}</div>}
          
          <div className="flex flex-col gap-1">
            <label className="text-sm font-bold text-on-surface">Student</label>
            <select 
              value={studentId} 
              onChange={(e) => setStudentId(e.target.value)}
              className="border border-outline-variant rounded-xl p-3 text-sm focus:outline-primary bg-white"
            >
              <option value="">Select a student...</option>
              {students.map(s => (
                <option key={s.id} value={s.id}>{s.first_name} {s.last_name}</option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-sm font-bold text-on-surface">Date</label>
            <input 
              type="date" 
              value={date} 
              onChange={(e) => setDate(e.target.value)}
              className="border border-outline-variant rounded-xl p-3 text-sm focus:outline-primary bg-white"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1">
              <label className="text-sm font-bold text-on-surface">Start Time</label>
              <input 
                type="time" 
                value={time} 
                onChange={(e) => setTime(e.target.value)}
                className="border border-outline-variant rounded-xl p-3 text-sm focus:outline-primary bg-white"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-bold text-on-surface">Duration</label>
              <select 
                value={duration} 
                onChange={(e) => setDuration(e.target.value)}
                className="border border-outline-variant rounded-xl p-3 text-sm focus:outline-primary bg-white"
              >
                <option value="1">1 hour</option>
                <option value="1.5">1.5 hours</option>
                <option value="2">2 hours</option>
              </select>
            </div>
          </div>

          <div className="pt-4 flex justify-end gap-3">
            <button 
              type="button" 
              onClick={onClose}
              className="px-5 py-2.5 font-bold text-on-surface-variant hover:bg-surface-container rounded-xl transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={loading}
              className="bg-primary text-white font-bold px-6 py-2.5 rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-70"
            >
              {loading ? 'Scheduling...' : 'Schedule Lesson'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}