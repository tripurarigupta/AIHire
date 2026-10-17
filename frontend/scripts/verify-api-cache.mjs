/**
 * Unit tests for the shared response cache that the candidate pages read through.
 *
 * Why this is guarded: the cache is keyed by request path only, so a bug here can
 * serve one user's profile to the next user on the same browser, or keep showing
 * a stale application list after an apply. Both are silent in the UI.
 *
 * Run: node scripts/verify-api-cache.mjs
 */
import {
  DEFAULT_TTL_MS,
  readCache,
  writeCache,
  invalidate,
  clearApiCache,
  cacheSize,
} from "../src/utils/apiCache.js";
import { readFileSync } from "node:fs";

let failures = 0;
const check = (name, cond, detail = "") => {
  if (cond) console.log(`  PASS  ${name}`);
  else { console.log(`  FAIL  ${name} ${detail}`); failures++; }
};

const read = (p) => readFileSync(new URL(p, import.meta.url), "utf8");

console.log("\n=== 1. A written value is served back ===");
clearApiCache();
writeCache("/applications/me", [{ id: "a1" }]);
const hit = readCache("/applications/me");
check("returns the stored value", Array.isArray(hit) && hit[0].id === "a1");
check("returns the same reference (no clone cost)", hit === readCache("/applications/me"));
check("one entry stored", cacheSize() === 1);

console.log("\n=== 2. Unknown keys miss ===");
check("unknown path is undefined", readCache("/nothing/here") === undefined);
check("key is path-exact, not prefix", readCache("/applications") === undefined);

console.log("\n=== 3. Expired entries are dropped on read ===");
clearApiCache();
writeCache("/jobs", [{ id: "j1" }]);
// ttl -1 makes (now - cachedAt) > ttl true for any timestamp, including "now",
// so this does not depend on sleeping.
check("expired read is undefined", readCache("/jobs", -1) === undefined);
check("expired entry was evicted", cacheSize() === 0);
check("re-writing works after eviction", writeCache("/jobs", []) !== undefined);

console.log("\n=== 4. Default TTL is a sensible revalidation window ===");
check("DEFAULT_TTL_MS is 60s", DEFAULT_TTL_MS === 60_000, String(DEFAULT_TTL_MS));

console.log("\n=== 5. invalidate() drops exactly one key ===");
clearApiCache();
writeCache("/applications/me", []);
writeCache("/candidate-profile/me", {});
invalidate("/applications/me");
check("invalidated key misses", readCache("/applications/me") === undefined);
check("other key survives", readCache("/candidate-profile/me") !== undefined);
check("invalidating a missing key is harmless", invalidate("/nope") === undefined);

console.log("\n=== 6. clearApiCache() empties everything (used on sign-in/out) ===");
clearApiCache();
check("cache is empty", cacheSize() === 0);
check("previously cached data is gone", readCache("/candidate-profile/me") === undefined);

console.log("\n=== 7. Sign-in and sign-out clear the cache ===");
const auth = read("../src/context/AuthContext.jsx");
check("AuthContext imports clearApiCache", /import\s*{[^}]*clearApiCache[^}]*}\s*from\s*"\.\.\/utils\/apiCache"/.test(auth));
check("login clears before storing the new token",
  /clearApiCache\(\);[\s\S]{0,200}localStorage\.setItem\("token"/.test(auth));
check("logout clears", /const logout = \(\) => \{\s*clearApiCache\(\);/.test(auth));

console.log("\n=== 8. The candidate pages read the shared resources through the cache ===");
const pages = {
  "CandidateDashboard": read("../src/pages/CandidateDashboard.jsx"),
  "ApplicationsPage": read("../src/pages/ApplicationsPage.jsx"),
  "CompaniesPage": read("../src/pages/CompaniesPage.jsx"),
  "InterviewPage": read("../src/pages/InterviewPage.jsx"),
};

for (const [name, src] of Object.entries(pages)) {
  check(`${name} imports cachedGet`, /from "\.\.\/api\/cachedGet"/.test(src));
  // The regression this catches: a page quietly reverting to apiClient.get for a
  // shared resource, which makes that one page slow again for no visible reason.
  check(`${name} does not GET /applications/me directly`,
    !/apiClient\.get\(\s*"\/applications\/me"/.test(src));
  check(`${name} does not GET /jobs directly`,
    !/apiClient\.get\(\s*"\/jobs"/.test(src));
}

console.log("\n=== 9. Mutations keep the cache honest ===");
check("editing the profile rewrites the cached copy",
  pages.CandidateDashboard.includes('writeCache("/candidate-profile/me", res.data)'));
check("applying from the job board invalidates the applications list",
  /invalidate\("\/applications\/me"\)/.test(pages.CompaniesPage));

console.log("\n=== 10. Interview history is deliberately NOT cached ===");
// It changes the moment an interview is submitted, and the page refetches it
// right after evaluation; a cached copy would show the pre-submit history.
check("history still uses apiClient.get",
  /apiClient\.get\("\/interviews\/history"\)/.test(pages.InterviewPage));

console.log("\n=== 11. Concurrent callers share one request ===");
const cachedGetSrc = read("../src/api/cachedGet.js");
check("in-flight requests are deduplicated", /inFlight\.has\(path\)/.test(cachedGetSrc));
check("in-flight entry is cleared when the request settles",
  /\.finally\(\(\) => inFlight\.delete\(path\)\)/.test(cachedGetSrc));
check("force skips the cache read", /force = false/.test(cachedGetSrc));

console.log("\n" + "=".repeat(60));
if (failures) { console.log(`RESULT: ${failures} FAILED`); process.exit(1); }
console.log("RESULT: all api cache checks passed.");
