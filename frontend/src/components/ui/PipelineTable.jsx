import { useMemo, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { MiniButton } from "./MiniButton";
import { Pill } from "./Pill";
import ApplicantRow from "./ApplicantRow";

const STAGE_STYLES = {
  applied: { label: "Applied", cls: "bg-indigo-50 text-indigo-600" },
  shortlisted: { label: "Shortlisted", cls: "bg-emerald-50 text-emerald-700" },
  interview: { label: "Interview", cls: "bg-amber-50 text-amber-700" },
  selected: { label: "Hired", cls: "bg-purple-50 text-purple-700" },
};

const stageFor = (status) => {
  const key = typeof status === "string" ? status.toLowerCase() : "";
  return STAGE_STYLES[key] || { label: String(status ?? "—"), cls: "bg-slate-100 text-slate-500" };
};

export default function PipelineTable({
  jobs,
  applications,
  allApplications,
  selectedJob,
  onOpenJobPipeline,
  onShowAllApplications,
  onOpenProfileModal,
  onDownloadResume,
  onStatusChange,
  onDeleteJob,
  search = "",
  sortMode = "score",
  stageFilter = "all",
  page = 1,
  pageSize = 20,
  selectedIds = new Set(),
  onPageChange,
  onPageSizeChange,
  onSearchChange,
  onSortModeChange,
  onStageFilterChange,
  onToggleRow,
  onSelectAll,
  onBulkStatusChange,
  fetchingRankedApps = false,
}) {
  const [searchParams, setSearchParams] = useSearchParams();

  const setActiveSection = useCallback(
    (key) => {
      setSearchParams(key === "candidates" ? {} : { section: key }, { replace: true });
    },
    [setSearchParams]
  );

  const pipelineSource = selectedJob ? applications : allApplications;

  const filteredSortedApps = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = pipelineSource.filter((a) => {
      if (stageFilter !== "all" && String(a.status).toLowerCase() !== stageFilter) return false;
      if (!q) return true;
      return (
        (a.candidate_name || "").toLowerCase().includes(q) ||
        (a.candidate_email || "").toLowerCase().includes(q)
      );
    });
    return [...list].sort((a, b) => {
      if (sortMode === "score") {
        return (b.ats_score ?? 0) - (a.ats_score ?? 0);
      }
      return new Date(b.applied_at || 0) - new Date(a.applied_at || 0);
    });
  }, [pipelineSource, search, sortMode, stageFilter]);

  const totalPages = Math.max(1, Math.ceil(filteredSortedApps.length / pageSize));
  const safePage = Math.min(page, totalPages);
  const pagedApps = filteredSortedApps.slice((safePage - 1) * pageSize, safePage * pageSize);

  const stageTabs = [
    { key: "all", label: "All" },
    { key: "applied", label: "Applied" },
    { key: "shortlisted", label: "Shortlisted" },
    { key: "interview", label: "Interview" },
    { key: "selected", label: "Hired" },
  ];

  const stageCount = (key) =>
    key === "all" ? pipelineSource.length : pipelineSource.filter((a) => String(a.status).toLowerCase() === key).length;

  const allOnPageSelected = pagedApps.length > 0 && pagedApps.every((a) => selectedIds.has(a.id));

  const toggleRow = (id) => {
    if (onToggleRow) onToggleRow(id);
  };

  const toggleSelectAllOnPage = () => {
    if (onSelectAll) onSelectAll();
  };

  const changeStageFilter = (key) => {
    if (onStageFilterChange) onStageFilterChange(key);
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-4 gap-5 items-start">
      <div className="xl:col-span-3 bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 p-5 sm:p-6 shadow-sm">
        <div className="mb-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h1 className="text-lg font-bold text-slate-900 dark:text-slate-100">
              {selectedJob ? `Applicants for ${selectedJob.title}` : "All Applications"}
            </h1>
            <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
              <svg className="w-3.5 h-3.5 text-emerald-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm3.857-9.809a.75.75 0 0 0-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 1 0-1.06 1.061l2.5 2.5a.75.75 0 0 0 1.137-.089l4-5.5Z" clipRule="evenodd" />
              </svg>
              {selectedJob
                ? `${filteredSortedApps.length} applicant${filteredSortedApps.length === 1 ? "" : "s"} • ranked by ATS`
                : `${filteredSortedApps.length} application${filteredSortedApps.length === 1 ? "" : "s"} across all your jobs`}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative flex-1 md:w-56">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 10.5a6.5 6.5 0 1 1-13 0 6.5 6.5 0 0 1 13 0Z" />
              </svg>
              <input
                type="text"
                value={search}
                onChange={(e) => {
                  if (onSearchChange) onSearchChange(e.target.value);
                  setActiveSection("candidates");
                }}
                placeholder="Search candidates…"
                className="w-full text-xs pl-9 pr-3 py-2.5 rounded-full border border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-950 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder:text-slate-400"
              />
            </div>
            <MiniButton onClick={() => sortMode === "date" ? onSortModeChange?.("score") : onSortModeChange?.("date")}>
              {sortMode === "date" ? "Sort by date" : "Sort by score"}
            </MiniButton>
          </div>
        </div>

        <div className="mb-3 border-b border-slate-100 dark:border-slate-800 overflow-x-auto">
          <div className="flex items-center gap-2 pb-3">
            <MiniButton active={!selectedJob} onClick={onShowAllApplications}>All jobs</MiniButton>
            {jobs.map((job) => (
              <MiniButton
                key={job.id}
                active={selectedJob?.id === job.id}
                onClick={() => onOpenJobPipeline(job)}
              >
                {job.title}
              </MiniButton>
            ))}
          </div>
        </div>

        <div className="mb-4 flex flex-wrap items-center gap-1.5 pb-4 border-b border-slate-100 dark:border-slate-800">
          {stageTabs.map((tab) => (
            <Pill key={tab.key} active={stageFilter === tab.key} onClick={() => changeStageFilter(tab.key)}>
              {tab.label}
              <span className={`ml-1.5 ${stageFilter === tab.key ? "text-indigo-100" : "text-slate-400"}`}>
                {stageCount(tab.key)}
              </span>
            </Pill>
          ))}
        </div>

        {selectedIds.size > 0 && (
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-indigo-200 bg-indigo-50 px-4 py-3">
            <span className="text-xs font-semibold text-indigo-900">
              {selectedIds.size} candidate{selectedIds.size === 1 ? "" : "s"} selected
            </span>
            <div className="flex flex-wrap items-center gap-2">
              <button onClick={() => onBulkStatusChange?.("shortlisted")} className="rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-emerald-700">
                Shortlist
              </button>
              <button onClick={() => onBulkStatusChange?.("interview")} className="rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-indigo-700">
                Interview
              </button>
              <button onClick={() => onBulkStatusChange?.("selected")} className="rounded-md bg-purple-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-purple-700">
                Hire
              </button>

              <button onClick={() => { if (onToggleRow) onToggleRow("clear"); }} className="text-xs font-semibold text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200">
                Clear
              </button>
            </div>
          </div>
        )}

        {!pipelineSource.length ? (
          <p className="py-14 text-center text-sm text-slate-400 dark:text-slate-500">
            {selectedJob ? "No candidates have applied for this position yet." : "No applications across your jobs yet."}
          </p>
        ) : pagedApps.length === 0 ? (
          <p className="py-14 text-center text-sm text-slate-400 dark:text-slate-500">No applicants match your filters.</p>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[720px] text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-slate-800">
                    <th className="w-10 py-3 pr-3">
                      <input
                        type="checkbox"
                        checked={allOnPageSelected}
                        onChange={toggleSelectAllOnPage}
                        title="Select all rows on this page"
                        className="cursor-pointer h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                      />
                    </th>
                    <th className="py-3 pr-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Candidate</th>
                    <th className="py-3 pr-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Role</th>
                    <th className="py-3 pr-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Stage</th>
                    <th className="py-3 pr-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">AI Score</th>
                    <th className="py-3 pr-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Applied On</th>
                    <th className="py-3 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Location</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50 dark:divide-slate-800/70">
                  {pagedApps.map((app) => (
                    <ApplicantRow
                      key={app.id}
                      app={app}
                      selected={selectedIds.has(app.id)}
                      onToggleSelect={() => toggleRow(app.id)}
                      onView={() => onOpenProfileModal(app.id)}
                      onDownloadResume={(resumeId, fileName) => onDownloadResume?.(app, resumeId, fileName)}
                    />
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-5 border-t border-slate-100 pt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 dark:border-slate-800">
              <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                <span>Showing</span>
                <select
                  value={pageSize}
                  onChange={(e) => onPageSizeChange?.(Number(e.target.value))}
                  className="rounded-md bg-indigo-50 px-2 py-1 font-bold text-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  {[10, 20, 50].map((n) => <option key={n} value={n}>{n}</option>)}
                </select>
                <span>Rows | {(safePage - 1) * pageSize + 1}-{(Math.min(safePage * pageSize, filteredSortedApps.length)) || 0} of {filteredSortedApps.length}</span>
              </div>

              <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                <span>Page</span>
                <button
                  onClick={() => onPageChange?.(safePage - 1)}
                  disabled={safePage <= 1}
                  className="rounded-lg border border-slate-200 p-1.5 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-slate-700 dark:hover:bg-slate-800/70"
                >
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" /></svg>
                </button>
                <span className="px-3 py-1 rounded-lg border">{safePage}</span>
                <button
                  onClick={() => onPageChange?.(safePage + 1)}
                  disabled={safePage >= totalPages}
                  className="rounded-lg border border-slate-200 p-1.5 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-slate-700 dark:hover:bg-slate-800/70"
                >
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" /></svg>
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
