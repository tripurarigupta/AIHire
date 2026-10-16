import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const COLORS = ["#7c3aed", "#059669", "#d97706", "#db2777", "#0d9488"];

const cardClass =
  "rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900";
const titleClass =
  "text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400";
const subtitleClass = "text-xs text-slate-400 dark:text-slate-500";

function ChartCard({ title, subtitle, children }) {
  return (
    <div className={cardClass}>
      <h3 className={titleClass}>{title}</h3>
      <p className={`${subtitleClass} mb-4`}>{subtitle}</p>
      {children}
    </div>
  );
}

function EmptyState({ message }) {
  return (
    <div className="flex h-[240px] items-center justify-center rounded-xl border border-dashed border-slate-200 px-6 text-center text-xs text-slate-400 dark:border-slate-700 dark:text-slate-500">
      {message}
    </div>
  );
}

export default function AnalyticsCharts({ counts, applicantsPerJob = [] }) {
  const stageData = [
    { name: "Applied", value: counts?.applied || 0 },
    { name: "Shortlisted", value: counts?.shortlisted || 0 },
    { name: "Interview", value: counts?.interview || 0 },
    { name: "Hired", value: counts?.selected || 0 },
    { name: "Rejected", value: counts?.rejected || 0 },
  ].filter((d) => d.value > 0);

  const hasJobs = applicantsPerJob.some((j) => j.applicants > 0);

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
      {/* Applicant pipeline — donut */}
      <ChartCard
        title="Applicant Pipeline"
        subtitle="Distribution of applications by hiring stage"
      >
        {stageData.length === 0 ? (
          <EmptyState message="No applications yet — post a job to start building your pipeline." />
        ) : (
          <>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={stageData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={2}
                  stroke="none"
                >
                  {stageData.map((entry, i) => (
                    <Cell key={entry.name} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value, name) => [
                    `${value} application${value === 1 ? "" : "s"}`,
                    name,
                  ]}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-2 flex flex-wrap justify-center gap-4">
              {stageData.map((d, i) => (
                <div key={d.name} className="flex items-center gap-1.5 text-xs">
                  <span
                    className="h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: COLORS[i % COLORS.length] }}
                  />
                  <span className="text-slate-600 dark:text-slate-300">{d.name}</span>
                  <span className="font-semibold text-slate-900 dark:text-slate-100">
                    {d.value}
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
      </ChartCard>

      {/* Applicants per job — horizontal bar */}
      <ChartCard
        title="Applicants Per Job"
        subtitle="Active postings by application volume"
      >
        {!hasJobs ? (
          <EmptyState message="No applicants across your active jobs yet." />
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart
              data={applicantsPerJob}
              layout="vertical"
              margin={{ left: 8, right: 16 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
              <XAxis
                type="number"
                allowDecimals={false}
                tick={{ fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                type="category"
                dataKey="name"
                width={120}
                tick={{ fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                cursor={{ fill: "rgba(124,58,237,0.06)" }}
                formatter={(v) => [`${v} applicant${v === 1 ? "" : "s"}`, "Applicants"]}
              />
              <Bar dataKey="applicants" fill="#7c3aed" radius={[0, 4, 4, 0]} barSize={18} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </ChartCard>
    </div>
  );
}