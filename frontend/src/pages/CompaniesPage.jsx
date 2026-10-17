import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import apiClient from "../api/client";
import { cachedGet } from "../api/cachedGet";
import { invalidate } from "../utils/apiCache";
import { JobCard, Toast } from "../components/ui";

export default function CompaniesPage() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  // Applying is candidate-only on the API, so the action is only offered to them.
  const canApply = user?.role?.toLowerCase() === "candidate";

  // Every hook must run before any conditional return (Rules of Hooks).
  const [mounted, setMounted] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [search, setSearch] = useState("");
  const [locationFilter, setLocationFilter] = useState("all");
  const [applyingJobId, setApplyingJobId] = useState(null);
  const [appliedJobIds, setAppliedJobIds] = useState(() => new Set());
  const [toast, setToast] = useState(null);

  const showToast = (text, type = "success") => { setToast({ text, type }); setTimeout(() => setToast(null), 3500); };

  useEffect(() => {
    setMounted(true);
    // Both resources are shared with the dashboard and the applications page, so
    // the cache makes most visits to this page hit zero endpoints.
    Promise.all([cachedGet("/jobs"), cachedGet("/applications/me")])
      .then(([jobsData, appsData]) => {
        setJobs(jobsData);
        const ids = new Set((appsData || []).filter((a) => (a.status || "").toLowerCase() !== "rejected").map((a) => String(a.job_id)));
        setAppliedJobIds(ids);
      })
      .catch(() => setJobs([]));
  }, []);

  const handleApply = async (job) => {
    const strJobId = String(job.id);
    setApplyingJobId(strJobId);
    try {
      await apiClient.post(`/jobs/${strJobId}/applications`, { cover_letter: "Applied via AIHire Companies Page" });
      // The applications list changed, so drop the cached copy other pages read.
      invalidate("/applications/me");
      setAppliedJobIds((prev) => new Set(prev).add(strJobId));
      showToast(`Application submitted for ${job.title}.`);
    } catch (err) {
      const detail = err.response?.data?.detail || "Failed to apply.";
      showToast(detail, "error");
      if (typeof detail === "string" && detail.toLowerCase().includes("already applied")) {
        setAppliedJobIds((prev) => new Set(prev).add(strJobId));
      }
    } finally {
      setApplyingJobId(null);
    }
  };

  // Collapse case-variant spellings of the same place ("Pune" / "pune") into
  // one chip, showing the properly capitalized spelling we saw first.
  const locations = [
    ...jobs.reduce((map, job) => {
      const raw = (job.location || "").trim();
      if (!raw) return map;
      const key = raw.toLowerCase();
      const current = map.get(key);
      if (!current || (/^[A-Z]/.test(raw) && !/^[A-Z]/.test(current))) map.set(key, raw);
      return map;
    }, new Map()).values(),
  ].sort((a, b) => a.localeCompare(b));
  const filteredJobs = jobs.filter((j) => {
    // Location chip and search box filter independently.
    if (locationFilter !== "all" && (j.location || "").trim().toLowerCase() !== locationFilter.toLowerCase()) return false;
    const term = search.trim().toLowerCase();
    if (!term) return true;
    const hay = `${j.title} ${j.company_name || ""} ${j.location || ""} ${j.salary || ""} ${j.job_type || ""}`.toLowerCase();
    return hay.includes(term);
  });

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">Companies</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Sign in to explore companies hiring on AIHire.</p>
          <button onClick={() => navigate("/login")} className="mt-4 rounded-lg bg-[#7c3aed] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#6d28d9]">Go to login</button>
        </div>
      </div>
    );
  }

  if (!mounted) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center"><div className="inline-flex h-8 w-8 animate-spin rounded-full border-b-2 border-t-2 border-[#7c3aed]" /><p className="mt-4 text-sm text-slate-500">Loading companies…</p></div>
      </div>
    );
  }

  return (
    <div className="py-6">
      <div className="mb-6 flex flex-col justify-between gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-end">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">Companies Hiring</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {filteredJobs.length > 0 ? `${filteredJobs.length} open role${filteredJobs.length === 1 ? "" : "s"} from ${new Set(filteredJobs.map((j) => j.company_name || "Unknown")).size} compan${new Set(filteredJobs.map((j) => j.company_name || "Unknown")).size === 1 ? "y" : "ies"}.` : "No open roles match your filters."}
          </p>
        </div>
        <div className="relative">
          <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" /></svg>
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search roles, companies…" className="w-64 rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-[#7c3aed]/20 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-200" />
        </div>
      </div>

      {locations.length > 0 && (
        <div className="mb-6 flex flex-wrap gap-2">
          <button onClick={() => setLocationFilter("all")} className={`rounded-full px-4 py-1.5 text-xs font-semibold transition ${locationFilter === "all" ? "bg-[#7c3aed] text-white shadow-xs" : "border border-slate-300 bg-white text-slate-600 hover:bg-slate-50"}`}>All Locations</button>
          {locations.map((loc) => <button key={loc} onClick={() => setLocationFilter(loc)} className={`rounded-full px-4 py-1.5 text-xs font-semibold transition ${locationFilter === loc ? "bg-[#7c3aed] text-white shadow-xs" : "border border-slate-300 bg-white text-slate-600 hover:bg-slate-50"}`}>{loc}</button>)}
        </div>
      )}

      {filteredJobs.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center dark:border-slate-600 dark:bg-slate-900">
          <p className="text-sm font-semibold text-slate-700 dark:text-slate-200">{jobs.length === 0 ? "No open roles yet." : "No roles match your filters."}</p>
          <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">{jobs.length === 0 ? "Companies appear here once recruiters post jobs." : "Try clearing the search or location filter."}</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">{filteredJobs.map((job) => <JobCard key={job.id} job={job} alreadyApplied={appliedJobIds.has(String(job.id))} applying={applyingJobId === String(job.id)} onApply={canApply ? () => handleApply(job) : undefined} />)}</div>
      )}

      {toast && <Toast text={toast.text} type={toast.type} onClose={() => setToast(null)} />}
    </div>
  );
}
