export const site = {
  title: "ORPHEON",
  tagline: "A continuously generated record of the things I build.",
  owner: "venvennnn",
  ownerName: "Venmani A D",
  github: "https://github.com/venvennnn",
  timezone: "Asia/Kolkata",
} as const;

export function withBase(path = ""): string {
  const base = import.meta.env.BASE_URL || "/";
  const trimmed = path.replace(/^\/+/, "");
  if (!trimmed) return base.endsWith("/") ? base : `${base}/`;
  const prefix = base.endsWith("/") ? base : `${base}/`;
  return `${prefix}${trimmed}`;
}

export function formatShortDate(iso: string | undefined): string {
  if (!iso) return "—";
  const date = new Date(iso.length === 10 ? `${iso}T00:00:00+05:30` : iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "Asia/Kolkata",
  });
}

export function shortSha(sha: string | undefined): string {
  return sha ? sha.slice(0, 7) : "—";
}
