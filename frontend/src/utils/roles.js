const ROLE_DASHBOARD_PATHS = {
  candidate: "/candidate",
  recruiter: "/recruiter",
  admin: "/admin",
};

export const dashboardPathForRole = (role) => {
  const key = typeof role === "string" ? role.toLowerCase() : "";
  return ROLE_DASHBOARD_PATHS[key] || "/candidate";
};
