import { initialsFor } from "./Initials";

export default function UsersTable({ users }) {
  if (!users?.length) {
    return <p className="py-8 text-center text-sm text-slate-400">No users found.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[480px] text-left text-sm">
        <thead>
          <tr className="border-b border-slate-100 text-xs font-bold uppercase tracking-wider text-slate-500 dark:border-slate-800">
            <th className="py-3 pr-4">User</th>
            <th className="py-3 pr-4">Role</th>
            <th className="py-3">Joined</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
          {users.map((u) => (
            <tr key={u.id} className="text-slate-700 dark:text-slate-300">
              <td className="py-3 pr-4">
                <div className="flex items-center gap-2.5">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-slate-600 to-slate-800 text-xs font-bold text-white">
                    {initialsFor(u.full_name)}
                  </span>
                  <span className="font-semibold">{u.full_name || "Unknown"}</span>
                </div>
              </td>
              <td className="py-3 pr-4">
                <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase ${
                  u.role === "admin" ? "bg-purple-100 text-purple-700" :
                  u.role === "recruiter" ? "bg-indigo-100 text-indigo-700" :
                  "bg-emerald-100 text-emerald-700"
                }`}>
                  {u.role}
                </span>
              </td>
              <td className="py-3 text-slate-500">{u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
