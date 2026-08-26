import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";

const CONTENT_ROOT = path.join(process.cwd(), "src/content/projects");

export interface ProjectMeta {
  name: string;
  slug: string;
  repository: string;
  status: string;
  categories: string[];
  tagline?: string;
  description?: string;
  demo?: string | null;
  last_updated: string;
  last_commit: string;
  commit_count?: number;
  github?: string;
}

export interface MarkdownDoc {
  meta: Record<string, unknown>;
  body: string;
}

export interface Takeaway {
  title: string;
  body: string;
}

export interface Project {
  meta: ProjectMeta;
  problem: MarkdownDoc | null;
  summary: MarkdownDoc | null;
  results: MarkdownDoc | null;
  examples: MarkdownDoc | null;
  architecture: string;
}

function readMarkdown(filePath: string): MarkdownDoc | null {
  if (!fs.existsSync(filePath)) return null;
  const raw = fs.readFileSync(filePath, "utf8");
  const parsed = matter(raw);
  return { meta: parsed.data as Record<string, unknown>, body: parsed.content.trim() };
}

function readOptional(filePath: string): string {
  if (!fs.existsSync(filePath)) return "";
  return fs.readFileSync(filePath, "utf8");
}

export function listProjectSlugs(): string[] {
  if (!fs.existsSync(CONTENT_ROOT)) return [];
  return fs
    .readdirSync(CONTENT_ROOT, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && fs.existsSync(path.join(CONTENT_ROOT, entry.name, "metadata.json")))
    .map((entry) => entry.name)
    .sort();
}

export function loadProject(slug: string): Project | null {
  const folder = path.join(CONTENT_ROOT, slug);
  const metaPath = path.join(folder, "metadata.json");
  if (!fs.existsSync(metaPath)) return null;
  const meta = JSON.parse(fs.readFileSync(metaPath, "utf8")) as ProjectMeta;
  meta.slug = meta.slug || slug;
  meta.categories = meta.categories || [];
  return {
    meta,
    problem: readMarkdown(path.join(folder, "problem.md")),
    summary: readMarkdown(path.join(folder, "summary.md")),
    results: readMarkdown(path.join(folder, "results.md")),
    examples: readMarkdown(path.join(folder, "examples.md")),
    architecture: readOptional(path.join(folder, "architecture.mmd")).trim(),
  };
}

export function loadAllProjects(): Project[] {
  return listProjectSlugs()
    .map((slug) => loadProject(slug))
    .filter((project): project is Project => project !== null)
    .sort((a, b) => {
      const left = a.meta.last_updated || "";
      const right = b.meta.last_updated || "";
      return right.localeCompare(left);
    });
}

export function isExperiment(project: Project): boolean {
  const status = (project.meta.status || "").toLowerCase();
  const categories = project.meta.categories.map((item) => item.toLowerCase());
  return status === "experimental" || categories.includes("experiment") || categories.includes("experiments");
}

export function githubUrl(project: Project): string {
  return project.meta.github || `https://github.com/${project.meta.repository}`;
}

export function splitTakeaways(body: string): { intro: string; takeaways: Takeaway[] } {
  if (!body.trim()) return { intro: "", takeaways: [] };
  const parts = body.trim().split(/\n(?=###\s+)/);
  if (parts.length < 2) return { intro: body.trim(), takeaways: [] };
  const intro = parts[0]?.trim() ?? "";
  const takeaways = parts.slice(1).map((chunk) => {
    const lines = chunk.trim().split("\n");
    return {
      title: (lines[0] ?? "").replace(/^###\s+/, "").trim(),
      body: lines.slice(1).join("\n").trim(),
    };
  });
  return { intro, takeaways };
}
