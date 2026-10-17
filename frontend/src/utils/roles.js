const ROLE_DASHBOARD_PATHS = {
  candidate: "/candidate",
  recruiter: "/recruiter",
  admin: "/admin",
};

export const normalizeRole = (role) =>
  typeof role === "string" ? role.toLowerCase() : "";

export const dashboardPathForRole = (role) => {
  const key = normalizeRole(role);
  return ROLE_DASHBOARD_PATHS[key] || "/candidate";
};

/**
 * What the route guard should do for a signed-in user sitting on `pathname`.
 *
 * Returns one of:
 *   { action: "render" }              the role may use this page
 *   { action: "redirect", to }        send them to their own dashboard
 *   { action: "notice" }              there is no dashboard to send them to
 *
 * "notice" covers the one case where redirecting would loop: an unrecognised
 * role resolves to /candidate, so if /candidate is also the guarded page there
 * is nowhere to go and the user needs to sign in again instead.
 */
export const routeGuardFor = (role, allowedRoles, pathname) => {
  if (!allowedRoles || allowedRoles.length === 0) {
    return { action: "render" };
  }

  const normalized = normalizeRole(role);
  if (allowedRoles.includes(normalized)) {
    return { action: "render" };
  }

  const ownDashboard = dashboardPathForRole(normalized);
  if (ownDashboard === pathname) {
    return { action: "notice" };
  }

  return { action: "redirect", to: ownDashboard };
};
