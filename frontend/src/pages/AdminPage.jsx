import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../api/client";
import { useAuth } from "../context/AuthContext";
import { StatCard, TabButton, UsersTable, JobsList, InterviewsTable } from "../components/ui";

export default function AdminPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [interviews, setInterviews] = useState([]);
  const [tab, setTab] = useState("users");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const isAdmin = user?.role?.toLowerCase() === "admin";

  const loadStats = useCallback(async () => {
    try { const res = await apiClient.get("/admin/dashboard-stats"); setStats(res.data); } catch { /* ignore */ }
  }, []);

  const loadUsers = useCallback(async () => {
    try { const res = await apiClient.get("/admin/users"); setUsers(res.data); } catch { setError("Failed to load users. Admin access required."); }
  }, []);

  const loadJobs = useCallback(async () => {
    try { const res = await apiClient.get("/admin/jobs"); setJobs(res.data); } catch { /* ignore */ }
  }, []);

  const loadInterviews = useCallback(async () => {
    try { const res = await apiClient.get("/admin/interviews"); setInterviews(res.data); } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    if (!isAdmin) { setLoading(false); return; }
    Promise.all([loadStats(), loadUsers(), loadJobs(), loadInterviews()]).finally(() => setLoading(false));
  }, [isAdmin, loadStats, loadUsers, loadJobs, loadInterviews]);

  const toggleActive = async (u) => {
    try { await apiClient.post(`/admin/users/${u.id}/toggle-active`); setUsers(prev => prev.map(item => item.id === u.id ? { ...item, is_active: !item.is_active } : item)); }
    catch (err) { alert(err?.response?.data?.detail || "Failed to update user"); }
  };

  if (!isAdmin) {
    return (
      <div className="mx-auto mt-16 max-w-lg rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-2">Admin Console</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">This section is only available to platform administrators.</p>
        <button onClick={() => navigate("/")} className="text-sm px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">Go Home</button>
      </div>
    );
  }

  const statCards = [
    { label: "Candidates", value: stats?.total_candidates ?? "-", accent: "text-indigo-600" },
    { label: "Recruiters", value: stats?.total_recruiters ?? "-", accent: "text-purple-600" },
    { label: "Total Users", value: stats?.total_users ?? "-", accent: "text-emerald-600" },
    { label: "Jobs Posted", value: stats?.total_jobs ?? "-", accent: "text-amber-600" },
    { label: "Applications", value: stats?.total_applications ?? "-", accent: "text-rose-600" },
    { label: "Mock Interviews", value: stats?.total_interviews ?? "-", accent: "text-indigo-600" },
  ];

  return (
    <div className="mx-auto max-w-6xl space-y-8 py-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Admin Console</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Platform overview and user management.</p>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-3 rounded-lg">{error}</div>}

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">{statCards.map((card) => <StatCard key={card.label} label={card.label} value={card.value} icon={<span className="text-lg">{card.label === "Candidates" ? "👤" : card.label === "Recruiters" ? "👥" : card.label === "Jobs Posted" ? "💼" : card.label === "Applications" ? "📄" : card.label === "Mock Interviews" ? "🎤" : "👤"}</span>} iconBg={card.accent === "text-indigo-600" ? "bg-indigo-100" : card.accent === "text-purple-600" ? "bg-purple-100" : card.accent === "text-amber-600" ? "bg-amber-100" : card.accent === "text-rose-600" ? "bg-rose-100" : "bg-emerald-100"} />)}</div>

      <div className="flex gap-2 flex-wrap">
        <TabButton key="users" active={tab === "users"} onClick={() => setTab("users")} label={`Users (${users.length})`} />
        <TabButton key="jobs" active={tab === "jobs"} onClick={() => setTab("jobs")} label={`Jobs (${jobs.length})`} />
        <TabButton key="interviews" active={tab === "interviews"} onClick={() => setTab("interviews")} label={`Interviews (${interviews.length})`} />
      </div>

      {loading ? (
        <p className="text-sm text-slate-400 text-center py-10">Loading...</p>
      ) : (
        <>
          {tab === "users" && <UsersTable users={users} toggleActive={toggleActive} currentUser={user} />}
          {tab === "jobs" && <JobsList jobs={jobs} onEdit={() => {}} onDelete={() => {}} />}
          {tab === "interviews" && <InterviewsTable interviews={interviews} />}
        </>
      )}
    </div>
  );
}
