// A tiny, dependency-free response cache.
//
// Why this exists: the candidate area is built from separate routes
// (/candidate, /applications, /companies), so every click unmounts one page and
// mounts another, and each page fetches its data again from scratch. The
// recruiter dashboard does not have that problem because its "tables" are
// ?section= tabs on one route - the component never remounts, so switching
// sections makes no requests at all.
//
// Caching reads briefly levels that difference: switching between candidate
// pages reuses what was fetched seconds ago instead of paying for the same
// round trips again.
//
// Kept pure (no imports, no network) so the eviction rules can be unit tested
// without a browser - see scripts/verify-api-cache.mjs.

/** How long a cached response is reused before it is fetched again. */
export const DEFAULT_TTL_MS = 60_000;

const entries = new Map();

/**
 * Cached value for `key`, or undefined when there is nothing usable.
 * Expired entries are dropped on read so the map cannot grow forever.
 */
export const readCache = (key, ttl = DEFAULT_TTL_MS) => {
  const entry = entries.get(key);
  if (!entry) return undefined;

  if (Date.now() - entry.cachedAt > ttl) {
    entries.delete(key);
    return undefined;
  }

  return entry.value;
};

export const writeCache = (key, value) => {
  entries.set(key, { value, cachedAt: Date.now() });
  return value;
};

/** Drop one key, e.g. straight after a mutation that invalidates it. */
export const invalidate = (key) => {
  entries.delete(key);
};

/**
 * Drop everything.
 *
 * Must be called whenever the signed-in user changes: entries are keyed by path
 * only, so without this the next user to sign in on the same browser could be
 * served the previous user's profile and applications.
 */
export const clearApiCache = () => {
  entries.clear();
};

/** Number of stored entries - for diagnostics and tests. */
export const cacheSize = () => entries.size;
