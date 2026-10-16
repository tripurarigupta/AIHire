import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="min-h-[85vh] flex flex-col justify-center items-center px-4">
      <div className="max-w-3xl text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 text-xs font-semibold tracking-wide uppercase">
          <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
          Intelligent Recruitment Platform
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight leading-tight">
          Smarter Hiring Powered by <span className="text-indigo-600">NLP & AI Matching</span>
        </h1>

        <p className="text-slate-600 dark:text-slate-300 text-base sm:text-lg max-w-xl mx-auto">
          Match verified candidate resumes to active recruiter openings using automated skill extraction, TF-IDF ranking, and role-based workflows.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
          <Link
            to="/register"
            className="w-full sm:w-auto px-8 py-3 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm rounded-xl shadow-sm transition"
          >
            Get Started (Register)
          </Link>
          <Link
            to="/login"
            className="w-full sm:w-auto px-8 py-3 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800/70 text-slate-800 dark:text-slate-100 font-semibold text-sm rounded-xl border border-slate-300 dark:border-slate-600 shadow-sm transition"
          >
            Sign In to Account
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left pt-12 max-w-2xl mx-auto">
          <div className="p-5 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 rounded-xl shadow-xs">
            <h3 className="font-bold text-slate-900 dark:text-slate-100 text-sm mb-1">For Candidates</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Upload your PDF resume, extract your skill profile with NLP, and get matched to jobs automatically.
            </p>
          </div>
          <div className="p-5 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 rounded-xl shadow-xs">
            <h3 className="font-bold text-slate-900 dark:text-slate-100 text-sm mb-1">For Recruiters</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Post jobs and view applicants pre-ranked by ATS similarity scores with candidate inspect modals.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
