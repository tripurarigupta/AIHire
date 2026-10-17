import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { dashboardPathForRole, routeGuardFor } from "./utils/roles";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import RecruiterDashboard from "./pages/RecruiterDashboard";
import CandidateDashboard from "./pages/CandidateDashboard";
import ApplicationsPage from "./pages/ApplicationsPage";
import CompaniesPage from "./pages/CompaniesPage";
import InterviewPage from "./pages/InterviewPage";
import AdminPage from "./pages/AdminPage";
import { useEffect } from "react";

// Shown when a signed-in user lands on a page their role cannot use and their
// own dashboard is that very page - an unrecognised role resolves to /candidate,
// so redirecting there would bounce forever.
function RoleMismatchNotice() {
  const { logout } = useAuth();

  return (
    <div className="mx-auto mt-16 max-w-lg rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">Not available for your account</h2>
      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
        This page belongs to a different account type. Sign in again to continue.
      </p>
      <button
        onClick={() => {
          logout();
          window.location.assign("/login");
        }}
        className="mt-5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700"
      >
        Back to sign in
      </button>
    </div>
  );
}

// Route guard component.
//
// `allowedRoles` restricts a route to specific account types. The API enforces
// the same rule with require_role(), so without it a signed-in candidate opening
// /recruiter would not be blocked - they would just see a dashboard whose every
// request comes back 403, looking like the app is broken.
function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const decision = routeGuardFor(user?.role, allowedRoles, location.pathname);

  if (decision.action === "notice") {
    return <RoleMismatchNotice />;
  }

  if (decision.action === "redirect") {
    return <Navigate to={decision.to} replace />;
  }

  return children;
}

// Keeps signed-in users out of the auth screens: an already-logged-in user who
// lands on /login or /register is sent straight to their role's dashboard.
function PublicOnlyRoute({ children }) {
  const { isAuthenticated, user } = useAuth();
  if (isAuthenticated) {
    return <Navigate to={dashboardPathForRole(user?.role)} replace />;
  }
  return children;
}

// Sends signed-in users to their dashboard, anonymous users to the login page.
function CatchAllRedirect() {
  const { isAuthenticated, user } = useAuth();
  return (
    <Navigate
      to={isAuthenticated ? dashboardPathForRole(user?.role) : "/login"}
      replace
    />
  );
}

function App() {
  useEffect(() => {
    const handler = (err) => {
      // Surface silent render/runtime crashes as a visible console error + alert
      // so a blank page is easier to debug.
      console.error("[App] Unhandled error:", err);
    };
    window.addEventListener("unhandledrejection", handler);
    return () => window.removeEventListener("unhandledrejection", handler);
  }, []);

  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300">
            <Navbar />
            <main className="container mx-auto px-4">
              <Routes>
              <Route
                path="/"
                element={
                  <PublicOnlyRoute>
                    <Home />
                  </PublicOnlyRoute>
                }
              />
              <Route
                path="/register"
                element={
                  <PublicOnlyRoute>
                    <Register />
                  </PublicOnlyRoute>
                }
              />
              <Route
                path="/login"
                element={
                  <PublicOnlyRoute>
                    <Login />
                  </PublicOnlyRoute>
                }
              />
              <Route
                path="/candidate"
                element={
                  <ProtectedRoute allowedRoles={["candidate"]}>
                    <CandidateDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/recruiter"
                element={
                  <ProtectedRoute allowedRoles={["recruiter"]}>
                    <RecruiterDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/applications"
                element={
                  <ProtectedRoute allowedRoles={["candidate"]}>
                    <ApplicationsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/companies"
                element={
                  <ProtectedRoute>
                    <CompaniesPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/interview"
                element={
                  <ProtectedRoute allowedRoles={["candidate"]}>
                    <InterviewPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin"
                element={
                  <ProtectedRoute allowedRoles={["admin"]}>
                    <AdminPage />
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<CatchAllRedirect />} />
            </Routes>
          </main>
        </div>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;