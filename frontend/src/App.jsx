import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { dashboardPathForRole } from "./utils/roles";
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

// Route guard component
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
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
              <Route path="/" element={<Home />} />
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
                  <ProtectedRoute>
                    <CandidateDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/recruiter"
                element={
                  <ProtectedRoute>
                    <RecruiterDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/applications"
                element={
                  <ProtectedRoute>
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
                  <ProtectedRoute>
                    <InterviewPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin"
                element={
                  <ProtectedRoute>
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