export function formatAppDate(app) {
  const ts = app.applied_at || app.created_at;
  if (!ts) return "-";
  try {
    const d = new Date(ts);
    if (Number.isNaN(d.getTime())) return String(ts);
    return d.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return String(ts);
  }
}

export function formatDateTime(ts) {
  if (!ts) return "";
  try {
    const d = new Date(ts);
    if (Number.isNaN(d.getTime())) return String(ts);
    return d.toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return String(ts);
  }
}

const statusTextMap = {
  applied: "Applied Date",
  interview: "Tech Screen",
  shortlisted: "Shortlisted",
  selected: "Offer",
  rejected: "No Response",
};

export function statusLabelRight(status) {
  const key = typeof status === "string" ? status.toLowerCase() : "";
  return statusTextMap[key] || "";
}

export function csvEscape(value) {
  const str = String(value == null ? "" : value);
  if (str.includes(",") || str.includes('"') || str.includes("\n")) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

const KNOWN_COMPANIES = ["TechCorp", "StartupXYZ", "DataFlow Systems", "Acme", "Initech", "Umbrella"];

export function csvEscapeSimple(value) {
  const str = String(value == null ? "" : value);
  if (str.includes(",") || str.includes('"') || str.includes("\n")) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

export function extractCompanyFallback(jobTitle) {
  const cleaned = (jobTitle || "").replace(/\./g, " ").trim();
  for (const name of KNOWN_COMPANIES) {
    if (cleaned.toLowerCase().includes(name.toLowerCase())) return name;
  }
  const firstWord = cleaned.split(/\s+/)[0];
  return firstWord && firstWord.length > 1 ? firstWord : "Company";
}
