export function initialsFor(name) {
  const parts = (name || "").trim().split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    return (
      (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase() ||
      "?"
    );
  }
  return (parts[0]?.charAt(0) || "?").toUpperCase();
}

export function displayNameFor(user) {
  const raw = user?.full_name || user?.email?.split("@")[0] || "Candidate";
  return (
    raw
      .split(" ")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
      .join(" ") || "Candidate"
  );
}
