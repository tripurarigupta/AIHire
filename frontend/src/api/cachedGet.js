import apiClient from "./client";
import { DEFAULT_TTL_MS, readCache, writeCache } from "../utils/apiCache";

// In-flight requests, so several components asking for the same path at the same
// moment (e.g. two pages mounting together) share one network call.
const inFlight = new Map();

/**
 * GET a path through the shared cache.
 *
 * Within the TTL this resolves from memory without touching the network, which
 * is what makes switching between the candidate pages instant. `force` skips the
 * cache for callers that must have fresh data.
 */
export const cachedGet = (path, { ttl = DEFAULT_TTL_MS, force = false } = {}) => {
  if (!force) {
    const cached = readCache(path, ttl);
    if (cached !== undefined) return Promise.resolve(cached);
  }

  if (inFlight.has(path)) return inFlight.get(path);

  const request = apiClient
    .get(path)
    .then((response) => writeCache(path, response.data, ttl))
    .finally(() => inFlight.delete(path));

  inFlight.set(path, request);
  return request;
};

export default cachedGet;
