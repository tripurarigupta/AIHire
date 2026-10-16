const pillBase = "rounded-full px-3 py-1.5 text-xs font-semibold transition";

export function Pill({ active, className = "", children, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`${pillBase} ${
        active
          ? "bg-indigo-600 text-white shadow-sm shadow-indigo-600/30"
          : "bg-slate-100 text-slate-500 hover:bg-slate-200 hover:text-slate-700"
      } ${className}`}
    >
      {children}
    </button>
  );
}
