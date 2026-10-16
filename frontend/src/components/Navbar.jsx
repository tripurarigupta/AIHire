import { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { dashboardPathForRole } from "../utils/roles";
import apiClient from "../api/client";

export default function Navbar() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const [open, setOpen] = useState(false);
  const [companyMenuOpen, setCompanyMenuOpen] = useState(false);
  const companyMenuRef = useRef(null);
  const companyPanelRef = useRef(null);
  const [notifs, setNotifs] = useState([]);
  const [unread, setUnread] = useState(0);
  const dropdownRef = useRef(null);

  const fetchUnread = async () => {
    try {
      const res = await apiClient.get("/notifications/unread-count");
      setUnread(res.data.count || 0);
    } catch {
      /* ignore */
    }
  };

  const fetchNotifs = async () => {
    try {
      const res = await apiClient.get("/notifications");
      setNotifs(res.data);
    } catch {
      /* ignore */
    }
  };

  useEffect(() => {
    if (!user) return;
    // Admins have no notification feed, so there is nothing to poll.
    if (user.role?.toLowerCase() === "admin") return;
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, [user]);

  useEffect(() => {
    if (open) {
      fetchNotifs();
      fetchUnread();
    }
  }, [open]);

  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
      // Close the company panel unless the click is on the toggle chip or inside the panel
      if (
        companyMenuRef.current &&
        companyPanelRef.current &&
        !companyMenuRef.current.contains(e.target) &&
        !companyPanelRef.current.contains(e.target)
      ) {
        setCompanyMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const markRead = async (id) => {
    try {
      await apiClient.post(`/notifications/${id}/read`);
      setNotifs((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
      setUnread((u) => Math.max(0, u - 1));
    } catch {
      /* ignore */
    }
  };

  const markAllRead = async () => {
    try {
      await apiClient.post("/notifications/read-all");
      setNotifs((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnread(0);
    } catch {
      /* ignore */
    }
  };

  const handleNotificationClick = (n) => {
    if (!n.is_read) markRead(n.id);
    setOpen(false);
    if (n.link) navigate(n.link);
  };

  const formatTime = (value) => {
    if (!value) return "";
    const d = new Date(value);
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric" }) +
      " · " +
      d.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
  };

  // Company profile for the recruiter logo chip (fetched once, refreshed on save).
  // Kept above the early return so hook order is stable across login/logout.
  const [company, setCompany] = useState(null);
  const recruiterRole = user?.role?.toLowerCase() === "recruiter";
  useEffect(() => {
    if (!recruiterRole) return;
    let cancelled = false;
    apiClient
      .get("/recruiter-profile/me")
      .then((res) => {
        if (!cancelled) setCompany(res.data);
      })
      .catch(() => {
        if (!cancelled) setCompany(null);
      });
    const refresh = () => {
      apiClient
        .get("/recruiter-profile/me")
        .then((res) => setCompany(res.data))
        .catch(() => setCompany(null));
    };
    window.addEventListener("aihire:company-updated", refresh);
    return () => {
      cancelled = true;
      window.removeEventListener("aihire:company-updated", refresh);
    };
  }, [recruiterRole]);

  if (!user) {
    return null;
  }  const rawName = user?.full_name || user?.email?.split("@")[0] || "User";
  const displayName = rawName
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join("");
  // First + last name initials for the avatar (e.g. "Deepak Patel" -> "DP")
  const nameParts = rawName.trim().split(/\s+/).filter(Boolean);
  const userInitials = (
    nameParts.length >= 2
      ? nameParts[0].charAt(0) + nameParts[nameParts.length - 1].charAt(0)
      : nameParts[0]?.charAt(0) || "U"
  ).toUpperCase();
  const initialsFor = (name) =>
    (name || "C")
      .split(" ")
      .map((w) => w.charAt(0))
      .slice(0, 2)
      .join("")
      .toUpperCase() || "C";
  const role = user?.role?.toLowerCase() || "candidate";
  const isCandidate = role === "candidate";
  const dashboardPath = dashboardPathForRole(role);

  // Role-aware navigation items. Recruiters get their dashboard sections
  // directly in this navbar (driven by the ?section= query param).
  const recruiterSection = new URLSearchParams(location.search).get("section");
  const navItems = isCandidate
    ? [
        { label: "Dashboard", to: dashboardPath },
        { label: "Applications", to: "/applications" },
        { label: "Companies", to: "/companies" },
      ]
    : role === "recruiter"
      ? [
          { label: "Jobs", to: "/recruiter?section=jobs", section: "jobs" },
          { label: "Candidates", to: "/recruiter?section=candidates", section: "candidates" },
          { label: "Analytics", to: "/recruiter?section=analytics", section: "analytics" },
        ]
      : [];

  const isActive = (item) => {
    if (item.section) {
      return (
        location.pathname === "/recruiter" &&
        (recruiterSection || "candidates") === item.section
      );
    }
    return location.pathname.startsWith(item.to);
  };

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-slate-900 text-white shadow-lg shadow-slate-900/10">
      {/* Recruiter menu — anchored to the navbar itself, right-aligned, opening just
          below the navbar edge (top-right, under the Sign Out area). */}
      {role === "recruiter" && companyMenuOpen && (
        <div
          className="absolute right-4 top-full mt-1 w-64 overflow-hidden rounded-xl bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 shadow-2xl shadow-slate-900/25 border border-slate-200 dark:border-slate-700 animate-dropdown"
          ref={companyPanelRef}
        >
          {/* Company identity */}
          <div className="px-4 py-3 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2.5">
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-xs font-bold text-white">
                {initialsFor(company?.company_name)}
              </span>
              <div className="min-w-0">
                <p className="text-xs font-bold text-slate-900 dark:text-slate-100 truncate">
                  {company?.company_name || "No company yet"}
                </p>
                <p className="text-[10px] text-slate-400 truncate">
                  {company?.designation || "Company profile"}
                </p>
              </div>
            </div>
          </div>
          <button
            onClick={() => {
              setCompanyMenuOpen(false);
              window.dispatchEvent(new Event("aihire:manage-company"));
            }}
            className="w-full text-left px-4 py-2.5 text-xs font-semibold text-slate-700 hover:bg-indigo-50/60 transition-colors"
          >
            Manage your company
          </button>
        </div>
      )}

      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo + nav links */}
        <div className="flex items-center gap-8">
          <button
            onClick={() => navigate(dashboardPath)}
            className="flex items-center gap-2.5 transition-transform duration-200 hover:scale-[1.03]"
          >
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 shadow-md shadow-indigo-900/40">
              <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </span>
            <span className="text-xl font-bold tracking-tight">AIHire</span>
          </button>

          {navItems.length > 0 && (
            <nav className="hidden items-center gap-1 md:flex">
              {navItems.map((item) => (
                <button
                  key={item.label}
                  onClick={() => navigate(item.to)}
                  className={`relative rounded-lg px-3.5 py-2 text-sm font-medium transition-all duration-200 ${
                    isActive(item)
                      ? "text-white"
                      : "text-slate-300 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  {item.label}
                  {isActive(item) && (
                    <span className="absolute inset-x-3 -bottom-[9px] h-0.5 rounded-full bg-gradient-to-r from-indigo-400 to-violet-400" />
                  )}
                </button>
              ))}
            </nav>
          )}
        </div>

        {/* Right side: role badge, notifications, profile, sign out */}
        <div className="flex items-center gap-3">
          <span className="hidden rounded-full border border-purple-400/40 bg-purple-500/15 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-purple-300 sm:inline-block">
            {user.role}
          </span>

          {/* Notifications — admins have no notification feed, so the bell is hidden */}
          {role !== "admin" && (
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setOpen((o) => !o)}
              className="relative p-2 rounded-lg text-slate-300 hover:bg-white/5 hover:text-white transition-all duration-200"
              title="Notifications"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
              </svg>
              {unread > 0 && (
                <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 flex items-center justify-center rounded-full bg-gradient-to-br from-red-500 to-rose-600 text-white text-[10px] font-bold shadow-md shadow-indigo-950/40 ring-2 ring-slate-900">
                  {unread > 99 ? "99+" : unread}
                </span>
              )}
            </button>

            {open && (
              <div className="absolute right-0 mt-2 w-80 origin-top-right overflow-hidden rounded-xl bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 shadow-2xl shadow-slate-900/25 border border-slate-200 dark:border-slate-700 animate-dropdown">
                <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
                    Notifications
                  </span>
                  {unread > 0 && (
                    <button
                      onClick={markAllRead}
                      className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 hover:underline transition-colors"
                    >
                      Mark all read
                    </button>
                  )}
                </div>
                <div className="max-h-80 overflow-y-auto divide-y divide-slate-100">
                  {notifs.length === 0 ? (
                    <p className="text-xs text-slate-400 dark:text-slate-500 text-center py-8">
                      No notifications yet.
                    </p>
                  ) : (
                    notifs.map((n) => (
                      <button
                        key={n.id}
                        onClick={() => handleNotificationClick(n)}
                        className={`w-full text-left px-4 py-3 hover:bg-indigo-50/60 transition-colors duration-150 ${
                          n.is_read ? "opacity-60" : ""
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                            {n.title}
                          </span>
                          {!n.is_read && (
                            <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600" />
                          )}
                        </div>
                        {n.message && (
                          <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">{n.message}</p>
                        )}
                        <p className="mt-1 text-[10px] text-slate-400">
                          {formatTime(n.created_at)}
                        </p>
                      </button>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
          )}

          {/* Right cluster: theme toggle + identity chip + sign out (recruiter menu
              is anchored to the navbar, top-right below the bar) */}
          <div className="flex items-center gap-3">
            {/* Dark / light mode toggle */}
            <button
              onClick={toggleTheme}
              title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
              className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-white/10 transition-all duration-200"
            >
              {theme === "dark" ? (
                // Sun icon (currently dark → offer light)
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z" />
                </svg>
              ) : (
                // Moon icon (currently light → offer dark)
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z" />
                </svg>
              )}
            </button>
            {role === "recruiter" ? (
              <button
                ref={companyMenuRef}
                onClick={() => setCompanyMenuOpen((o) => !o)}
                className="hidden sm:flex items-center gap-2.5 rounded-full border border-white/10 bg-white/5 py-1 pl-1 pr-3 hover:bg-white/10 transition-all duration-200"
                title="Account & company"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-[11px] font-bold shadow-sm">
                  {userInitials}
                </span>
                <span className="flex flex-col leading-tight text-left">
                  <span className="text-xs font-semibold text-white max-w-[140px] truncate">
                    {displayName}
                  </span>
                  <span className="text-[10px] text-slate-400">Manage company</span>
                </span>
              </button>
            ) : (
              <div className="hidden items-center gap-2.5 rounded-full border border-white/10 bg-white/5 py-1 pl-1 pr-3 sm:flex">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-xs font-bold shadow-sm">
                  {userInitials}
                </div>
                <span className="text-xs font-semibold text-white">{displayName}</span>
              </div>
            )}

            <button
              onClick={() => {
                logout();
                navigate("/login", { replace: true });
              }}
              className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 transition-all duration-200 hover:border-slate-600 hover:bg-white/5 hover:text-white"
            >
              Sign Out
            </button>

          </div>
        </div>
      </div>

      {/* Mobile nav row: role links + recruiter section switcher */}
      <nav className="md:hidden flex items-center gap-1.5 overflow-x-auto border-t border-white/10 px-4 py-2">
        {navItems.map((item) => (
          <button
            key={item.label}
            onClick={() => navigate(item.to)}
            className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition ${
              isActive(item)
                ? "bg-gradient-to-r from-indigo-500 to-violet-600 text-white"
                : "bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white"
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>
    </header>
  );
}
