/**
 * Unit tests for the role-based route guard.
 *
 * Guards the regression where every protected route only checked *that* you were
 * signed in, not *which account type* you are. A candidate opening /recruiter
 * therefore landed on the recruiter dashboard and watched every request come back
 * 403, while a recruiter opening /candidate saw an empty candidate dashboard.
 *
 * Also checks the wiring in App.jsx, so a route cannot quietly lose its roles.
 *
 * Run: node scripts/verify-role-routing.mjs
 */
import { readFileSync } from "node:fs";
import { dashboardPathForRole, routeGuardFor } from "../src/utils/roles.js";

let failures = 0;
const check = (name, cond, detail = "") => {
  if (cond) console.log(`  PASS  ${name}`);
  else { console.log(`  FAIL  ${name} ${detail}`); failures++; }
};

// The route table from App.jsx, restated so a mismatch is caught in either place.
const ROUTES = [
  { path: "/candidate", allowedRoles: ["candidate"] },
  { path: "/applications", allowedRoles: ["candidate"] },
  { path: "/interview", allowedRoles: ["candidate"] },
  { path: "/recruiter", allowedRoles: ["recruiter"] },
  { path: "/companies", allowedRoles: null }, // any signed-in role
  { path: "/admin", allowedRoles: ["admin"] },
];

const ROLES = ["candidate", "recruiter", "admin", "", "unexpected-role"];

console.log("\n=== 1. Each role reaches its own dashboard ===");
check("candidate on /candidate renders", routeGuardFor("candidate", ["candidate"], "/candidate").action === "render");
check("recruiter on /recruiter renders", routeGuardFor("recruiter", ["recruiter"], "/recruiter").action === "render");
check("admin on /admin renders", routeGuardFor("admin", ["admin"], "/admin").action === "render");

console.log("\n=== 2. REGRESSION: a candidate cannot open the recruiter dashboard ===");
let d = routeGuardFor("candidate", ["recruiter"], "/recruiter");
check("candidate on /recruiter is not rendered", d.action !== "render", d.action);
check("sent to their own dashboard", d.to === "/candidate", d.to);

console.log("\n=== 3. A recruiter cannot open the candidate dashboard ===");
d = routeGuardFor("recruiter", ["candidate"], "/candidate");
check("recruiter on /candidate is not rendered", d.action !== "render", d.action);
check("sent to /recruiter", d.to === "/recruiter", d.to);

console.log("\n=== 4. Admin is not sent to the candidate dashboard ===");
d = routeGuardFor("admin", ["candidate"], "/candidate");
check("admin on /candidate redirects to /admin", d.to === "/admin", d.to);

console.log("\n=== 5. Candidate-only pages are closed to other roles ===");
for (const path of ["/applications", "/interview"]) {
  d = routeGuardFor("recruiter", ["candidate"], path);
  check(`recruiter on ${path} redirects`, d.action === "redirect" && d.to === "/recruiter", `${d.action} ${d.to ?? ""}`);
  check(`candidate on ${path} renders`, routeGuardFor("candidate", ["candidate"], path).action === "render");
}

console.log("\n=== 6. Unrestricted pages stay open to every signed-in role ===");
check("candidate on /companies renders", routeGuardFor("candidate", null, "/companies").action === "render");
check("recruiter on /companies renders", routeGuardFor("recruiter", null, "/companies").action === "render");
check("admin on /companies renders", routeGuardFor("admin", null, "/companies").action === "render");
check("an empty role list means no restriction", routeGuardFor("recruiter", [], "/companies").action === "render");

console.log("\n=== 7. Role casing does not matter ===");
check("CANDIDATE matches candidate", routeGuardFor("CANDIDATE", ["candidate"], "/candidate").action === "render");
check("Recruiter matches recruiter", routeGuardFor("Recruiter", ["recruiter"], "/recruiter").action === "render");

console.log("\n=== 8. An unknown role cannot cause a redirect loop ===");
// dashboardPathForRole falls back to /candidate, so an unrecognised role sitting
// on /candidate has nowhere to be sent - it must show a notice, not redirect.
d = routeGuardFor("unexpected-role", ["candidate"], "/candidate");
check("notice instead of redirect on the fallback dashboard", d.action === "notice", d.action);
d = routeGuardFor(null, ["candidate"], "/candidate");
check("missing role behaves the same", d.action === "notice", d.action);
d = routeGuardFor("unexpected-role", ["recruiter"], "/recruiter");
check("elsewhere it still redirects to the fallback", d.action === "redirect" && d.to === "/candidate", `${d.action} ${d.to ?? ""}`);

console.log("\n=== 9. No decision on any route can chain into a second redirect ===");
let chained = 0;
for (const role of ROLES) {
  for (const route of ROUTES) {
    const first = routeGuardFor(role, route.allowedRoles, route.path);
    if (first.action !== "redirect") continue;
    const second = routeGuardFor(role, ROUTES.find((r) => r.path === first.to)?.allowedRoles, first.to);
    if (second.action === "redirect") {
      chained++;
      console.log(`        ${role} ${route.path} -> ${first.to} -> ${second.to}`);
    }
  }
}
check("every redirect target settles (render or notice)", chained === 0, `${chained} chained`);

console.log("\n=== 10. App.jsx actually wires those roles onto the routes ===");
const appSource = readFileSync(new URL("../src/App.jsx", import.meta.url), "utf8");

// Return one route's own source, bounded by the next <Route tag, so a guard
// from a neighbouring route can never be mistaken for this one's.
const blockFor = (path) => {
  const marker = `path="${path}"`;
  const at = appSource.indexOf(marker);
  if (at === -1) return null;
  const rest = appSource.slice(at + marker.length);
  const nextRoute = rest.search(/<Route\s/);
  return nextRoute === -1 ? rest : rest.slice(0, nextRoute);
};

for (const route of ROUTES) {
  const block = blockFor(route.path);
  if (block === null) {
    check(`${route.path} exists in App.jsx`, false, "route not found");
    continue;
  }
  const guard = block.match(/<ProtectedRoute([^>]*)>/);
  const rolesAttr = block.match(/allowedRoles=\{\[([^\]]*)\]\}/);

  if (!route.allowedRoles) {
    check(`${route.path} is open to any signed-in user`, Boolean(guard) && !rolesAttr, rolesAttr ? rolesAttr[1] : "no guard");
    continue;
  }

  const wired = rolesAttr
    ? rolesAttr[1].split(",").map((s) => s.trim().replace(/"/g, "")).filter(Boolean)
    : null;
  check(
    `${route.path} is guarded by ${route.allowedRoles.join(", ")}`,
    Boolean(guard) && sameRoles(wired, route.allowedRoles),
    wired ? wired.join(",") : "no allowedRoles",
  );
}

function sameRoles(actual, expected) {
  if (!actual || actual.length !== expected.length) return false;
  return [...actual].sort().join(",") === [...expected].sort().join(",");
}

console.log("\n=== 11. Dashboard path falls back safely ===");
check("unknown role lands on /candidate", dashboardPathForRole("nope") === "/candidate", dashboardPathForRole("nope"));
check("missing role lands on /candidate", dashboardPathForRole(undefined) === "/candidate");

console.log("\n" + "=".repeat(60));
if (failures) { console.log(`RESULT: ${failures} FAILED`); process.exit(1); }
console.log("RESULT: all role routing checks passed.");
