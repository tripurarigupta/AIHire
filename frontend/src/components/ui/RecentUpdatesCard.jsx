export default function RecentUpdatesCard({ updates = [], onViewAll }) {
  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">Recent Updates</h2>
        {onViewAll && (
          <button
            onClick={onViewAll}
            className="text-xs font-semibold text-[#7c3aed] hover:underline transition-colors"
          >
            View All
          </button>
        )}
      </div>
      <div className="mt-4 space-y-3">
        {updates.length === 0 ? (
          <p className="py-3 text-center text-xs text-slate-400 dark:text-slate-500">No recent activity yet.</p>
        ) : (
          updates.map((item) => (
            <div key={item.id} className="flex gap-3">
              <div className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${item.dotColor || "bg-slate-400"}`} />
              <div className="min-w-0">
                <p className="text-sm font-bold text-slate-900 dark:text-slate-100">{item.title}</p>
                {item.metaText && (
                  <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">{item.metaText}</p>
                )}
                {item.tags && (
                  <div className="mt-1 flex flex-wrap gap-2">
                    {item.tags.map((tag, idx) => (
                      <span key={idx} className={tag.cls}>{tag.text}</span>
                    ))}
                  </div>
                )}
                {item.timestamp && (
                  <p className="mt-0.5 text-[10px] text-slate-400 dark:text-slate-500">{item.timestamp}</p>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
