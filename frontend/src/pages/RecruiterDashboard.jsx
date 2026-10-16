import { useState, useEffect, useMemo, useCallback, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import apiClient from "../api/client";
import {
  JobPostingCard,
  JobFormModal,
  PipelineTable,
  ApplicantRowModal,
  Toast,
  AnalyticsCharts,
} from "../components/ui";
import { useAuth } from "../context/AuthContext";

export default function RecruiterDashboard() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeSection = ["jobs", "candidates", "analytics"].includes(searchParams.get("section")) ? searchParams.get("section") : "candidates";

  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [allApplications, setAllApplications] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [activeModalApp, setActiveModalApp] = useState(null);

  const [profile, setProfile] = useState(null);
  const [profileForm, setProfileForm] = useState({ company_name: "", designation: "", company_description: "" });
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileError, setProfileError] = useState("");

  const [showJobModal, setShowJobModal] = useState(false);
  const [editingJob, setEditingJob] = useState(null);
  const [jobForm, setJobForm] = useState({ title: "", location: "", job_type: "full-time", description: "", required_skills: "", experience_required: "", salary: "" });
  const [creatingJob, setCreatingJob] = useState(false);
  const [jobError, setJobError] = useState("");

  const [search, setSearch] = useState("");
  const [sortMode, setSortMode] = useState("score");
  const [pageSize, setPageSize] = useState(20);
  const [page, setPage] = useState(1);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [stageFilter, setStageFilter] = useState("all");
  const [bulkUpdating, setBulkUpdating] = useState(false);
  const [toast, setToast] = useState(null);
  const toastTimer = useRef(null);

  const [showProfileModal, setShowProfileModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [company, setCompany] = useState(null);

  const showToast = useCallback((message, type = "success") => {
    setToast({ message, type });
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 2600);
  }, []);

  const fetchRecruiterProfile = async () => {
    try {
      const res = await apiClient.get("/recruiter-profile/me");
      setProfile(res.data);
      setProfileForm({ company_name: res.data.company_name || "", designation: res.data.designation || "", company_description: res.data.company_description || "" });
    } catch (err) { if (err.response?.status === 404) setShowProfileModal(true); }
  };

  const fetchJobs = async () => { try { const res = await apiClient.get("/jobs/recruiter/me"); setJobs(res.data); } catch (err) { console.error("Failed to load jobs:", err); } };

  const fetchApplications = async () => {
    try { const res = await apiClient.get("/applications/recruiter"); setAllApplications(res.data); } catch (err) { console.error("Failed to load applications:", err); }
  };

  useEffect(() => {
    fetchRecruiterProfile();
    fetchJobs();
    fetchApplications();
    setLoading(false);
  }, []);

  // Listen for the Manage Company event dispatched from the company menu
  useEffect(() => {
    if (user?.role?.toLowerCase() !== "recruiter") return;
    const handleManageCompany = () => setShowProfileModal(true);
    window.addEventListener("aihire:manage-company", handleManageCompany);
    return () => window.removeEventListener("aihire:manage-company", handleManageCompany);
  }, [user]);

  const fetchRankedApps = useCallback(async (job) => {
    setSelectedJob(job); setStageFilter("all"); setSortMode("score"); setPage(1); setSelectedIds(new Set());
    try { const res = await apiClient.get(`/jobs/${job.id}/applications/ranked`); setApplications(res.data); } catch (err) { console.error("Failed to load ranked apps:", err); }
  }, []);

  const openJobPipeline = (job) => { fetchRankedApps(job); setSearchParams({ section: "candidates" }, { replace: true }); };

  const showAllApplications = () => { setSelectedJob(null); setStageFilter("all"); setSortMode("date"); setPage(1); setSelectedIds(new Set()); };

  const handleProfileSubmit = async (form) => {
    setSavingProfile(true); setProfileError("");
    try {
      const method = profile ? "put" : "post";
      const endpoint = profile ? "/recruiter-profile/me" : "/recruiter-profile";
      const res = await apiClient[method](endpoint, form);
      setProfile(res.data); setShowProfileModal(false); window.dispatchEvent(new Event("aihire:company-updated")); showToast("Company profile saved.");
    } catch (err) { setProfileError(err.response?.data?.detail || "Failed to save profile."); } finally { setSavingProfile(false); }
  };

  const openJobModal = (job = null) => {
    setJobError(""); setEditingJob(job);
    setJobForm({ title: job?.title || "", location: job?.location || "", job_type: job?.job_type || "full-time", description: job?.description || "", required_skills: job?.required_skills || "", experience_required: job?.experience_required || "", salary: job?.salary || "" });
    setShowJobModal(true);
  };

  const handleCreateJob = async (form) => {
    setCreatingJob(true); setJobError("");
    try {
      let savedJob;
      if (editingJob) { savedJob = (await apiClient.put(`/jobs/${editingJob.id}`, form)).data; showToast("Job updated."); }
      else { savedJob = (await apiClient.post("/jobs", form)).data; showToast("Job published."); }
      setShowJobModal(false); setJobForm({ title: "", location: "", job_type: "full-time", description: "", required_skills: "", experience_required: "", salary: "" });
      await fetchJobs();
      if (selectedJob?.id === savedJob.id) fetchRankedApps(savedJob);
    } catch (err) { setJobError(err.response?.data?.detail || "Failed to save job."); } finally { setCreatingJob(false); }
  };

  const handleDeleteJob = async (jobId) => {
    if (!window.confirm("Deactivate and remove this job posting?")) return;
    try { await apiClient.delete(`/jobs/${jobId}`); if (selectedJob?.id === jobId) { setSelectedJob(null); setApplications([]); } fetchJobs(); fetchApplications(); showToast("Job deactivated."); }
    catch (err) { alert(err.response?.data?.detail || "Failed to deactivate job."); }
  };

  const openProfileModal = async (appId) => {
    try { const res = await apiClient.get(`/applications/${appId}/details`); setActiveModalApp(res.data); } catch (err) { console.error("Failed to load details:", err); showToast("Could not load applicant details.", "error"); }
  };

  const downloadResume = async (app, resumeId, fileName) => {
    if (!app?.resume_id) return;
    try { const res = await apiClient.get(`/candidate-profile/resume/${resumeId}`, { responseType: "blob" }); const url = window.URL.createObjectURL(new Blob([res.data])); const link = document.createElement("a"); link.href = url; link.download = fileName || "resume"; document.body.appendChild(link); link.click(); document.body.removeChild(link); window.URL.revokeObjectURL(url); }
    catch (err) { console.error("Failed to download:", err); showToast("Failed to download resume.", "error"); }
  };

  const handleStatusChange = async (newStatus) => {
    if (!activeModalApp) return;
    try {
      await apiClient.patch(`/applications/${activeModalApp.application_id}/status`, { status: newStatus });
      refreshAfterStatusChange();
      showToast("Status updated.");
      setActiveModalApp(null);
    } catch (err) { showToast(err.response?.data?.detail || "Failed to update status.", "error"); }
  };

  const refreshAfterStatusChange = () => { if (selectedJob) fetchRankedApps(selectedJob); else setApplications(prev => [...prev]); fetchApplications(); };

  const bulkUpdateStatus = async (newStatus) => {
    if (!selectedJob) return;
    const ids = selectedIds.size ? Array.from(selectedIds) : applications.map(a => a.id);
    setBulkUpdating(true);
    try {
      const res = await apiClient.patch(`/jobs/${selectedJob.id}/applications/bulk-status`, { application_ids: ids, status: newStatus });
      const updated = new Set(res.data.updated_ids || []);
      setApplications(prev => prev.map(a => updated.has(a.id) ? { ...a, status: newStatus } : a));
      fetchApplications();
      showToast(`${ids.length} applications updated.`);
      setSelectedIds(new Set());
    } catch (err) { showToast(err.response?.data?.detail || "Failed to update statuses.", "error"); } finally { setBulkUpdating(false); }
  };

  const applicantsPerJob = useMemo(() => {
    const map = {}; jobs.forEach(j => map[j.id] = 0);
    allApplications.forEach(a => { if (map[a.job_id] != null) map[a.job_id]++; });
    return map;
  }, [jobs, allApplications]);

  const analytics = useMemo(() => {
    const counts = { applied: 0, shortlisted: 0, interview: 0, selected: 0, rejected: 0 };
    allApplications.forEach(a => { const s = (a.status || "applied").toLowerCase(); if (counts[s] != null) counts[s]++; });
    const scored = allApplications.filter(a => a.ats_score != null);

    return {
      total: allApplications.length,
      counts,
      activeJobs: jobs.filter(j => j.is_active).length,
      avgAts: scored.reduce((s, a) => s + (Number(a.ats_score) || 0), 0) / Math.max(1, scored.length),
      // Applicants per active job posting, lowest -> highest, for the bar chart.
      applicantsPerJob: jobs
        .filter(j => j.is_active)
        .map(j => ({
          name: (j.title || "Untitled").slice(0, 18),
          applicants: applicantsPerJob[j.id] || 0,
        }))
        .sort((a, b) => a.applicants - b.applicants)
        .slice(0, 8),
    };
  }, [allApplications, jobs, applicantsPerJob]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center"><div className="mx-auto inline-flex h-8 w-8 animate-spin rounded-full border-b-2 border-t-2 border-[#7c3aed]" /><p className="mt-4 text-sm text-slate-500">Loading dashboard…</p></div>
      </div>
    );
  }

  return (
    <div className="pb-8">
      <div className="mb-6 flex flex-col justify-between gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">Recruiter Dashboard</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{jobs.length} active job{jobs.length === 1 ? "" : "s"} • {allApplications.length} total application{allApplications.length === 1 ? "" : "s"}</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button onClick={() => window.history.back()} className="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-300"><svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M10 19L3 12m0 0l7-7m-7 7h18" /></svg><span className="hidden sm:inline">Back</span></button>
          <button onClick={() => openJobModal()} className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-md shadow-indigo-600/25 transition">+ Post Job</button>
        </div>
      </div>

      {!profile && (
        <div className="mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900 dark:border-amber-900/40 dark:bg-amber-950/30">
          <div><p className="font-semibold text-sm">Company Profile Incomplete</p><p className="text-xs text-amber-700 dark:text-amber-600">Complete your company profile so candidates see who they are applying to.</p></div>
          <button onClick={() => setShowProfileModal(true)} className="text-xs font-bold uppercase tracking-wider bg-amber-200 px-3 py-1.5 rounded-md hover:bg-amber-300 transition self-start sm:self-auto">Complete Now</button>
        </div>
      )}

      {activeSection === "jobs" && (
        <>
          {jobs.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-200 p-14 text-center dark:border-slate-700"><p className="font-semibold text-slate-700 dark:text-slate-200">No jobs posted yet</p><p className="mt-1 text-xs text-slate-400 dark:text-slate-500">Create your first job opening to start receiving applications.</p><button onClick={() => openJobModal()} className="mt-4 px-4 py-2.5 bg-indigo-600 text-white rounded-xl text-xs font-semibold transition">+ Post Your First Job</button></div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">{jobs.map(job => <JobPostingCard key={job.id} job={job} applicantsCount={applicantsPerJob[job.id] || 0} onView={openJobPipeline} onEdit={openJobModal} onDelete={handleDeleteJob} />)}</div>
          )}
        </>
      )}

      {activeSection === "candidates" && (
        <PipelineTable
          jobs={jobs}
          applications={applications}
          allApplications={allApplications}
          selectedJob={selectedJob}
          onOpenJobPipeline={openJobPipeline}
          onShowAllApplications={showAllApplications}
          onOpenProfileModal={openProfileModal}
          onDownloadResume={downloadResume}
          onStatusChange={handleStatusChange}
          onDeleteJob={handleDeleteJob}
          search={search}
          onSearchChange={setSearch}
          sortMode={sortMode}
          onSortModeChange={setSortMode}
          stageFilter={stageFilter}
          onStageFilterChange={setStageFilter}
          page={page}
          onPageChange={setPage}
          pageSize={pageSize}
          onPageSizeChange={(n) => {
            setPageSize(n);
            setPage(1);
          }}
          selectedIds={selectedIds}
          onToggleRow={(id) => {
            if (id === "clear") {
              setSelectedIds(new Set());
              return;
            }
            const next = new Set(selectedIds);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            setSelectedIds(next);
          }}
          onSelectAll={() => {
            const source = selectedJob ? applications : allApplications;
            const q = search.trim().toLowerCase();
            const list = source.filter((a) => {
              if (stageFilter !== "all" && String(a.status).toLowerCase() !== stageFilter) return false;
              if (!q) return true;
              return (
                (a.candidate_name || "").toLowerCase().includes(q) ||
                (a.candidate_email || "").toLowerCase().includes(q)
              );
            });
            const sorted = [...list].sort((a, b) => {
              if (sortMode === "score") return (b.ats_score ?? 0) - (a.ats_score ?? 0);
              return new Date(b.applied_at || 0) - new Date(a.applied_at || 0);
            });
            const paged = sorted.slice((page - 1) * pageSize, page * pageSize);
            const allSelected = paged.length > 0 && paged.every((a) => selectedIds.has(a.id));
            const next = new Set(selectedIds);
            if (allSelected) {
              paged.forEach((a) => next.delete(a.id));
            } else {
              paged.forEach((a) => next.add(a.id));
            }
            setSelectedIds(next);
          }}
          onBulkStatusChange={bulkUpdateStatus}
        />
      )}

      {activeSection === "analytics" && (
        <div className="mx-auto max-w-6xl space-y-6 py-8">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900"><p className="text-2xl font-extrabold text-indigo-600">{analytics.total}</p><p className="text-xs font-medium text-slate-500">Total Applications</p></div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900"><p className="text-2xl font-extrabold text-emerald-600">{analytics.counts.shortlisted}</p><p className="text-xs font-medium text-slate-500">Shortlisted</p></div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900"><p className="text-2xl font-extrabold text-amber-500">{analytics.counts.interview}</p><p className="text-xs font-medium text-slate-500">Interview</p></div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900"><p className="text-2xl font-extrabold text-purple-600">{analytics.counts.selected}</p><p className="text-xs font-medium text-slate-500">Hired</p></div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900"><p className="text-2xl font-extrabold text-rose-600">{analytics.activeJobs}</p><p className="text-xs font-medium text-slate-500">Active Jobs</p></div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900"><p className="text-2xl font-extrabold text-indigo-600">{Math.round(analytics.avgAts)}%</p><p className="text-xs font-medium text-slate-500">Avg ATS</p></div>
          </div>
          <AnalyticsCharts
            counts={analytics.counts}
            applicantsPerJob={analytics.applicantsPerJob}
          />
        </div>
      )}

      {showJobModal && <JobFormModal job={editingJob} onSubmit={handleCreateJob} onCancel={() => setShowJobModal(false)} submitting={creatingJob} error={jobError} />}

      {showProfileModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900">
            <div className="mb-4 flex justify-between border-b border-slate-200 pb-3 dark:border-slate-700"><h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">{profile ? "Edit Company Profile" : "Company Profile"}</h3><button onClick={() => setShowProfileModal(false)} className="text-slate-400 hover:text-slate-600">✕</button></div>
            {profileError && <p className="mb-3 text-xs text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{profileError}</p>}
            <form onSubmit={(e) => { e.preventDefault(); handleProfileSubmit(profileForm); }} className="space-y-3.5">
              <div><label className="mb-1 block text-xs font-semibold text-slate-700">Company Name *</label><input required value={profileForm.company_name} onChange={(e) => setProfileForm({ ...profileForm, company_name: e.target.value })} className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900" /></div>
              <div><label className="mb-1 block text-xs font-semibold text-slate-700">Designation</label><input value={profileForm.designation} onChange={(e) => setProfileForm({ ...profileForm, designation: e.target.value })} className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900" /></div>
              <div><label className="mb-1 block text-xs font-semibold text-slate-700">Description</label><textarea rows={3} value={profileForm.company_description} onChange={(e) => setProfileForm({ ...profileForm, company_description: e.target.value })} className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900" /></div>
              <button type="submit" disabled={savingProfile} className="w-full bg-[#7c3aed] rounded-lg px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[#6d28d9] disabled:opacity-60">{savingProfile ? "Saving..." : "Save Profile"}</button>
            </form>
          </div>
        </div>
      )}

      {activeModalApp && (
        <ApplicantRowModal app={activeModalApp} onClose={() => setActiveModalApp(null)} onStatusChange={handleStatusChange} onDownloadResume={downloadResume} />
      )}

      {toast && <Toast text={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        .animate-spin { animation: spin 1s linear infinite; }
        @keyframes dropdown { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
        .animate-dropdown { animation: dropdown 0.15s ease-out; }
        @keyframes modal { from { opacity: 0; transform: scale(0.96); } to { opacity: 1; transform: scale(1); } }
        .animate-modal { animation: modal 0.15s ease-out; }
      `}</style>
    </div>
  );
}
