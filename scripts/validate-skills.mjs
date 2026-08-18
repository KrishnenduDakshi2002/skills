import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const skillsRoot = path.resolve("skills");
const errors = [];
const warnings = [];

async function findSkillFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(
    entries
      .filter((entry) => !entry.name.startsWith("."))
      .map(async (entry) => {
        const entryPath = path.join(directory, entry.name);
        if (entry.isDirectory()) return findSkillFiles(entryPath);
        return entry.name === "SKILL.md" ? [entryPath] : [];
      }),
  );

  return nested.flat();
}

function readFrontmatter(content, file) {
  const lines = content.replaceAll("\r\n", "\n").split("\n");
  if (lines[0] !== "---") {
    errors.push(`${file}: must start with YAML frontmatter`);
    return null;
  }

  const closingIndex = lines.indexOf("---", 1);
  if (closingIndex === -1) {
    errors.push(`${file}: frontmatter has no closing delimiter`);
    return null;
  }

  return lines.slice(1, closingIndex);
}

function findField(lines, field) {
  const matcher = new RegExp(`^${field}\\s*:\\s*(.*)$`);
  const index = lines.findIndex((line) => matcher.test(line));
  if (index === -1) return null;

  const inlineValue = lines[index].match(matcher)?.[1].trim() ?? "";
  if (inlineValue && inlineValue !== ">" && inlineValue !== "|") {
    return inlineValue.replace(/^(["'])(.*)\1$/, "$2");
  }

  const blockLines = [];
  for (const line of lines.slice(index + 1)) {
    if (!/^\s+/.test(line)) break;
    blockLines.push(line.trim());
  }
  return blockLines.join(" ").trim();
}

const skillFiles = await findSkillFiles(skillsRoot);
const names = new Map();

for (const file of skillFiles) {
  const relativeFile = path.relative(process.cwd(), file);
  const content = await readFile(file, "utf8");
  const frontmatter = readFrontmatter(content, relativeFile);
  if (!frontmatter) continue;

  const name = findField(frontmatter, "name");
  const description = findField(frontmatter, "description");
  const skillDirectory = path.dirname(file);
  const folderName = path.basename(skillDirectory);
  const topLevelFields = frontmatter
    .filter((line) => /^[a-zA-Z0-9_-]+\s*:/.test(line))
    .map((line) => line.slice(0, line.indexOf(":")).trim());
  const reviewedFields = new Set(["name", "description", "disable-model-invocation"]);
  const agentSpecificFields = topLevelFields.filter((field) => !reviewedFields.has(field));
  const disableModelInvocation = findField(frontmatter, "disable-model-invocation");

  if (!name) {
    errors.push(`${relativeFile}: missing frontmatter name`);
  } else {
    if (!/^[a-z0-9-]{1,63}$/.test(name)) {
      errors.push(`${relativeFile}: name must use 1-63 lowercase letters, digits, or hyphens`);
    }
    if (folderName !== name) {
      errors.push(`${relativeFile}: folder "${folderName}" must match name "${name}"`);
    }
    if (names.has(name)) {
      errors.push(`${relativeFile}: duplicate name also used by ${names.get(name)}`);
    } else {
      names.set(name, relativeFile);
    }
  }

  if (!description) {
    errors.push(`${relativeFile}: missing or empty frontmatter description`);
  }

  if (agentSpecificFields.length > 0) {
    warnings.push(
      `${relativeFile}: verify portability of frontmatter field(s): ${agentSpecificFields.join(", ")}`,
    );
  }

  if (disableModelInvocation && disableModelInvocation !== "true") {
    warnings.push(
      `${relativeFile}: disable-model-invocation should be true when the Claude Code exception is used`,
    );
  }

  let openaiMetadata = "";
  try {
    openaiMetadata = await readFile(path.join(skillDirectory, "agents", "openai.yaml"), "utf8");
  } catch {
    // Product-specific metadata is optional unless invocation policy requires it.
  }

  const codexExplicitOnly = /^\s*allow_implicit_invocation:\s*false\s*$/m.test(openaiMetadata);
  const claudeExplicitOnly = disableModelInvocation === "true";
  if (claudeExplicitOnly !== codexExplicitOnly) {
    errors.push(
      `${relativeFile}: explicit-only workflows must pair Claude Code disable-model-invocation with Codex allow_implicit_invocation: false`,
    );
  }

  try {
    await readFile(path.join(skillDirectory, "LICENSE"), "utf8");
  } catch {
    errors.push(`${relativeFile}: missing LICENSE carried with selective installations`);
  }

  const lineCount = content.split(/\r?\n/).length;
  if (lineCount > 500) {
    warnings.push(`${relativeFile}: ${lineCount} lines; consider progressive disclosure`);
  }
}

if (skillFiles.length === 0) {
  console.log("No skills found yet; repository scaffold is valid.");
} else {
  console.log(`Validated ${skillFiles.length} skill(s).`);
}

for (const warning of warnings) console.warn(`Warning: ${warning}`);
for (const error of errors) console.error(`Error: ${error}`);

if (errors.length > 0) process.exitCode = 1;
