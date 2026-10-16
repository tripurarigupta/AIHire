import JobPostingCard from "./JobPostingCard";

export default function JobsList({ jobs, onEdit, onDelete }) {
  if (!jobs?.length) {
    return <p className="py-8 text-center text-sm text-slate-400">No jobs to display.</p>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {jobs.map((job) => (
        <JobPostingCard
          key={job.id}
          job={job}
          applicantsCount={job.applicants_count || 0}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
