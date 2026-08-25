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
  reference_count?: number;
  github?: string;
}

export interface MarkdownDoc {
  meta: Record<string, unknown>;
  body: string;
}

export interface Project {
  meta: ProjectMeta;
  eli15: MarkdownDoc | null;
  technical: MarkdownDoc | null;
  references: MarkdownDoc | null;
  buildLog: MarkdownDoc | null;
  architecture: string;
  evolution: MarkdownDoc | null;
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
    eli15: readMarkdown(path.join(folder, "eli15.md")),
    technical: readMarkdown(path.join(folder, "technical.md")),
    references: readMarkdown(path.join(folder, "references.md")),
    buildLog: readMarkdown(path.join(folder, "build-log.md")),
    architecture: readOptional(path.join(folder, "architecture.mmd")).trim(),
    evolution: readMarkdown(path.join(folder, "evolution.md")),
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

export function splitBuildLog(body: string): { date: string; body: string }[] {
  if (!body.trim()) return [];
  const chunks = body.trim().split(/\n(?=\d{1,2} [A-Z][a-z]+ \d{4}\s*\n)/);
  return chunks
    .map((chunk) => {
      const lines = chunk.trim().split("\n");
      return { date: lines[0] ?? "", body: lines.slice(1).join("\n").trim() };
    })
    .filter((entry) => entry.date);
}

export function splitEvolutions(body: string): string[] {
  if (!body.trim()) return [];
  return body
    .trim()
    .split(/\n(?=Evolution #\d+)/)
    .map((chunk) => chunk.trim())
    .filter(Boolean);
}
