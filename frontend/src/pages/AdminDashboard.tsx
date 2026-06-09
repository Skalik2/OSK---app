import { motion } from 'motion/react';
import { School, Users, CreditCard, Car, CheckCircle2, RefreshCw, Calendar, XCircle, AlertTriangle, Info, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import api from '../api/axios';

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, profileRes] = await Promise.all([
          api.get('/admin/stats'),
          api.get('/admin/profile/me')
        ]);
        setStats(statsRes.data);
        setProfile(profileRes.data);
      } catch (error) {
        console.error("Failed to fetch admin data", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-64px)]">
        <Loader2 className="w-12 h-12 animate-spin text-primary" />
      </div>
    );
  }

  const metrics = [
    { label: 'Total Students', value: stats?.total_students || 0, change: 'Live count', icon: School, color: 'bg-tertiary-container text-on-tertiary-container' },
    { label: 'Active Instructors', value: stats?.total_instructors || 0, change: 'Live count', icon: Users, color: 'bg-primary-fixed text-on-primary-fixed' },
    { label: 'Total Lessons', value: stats?.total_lessons || 0, change: 'Total scheduled', icon: Calendar, color: 'bg-secondary-container text-on-secondary-container' },
    { label: 'Estimated Revenue', value: `$${stats?.revenue || 0}`, change: 'Current month', icon: CreditCard, color: 'bg-surface-container-highest text-on-surface' },
  ];

  const activities = [
    // These could be fetched from a real audit log if implemented
    { name: profile?.first_name + ' ' + profile?.last_name, role: 'Admin', action: 'Accessed Dashboard', status: 'Completed', time: 'Just now', initial: profile?.first_name?.[0] || 'A' },
  ];

  const alerts = [
    { title: 'System Online', desc: 'All microservices are communicating correctly.', type: 'info', icon: Info },
  ];

  return (
    <div className="space-y-10">
      <div className="mb-10">
        <h2 className="text-3xl font-bold text-on-surface">Welcome back, {profile?.first_name || 'Admin'}</h2>
        <p className="text-lg text-on-surface-variant font-medium mt-1">Platform Status: Healthy. Position: {profile?.position || 'Administrator'}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((m, i) => (
          <motion.div
            key={m.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-white border border-outline-variant rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start mb-6">
              <div className={`p-2.5 rounded-xl ${m.color}`}>
                <m.icon className="w-6 h-6" />
              </div>
              <span className="text-[10px] font-bold text-secondary uppercase tracking-wider bg-surface-container-low px-2 py-1 rounded-md border border-outline-variant/30">
                {m.change}
              </span>
            </div>
            <div>
              <p className="text-xs font-bold text-secondary uppercase tracking-widest mb-1">{m.label}</p>
              <h3 className="text-3xl font-bold text-on-surface">{m.value}</h3>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2 bg-white border border-outline-variant rounded-2xl overflow-hidden shadow-sm">
          <div className="px-6 py-4 border-b border-outline-variant bg-surface-container-low flex justify-between items-center">
            <h3 className="text-lg font-bold text-on-surface">Recent Activities</h3>
            <button className="text-sm font-bold text-primary hover:underline">View All</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-outline-variant/50 text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">
                  <th className="px-6 py-4">User</th>
                  <th className="px-6 py-4">Action</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/30">
                {activities.map((a, i) => (
                  <tr key={i} className="hover:bg-surface-container-low/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary-fixed text-on-primary-fixed flex items-center justify-center text-xs font-bold ring-1 ring-white shadow-sm">
                          {a.initial}
                        </div>
                        <div>
                          <p className="text-sm font-bold text-on-surface leading-tight">{a.name}</p>
                          <p className="text-[10px] font-medium text-on-surface-variant uppercase tracking-wide">{a.role}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-on-surface">{a.action}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold border ${
                        a.status === 'Completed' ? 'bg-tertiary-container/20 text-tertiary border-tertiary/20' :
                        a.status === 'Updated' ? 'bg-surface-variant/50 text-on-surface-variant border-outline-variant' :
                        a.status === 'Scheduled' ? 'bg-primary-container/10 text-primary border-primary/20' :
                        'bg-error-container/20 text-error border-error/20'
                      }`}>
                        {a.status === 'Completed' && <CheckCircle2 className="w-3 h-3" />}
                        {a.status === 'Updated' && <RefreshCw className="w-3 h-3" />}
                        {a.status === 'Scheduled' && <Calendar className="w-3 h-3" />}
                        {a.status === 'Cancelled' && <XCircle className="w-3 h-3" />}
                        {a.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs font-medium text-on-surface-variant">{a.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="bg-white border border-outline-variant rounded-2xl overflow-hidden shadow-sm flex flex-col">
          <div className="px-6 py-4 border-b border-outline-variant bg-surface-container-low flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-bold text-on-surface">System Alerts</h3>
          </div>
          <div className="p-6 flex flex-col gap-4">
            {alerts.map((alert) => (
              <div 
                key={alert.title}
                className={`p-4 rounded-xl border flex gap-4 ${
                  alert.type === 'error' ? 'bg-error-container/5 text-on-surface border-error/10' :
                  alert.type === 'warning' ? 'bg-primary-container/5 text-on-surface border-primary-container/20' :
                  'bg-surface-container text-on-surface border-outline-variant'
                }`}
              >
                <div className={`p-2 rounded-lg shrink-0 h-fit ${
                  alert.type === 'error' ? 'text-error bg-error-container/20' :
                  alert.type === 'warning' ? 'text-primary bg-primary-container/20' :
                  'text-secondary bg-surface-container-highest'
                }`}>
                  <alert.icon className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold leading-tight">{alert.title}</h4>
                  <p className="text-xs font-medium text-on-surface-variant mt-1 leading-relaxed">{alert.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

