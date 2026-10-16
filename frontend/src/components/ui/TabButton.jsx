export default function TabButton({ active, onClick, label, count }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold transition ${
        active ? "bg-[#7c3aed] text-white shadow-xs" : "border border-slate-300 bg-white text-slate-600 hover:bg-slate-50"
      }`}
    >
      {label}
      {count != null && count > 0 && <span className="opacity-70">{count}</span>}
    </button>
  );
}
