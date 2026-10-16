export function MiniButton({
  onClick,
  children,
  active = false,
  className = "",
}) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded-full text-xs font-semibold transition border ${
        active
          ? "bg-indigo-600 border-indigo-600 text-white"
          : "bg-white border-slate-200 text-slate-600 hover:border-slate-300 hover:text-slate-900"
      } ${className}`}
    >
      {children}
    </button>
  );
}
