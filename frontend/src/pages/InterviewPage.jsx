import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../api/client";
import { cachedGet } from "../api/cachedGet";
import { InterviewSetupView, InterviewActiveView, InterviewResultView, InterviewHistoryView } from "../components/ui";
import { createResponses, advance, toSubmitPayload, answeredCount } from "../utils/interviewState";

export default function InterviewPage() {
  const navigate = useNavigate();

  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [mode, setMode] = useState("setup");
  const [questions, setQuestions] = useState([]);
  const [questionSetId, setQuestionSetId] = useState(null);
  const [responses, setResponses] = useState([]);
  const [current, setCurrent] = useState(0);
  const [draft, setDraft] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expandedHistory, setExpandedHistory] = useState(null);
  const [eligible, setEligible] = useState(null);

  // Jobs and applications are shared with the other candidate pages, so both are
  // read through the cache. History is deliberately NOT cached: it changes as soon
  // as an interview is submitted, and this page refetches it right after that.
  const fetchJobs = () => cachedGet("/jobs").then(setJobs).catch((e) => console.error("Failed to load jobs:", e));
  const fetchHistory = () => apiClient.get("/interviews/history").then((r) => setHistory(r.data)).catch((e) => console.error("Failed to load history:", e));
  // Mirrors the server-side gate: only candidates with an application in the
  // Interview stage may practice. The server still enforces it on /questions.
  const fetchEligibility = () => cachedGet("/applications/me")
    .then((apps) => setEligible((apps || []).some((a) => a.status === "interview")))
    .catch(() => setEligible(false));

  useEffect(() => { fetchJobs(); fetchHistory(); fetchEligibility(); }, []);
  const startInterview = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await apiClient.post("/interviews/questions", { job_id: selectedJobId || null });
      // The server now returns { question_set_id, questions }. question_set_id
      // must be echoed back at submit time so grading reads the stored
      // questions rather than anything the client sends.
      setQuestionSetId(res.data.question_set_id);
      const issued = res.data.questions || [];
      setQuestions(issued);
      setResponses(createResponses(issued));
      setCurrent(0);
      setDraft("");
      setMode("active");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate questions.");
    } finally {
      setLoading(false);
    }
  };

  const submitInterview = async (finalResponses) => {
    setLoading(true);
    setError("");
    try {
      const res = await apiClient.post("/interviews/evaluate", toSubmitPayload(finalResponses, questionSetId, selectedJobId));
      setResult(res.data);
      setMode("result");
      fetchHistory();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to evaluate answers.");
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    const step = advance(responses, current, draft, questions.length);
    setResponses(step.responses);

    if (step.isLast) {
      submitInterview(step.submitResponses);
      return;
    }

    setCurrent(step.nextIndex);
    setDraft(step.draft);
  };

  const resetInterview = () => {
    setMode("setup");
    setQuestions([]);
    setQuestionSetId(null);
    setResponses([]);
    setResult(null);
    setCurrent(0);
    setDraft("");
    setSelectedJobId("");
  };

  const openHistory = async (id) => {
    if (expandedHistory === id) {
      setExpandedHistory(null);
      return;
    }
    try {
      const res = await apiClient.get(`/interviews/${id}`);
      setExpandedHistory(id);
      setResult({ ...res.data, per_question: [], is_history: true });
      setMode("result");
    } catch (err) {
      console.error("Failed to load details:", err);
    }
  };


  return (
    <div className="space-y-6 max-w-4xl mx-auto py-6">
      <div className="flex items-center justify-between border-b border-slate-200 pb-4 dark:border-slate-700">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">AI Mock Interview</h1>
          <p className="text-xs text-slate-500 mt-0.5 dark:text-slate-400">Practice role-specific questions and get AI performance feedback</p>
        </div>
        <button onClick={() => navigate("/candidate")} className="text-xs font-semibold text-indigo-600 hover:underline">← Back to Dashboard</button>
      </div>

      {error && <div className="p-4 rounded-lg border text-sm font-medium bg-red-50 text-red-800 border-red-200">{error}</div>}

      {mode === "setup" && eligible === false && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-200">
          <p className="font-semibold">Mock interviews are locked</p>
          <p className="mt-1">
            Practice unlocks once a recruiter moves one of your applications to the Interview stage.
            Keep applying to get there — your interview history below is still available.
          </p>
        </div>
      )}

      {mode === "setup" && eligible && <InterviewSetupView jobs={jobs} selectedJobId={selectedJobId} onSelectJob={setSelectedJobId} onStart={startInterview} loading={loading} />}

      {mode === "active" && questions.length > 0 && (
        <InterviewActiveView
          questions={questions}
          current={current}
          draft={draft}
          onDraftChange={setDraft}
          onNext={handleNext}
          answered={answeredCount(responses)}
          loading={loading}
        />
      )}

      {mode === "result" && result && <InterviewResultView result={result} onReset={resetInterview} />}

      <InterviewHistoryView history={history} onOpen={openHistory} />
    </div>
  );
}
