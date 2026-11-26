#!/usr/bin/env node
// Checks a pull request body (and optionally its title) against the Layers story format, v1.
// Usage: node check-story.mjs <body.md | -> [--title "<title>"] [--allow Word,Word]
// Exit codes: 0 no errors (warnings may remain), 1 rules broken, 2 could not check.

import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, rmSync } from "node:fs";
import { readFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const START = "<!-- layers:story v1 -->";
const END = "<!-- /layers:story -->";
const CELLS = ["Applies to", "Existing data", "Who notices"];
const CLASS_DEFS = [
  "classDef old fill:#fdecec,stroke:#d93036,stroke-dasharray:5 3,color:#1c1c1f",
  "classDef new fill:#e8f6ef,stroke:#218358,color:#1c1c1f",
];
const LIMITS = {
  titleWords: 12,
  nodes: 11,
  labelWords: 9,
  groups: 4,
  groupItems: 4,
  itemWords: 10,
  cellWords: 18,
  listenWords: 105,
  edgeLabelWords: 4,
};
// Product and brand names that look like code identifiers. Extend per run with --allow.
const BRAND_NAMES = [
  "AirPods", "ChatGPT", "DevOps", "DynamoDB", "FaceTime", "GitHub", "GitLab", "HubSpot",
  "iCloud", "iOS", "iPad", "iPadOS", "iPhone", "JavaScript", "LinkedIn", "macOS", "MongoDB",
  "MySQL", "Next.js", "Node.js", "OpenAI", "PayPal", "PostgreSQL", "PowerPoint", "SharePoint",
  "TikTok", "TypeScript", "Vue.js", "WhatsApp", "WordPress", "YouTube",
];
const FILE_EXTENSIONS =
  "ts|tsx|js|jsx|mjs|cjs|json|py|go|rb|java|kt|swift|md|ya?ml|sql|sh|css|scss|html|vue|rs|cpp|cc|hpp|cs|php|toml|lock|env|xml|gradle|tf|txt|csv";
const DOMAIN_ENDINGS = new Set(["com", "org", "net", "io", "ai", "dev", "app", "co", "in", "me", "so"]);
const STORY_SYMBOLS = /[`*#_<>=+\\/|{}[\]~^%$&@→←⇒×÷]/gu;

const usage = 'Usage: node check-story.mjs <body.md | -> [--title "<title>"] [--allow Word,Word]';

function parseArgs(argv) {
  const options = { file: null, title: null, allow: [] };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--title") options.title = argv[++index] ?? "";
    else if (argument === "--allow") options.allow.push(...(argv[++index] ?? "").split(","));
    else if (argument === "--help" || argument === "-h") options.help = true;
    else if (options.file === null) options.file = argument;
    else throw new Error(`Unexpected argument: ${argument}`);
  }
  return options;
}

async function readBody(file) {
  if (file !== "-") return readFile(file, "utf8");
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks).toString("utf8");
}

const countWords = (text) => text.split(/\s+/).filter((word) => /[\p{L}\p{N}]/u.test(word)).length;

function createReport() {
  const problems = [];
  return {
    problems,
    error: (where, message) => problems.push({ level: "error", where, message }),
    warn: (where, message) => problems.push({ level: "warning", where, message }),
  };
}

// ---------------------------------------------------------------- plain-words checks

function codeNameFindings(text, allowed) {
  const findings = [];
  const tokens = [];
  const add = (kind, token) => {
    const trimmed = token.trim();
    if (allowed.has(trimmed)) return;
    if (tokens.some((seen) => seen.includes(trimmed) || trimmed.includes(seen))) return;
    tokens.push(trimmed);
    findings.push(`${kind} "${trimmed}"`);
  };
  const withoutUrls = text.replace(/https?:\/\/\S+/g, " ");
  const patterns = [
    ["backtick", /`/g],
    ["file name", new RegExp(`(?<![\\w/.-])(?:[\\w.-]+/)*[\\w-]+\\.(?:${FILE_EXTENSIONS})\\b`, "g")],
    ["file path", /(?<![\w/.:-])[\w.-]+\/[\w.-]+\/[\w./-]*/g],
    ["call", /\b[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*\s*\(\s*\)/g],
    ["dotted call", /\b[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)+\s*\(/g],
    ["snake_case name", /\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b/g],
    ["constant name", /\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b/g],
    ["camelCase name", /\b[a-z]+(?:[A-Z][a-z0-9]*)+\b/g],
    ["PascalCase name", /\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+\b/g],
    ["code operator", /\w(?:::|->|=>)\w?|(?:^|\s)(?:==|!=|>=|<=|&&|\|\|)(?:\s|$)/g],
    ["command-line flag", /(?:^|\s)--[a-z][\w-]*/g],
    [
      "command",
      /(?:^|\s)(?:npm|npx|yarn|pnpm|bun|git|gh|node|tsc|jest|vitest|pytest|make|docker|kubectl|cargo)\s+(?:run|test|install|i|ci|exec|build|push|commit|merge|rebase|lint|-)/g,
    ],
  ];
  for (const [kind, pattern] of patterns) {
    for (const match of withoutUrls.matchAll(pattern)) add(kind, match[0]);
  }
  for (const match of withoutUrls.matchAll(/\b([a-z_$][\w$]+)\.([a-z_$][\w$]+)\b/g)) {
    if (!DOMAIN_ENDINGS.has(match[2]) && !new RegExp(`^(?:${FILE_EXTENSIONS})$`).test(match[2])) {
      add("dotted name", match[0]);
    }
  }
  if (/[a-z0-9)\]]\s*[*×÷^]\s*[a-z0-9(]/i.test(withoutUrls)) findings.push("formula");
  if (/\b\d+\s*(?:\/\s*\d+\s*)?(?:unit |integration |e2e |end-to-end )?(?:tests?|specs?|test cases|assertions)\b/i.test(withoutUrls)) {
    findings.push("test count");
  }
  if (/\b(?:tests?|specs?|suites?|checks?|jest|vitest|pytest|lint|typecheck)\b[^.]{0,25}\b(?:pass|passes|passed|passing|green|clean)\b/i.test(withoutUrls)) {
    findings.push("test result (mention tests only when something failed or was not tested)");
  }
  return [...new Set(findings)];
}

function checkPlainWords(report, where, text, allowed, { allowQuestion = false } = {}) {
  for (const finding of codeNameFindings(text, allowed)) {
    report.error(where, `looks like code, not product words: ${finding}`);
  }
  if (/\b(?:decide|should we|do we want|which option|please confirm|your call|let me know)\b/i.test(text)) {
    report.error(where, 'reads like a "decide" question; say only what the change does');
  } else if (!allowQuestion && /\?\s*$/.test(text.trim())) {
    report.warn(where, "ends with a question; a pull request says what happened, it does not ask");
  }
}

function checkWordCap(report, where, text, limit, noun) {
  const words = countWords(text);
  if (words > limit) report.error(where, `${noun} has ${words} words; the cap is ${limit}`);
}

// ---------------------------------------------------------------- title

function checkTitle(report, title, allowed) {
  const match = title.trim().match(/^([a-z]+)(\([^)]*\))?(!)?:\s+(.+)$/);
  if (!match) {
    report.error("title", "must look like <type>(<scope>): <headline>, for example fix(billing): ...");
    return;
  }
  const headline = match[4]
    .replace(/\[[A-Z][A-Z0-9]+-\d+\]|\(?\b[A-Z][A-Z0-9]+-\d+\b\)?|\(#\d+\)|#\d+/g, " ")
    .trim();
  checkWordCap(report, "title", headline, LIMITS.titleWords, "headline");
  checkPlainWords(report, "title", headline, allowed);
}

// ---------------------------------------------------------------- story structure

function splitStory(report, lines) {
  const startLines = lines.flatMap((line, index) => (line.trim() === START ? [index] : []));
  const endLines = lines.flatMap((line, index) => (line.trim() === END ? [index] : []));
  if (startLines.length !== 1) {
    report.error("markers", `need exactly one "${START}" line, found ${startLines.length}`);
  }
  if (endLines.length !== 1) {
    report.error("markers", `need exactly one "${END}" line, found ${endLines.length}`);
  }
  if (startLines.length !== 1 || endLines.length !== 1) return null;
  const [start] = startLines;
  const [end] = endLines;
  if (end < start) {
    report.error("markers", "the end marker comes before the start marker");
    return null;
  }
  if (lines.slice(0, start).some((line) => line.trim() !== "")) {
    report.warn("markers", "text before the start marker; Layers draws the story first, so put other text after the end marker");
  }
  return { first: start + 1, storyLines: lines.slice(start + 1, end) };
}

function readBlocks(report, storyLines, lineNumber) {
  const blocks = [];
  for (let index = 0; index < storyLines.length; index += 1) {
    const raw = storyLines[index];
    const line = raw.trim();
    const at = lineNumber(index);
    if (line === "") continue;
    if (/^```/.test(line)) {
      const fenceEnd = storyLines.findIndex((candidate, after) => after > index && candidate.trim() === "```");
      if (fenceEnd === -1) {
        report.error(`line ${at}`, "code fence is never closed");
        return blocks;
      }
      const content = storyLines.slice(index + 1, fenceEnd);
      if (line === "```mermaid") blocks.push({ kind: "chart", at, content });
      else report.error(`line ${at}`, "only ```mermaid fences belong in the story; no code blocks");
      index = fenceEnd;
      continue;
    }
    const cell = line.match(/^\*\*(Applies to|Existing data|Who notices):\*\*\s*(.*)$/);
    if (cell) {
      blocks.push({ kind: "cell", at, name: cell[1], text: cell[2].trim() });
      continue;
    }
    if (line === "<details>") {
      const close = storyLines.findIndex((candidate, after) => after > index && candidate.trim() === "</details>");
      if (close === -1) {
        report.error(`line ${at}`, "<details> is never closed");
        return blocks;
      }
      blocks.push({ kind: "details", at, content: storyLines.slice(index + 1, close).map((text) => text.trim()) });
      index = close;
      continue;
    }
    if (line === "**Before**" || line === "**Now**") {
      blocks.push({ kind: line === "**Before**" ? "before" : "now", at });
      continue;
    }
    const heading = line.match(/^####\s+(.+)$/);
    if (heading) {
      blocks.push({ kind: "group", at, title: heading[1].trim(), items: [] });
      continue;
    }
    const item = line.match(/^-\s+(.+)$/);
    if (item) {
      const group = blocks.at(-1);
      if (group?.kind === "group") group.items.push({ at, text: item[1].trim() });
      else report.error(`line ${at}`, "list item outside a #### group");
      continue;
    }
    blocks.push({ kind: "text", at, text: line });
  }
  return blocks;
}

function checkSequence(report, blocks) {
  const phaseOf = { chart: 0, before: 0, now: 0, group: 0, cell: 1, details: 2 };
  let phase = 0;
  blocks.forEach((block, index) => {
    if (block.kind === "text") {
      const message =
        blocks[index - 1]?.kind === "cell" && blocks[index - 1].at === block.at - 1
          ? "a cell continues onto a second line; keep each cell on one line"
          : `text outside the format: "${block.text.slice(0, 60)}"`;
      report.error(`line ${block.at}`, message);
      return;
    }
    if (phaseOf[block.kind] < phase) {
      report.error(`line ${block.at}`, "out of order; the story is layout, then the three cells, then Listen");
    }
    phase = Math.max(phase, phaseOf[block.kind]);
  });
}

function detectLayout(report, blocks) {
  const layoutBlocks = blocks.filter((block) => ["chart", "before", "now", "group"].includes(block.kind));
  const shape = layoutBlocks.map((block) => block.kind).join(",");
  if (shape === "chart") return { name: "a", charts: [{ ...layoutBlocks[0], role: "only" }] };
  if (shape === "before,chart,now,chart") {
    return { name: "b", charts: [{ ...layoutBlocks[1], role: "Before" }, { ...layoutBlocks[3], role: "Now" }] };
  }
  if (layoutBlocks.length > 0 && layoutBlocks.every((block) => block.kind === "group")) {
    return { name: "c", charts: [], groups: layoutBlocks };
  }
  report.error(
    "layout",
    `need one of: (a) one chart, (b) **Before** + chart then **Now** + chart, (c) #### groups; found ${shape || "nothing"}`,
  );
  return { name: null, charts: layoutBlocks.filter((block) => block.kind === "chart"), groups: [] };
}

function checkGroups(report, groups, allowed) {
  if (groups.length > LIMITS.groups) report.error("groups", `${groups.length} groups; the cap is ${LIMITS.groups}`);
  groups.forEach((group, groupIndex) => {
    const where = `group ${groupIndex + 1} "${group.title}"`;
    checkPlainWords(report, where, group.title, allowed);
    if (group.items.length === 0) report.error(where, "has no - items");
    if (group.items.length > LIMITS.groupItems) {
      report.error(where, `${group.items.length} items; the cap is ${LIMITS.groupItems}`);
    }
    group.items.forEach((item, itemIndex) => {
      const itemWhere = `${where}, item ${itemIndex + 1}`;
      checkWordCap(report, itemWhere, item.text, LIMITS.itemWords, "item");
      checkPlainWords(report, itemWhere, item.text, allowed);
    });
  });
}

function checkCells(report, blocks, allowed) {
  const cells = blocks.filter((block) => block.kind === "cell");
  for (const name of CELLS) {
    const found = cells.filter((cell) => cell.name === name);
    const where = `**${name}:**`;
    if (found.length === 0) {
      report.error(where, "missing; all three cells are always present");
      continue;
    }
    if (found.length > 1) report.error(where, "appears more than once");
    const [cell] = found;
    if (cell.text === "") report.error(where, "is empty; keep the text on the same line");
    checkWordCap(report, where, cell.text, LIMITS.cellWords, "cell");
    checkPlainWords(report, where, cell.text, allowed);
  }
  const order = cells.map((cell) => cell.name).join(",");
  if (cells.length === 3 && order !== CELLS.join(",")) {
    report.warn("cells", `order is ${order}; use ${CELLS.join(", ")}`);
  }
}

function checkListen(report, blocks, allowed) {
  const details = blocks.filter((block) => block.kind === "details");
  if (details.length !== 1) {
    report.error("Listen", `need exactly one <details> Listen block, found ${details.length}`);
    return;
  }
  const [block] = details;
  const [summary, ...rest] = block.content.filter((line) => line !== "");
  if (summary !== "<summary>Listen</summary>") {
    report.error("Listen", 'first line inside <details> must be "<summary>Listen</summary>"');
  }
  const text = rest.join(" ");
  if (text === "") {
    report.error("Listen", "has no spoken text");
    return;
  }
  const spoken = countWords(text);
  if (spoken > LIMITS.listenWords) {
    report.error(
      "Listen",
      `spoken version has ${spoken} words; the cap is ${LIMITS.listenWords} (about 40 seconds aloud). ` +
        "A change that needs more is too big for one pull request: split it into smaller, targeted ones.",
    );
  }
  const symbols = [...new Set(text.match(STORY_SYMBOLS) ?? [])];
  if (symbols.length > 0) {
    report.error("Listen", `contains ${symbols.map((symbol) => `"${symbol}"`).join(" ")}; write it as spoken words`);
  }
  checkPlainWords(report, "Listen", text, allowed);
}

// ---------------------------------------------------------------- charts

function checkChartSource(report, chart, where) {
  const lines = chart.content.map((line) => line.trim()).filter((line) => line !== "" && !line.startsWith("%%"));
  if (lines[0] !== "flowchart TD") report.error(where, 'first line must be "flowchart TD"');
  const lastTwo = lines.slice(-2);
  if (lastTwo[0] !== CLASS_DEFS[0] || lastTwo[1] !== CLASS_DEFS[1]) {
    report.error(where, "must end with exactly the two classDef lines (old, then new) from the format");
  }
  const body = lines.slice(1, -2);
  body.forEach((line) => {
    if (/^classDef\b/.test(line)) report.error(where, `extra classDef: "${line}"`);
    if (/^(?:style|linkStyle|class|click)\b/.test(line)) {
      report.error(where, `"${line.split(/\s/)[0]}" lines are not part of the format; mark steps with :::old or :::new`);
    }
    if (/^subgraph\b/.test(line)) report.warn(where, "subgraph is not part of the format; Layers may not draw it");
    if (/#quot;|&quot;/.test(line)) report.error(where, "no double quotes inside a label");
    const stripped = line.replace(/"[^"]*"/g, '""').replace(/\|[^|]*\|/g, "||");
    for (const match of stripped.matchAll(/\b([A-Za-z][\w-]*)\s*(\[\[|\[\(|\[\/|\[\\|\(\(\(|\(\(|\(\[|\(|\[|\{\{|\{|>)/g)) {
      const after = stripped.slice(match.index + match[0].length).trimStart();
      if (!after.startsWith('"')) report.error(where, `node ${match[1]}: put the label in double quotes, like ${match[1]}["..."]`);
    }
    if (/\s--\s+[^\s>-]/.test(stripped) || /\s==\s+[^\s>=]/.test(stripped)) {
      report.warn(where, 'write edge labels as -->|yes|, not "-- yes -->"');
    }
  });
}

/**
 * Installs the pinned parser into this folder the first time it is needed, as the skills CLI
 * copies the files but installs nothing. A lock directory keeps two checks from installing at once.
 */
function installParser(scriptsDir) {
  if (existsSync(path.join(scriptsDir, "node_modules", "mermaid", "package.json"))) return null;
  const lock = path.join(scriptsDir, ".installing");
  const deadline = Date.now() + 5 * 60_000;
  for (;;) {
    try {
      mkdirSync(lock);
      break;
    } catch {
      if (Date.now() > deadline) return "another install of the parser did not finish";
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 500);
      if (existsSync(path.join(scriptsDir, "node_modules", "mermaid", "package.json"))) return null;
    }
  }
  try {
    console.error("Installing the Mermaid parser once (needs network this time only)...");
    const npm = process.platform === "win32" ? "npm.cmd" : "npm";
    const result = spawnSync(npm, ["ci", "--prefix", scriptsDir, "--no-audit", "--no-fund", "--silent"], {
      stdio: ["ignore", "ignore", "pipe"],
      encoding: "utf8",
    });
    if (result.error) return `npm could not run: ${result.error.message}`;
    if (result.status !== 0) return `npm ci failed: ${(result.stderr || "").trim().split("\n").slice(-3).join(" ")}`;
    return null;
  } finally {
    rmSync(lock, { recursive: true, force: true });
  }
}

async function loadParser() {
  const scriptsDir = path.dirname(fileURLToPath(import.meta.url));
  const failed = installParser(scriptsDir);
  if (failed) return { missing: new Error(failed) };
  try {
    const { JSDOM } = await import("jsdom");
    const { window } = new JSDOM("<!doctype html><html><body></body></html>");
    globalThis.window ??= window;
    globalThis.document ??= window.document;
    const { default: mermaid } = await import("mermaid");
    mermaid.initialize({ startOnLoad: false, logLevel: 5, securityLevel: "strict" });
    return mermaid;
  } catch (error) {
    return { missing: error };
  }
}

async function checkChartWithParser(report, mermaid, chart, where, layout, allowed) {
  const text = chart.content.join("\n");
  let diagram;
  try {
    await mermaid.parse(text);
    diagram = await mermaid.mermaidAPI.getDiagramFromText(text);
  } catch (error) {
    const message = String(error?.message ?? error).split("\n").slice(0, 4).join(" | ");
    report.error(where, `Mermaid cannot parse this chart: ${message}`);
    return;
  }
  const vertices = [...diagram.db.getVertices().values()];
  const edges = diagram.db.getEdges();
  if (vertices.length > LIMITS.nodes) {
    report.error(where, `${vertices.length} nodes; the cap is ${LIMITS.nodes}`);
  }
  const classOf = new Map(vertices.map((vertex) => [vertex.id, vertex.classes.filter((name) => name !== "default")]));
  for (const vertex of vertices) {
    const nodeWhere = `${where}, node ${vertex.id}`;
    const classes = classOf.get(vertex.id);
    if (vertex.text === vertex.id || !vertex.text) {
      report.error(nodeWhere, 'has no label; give every node a quoted label like A["..."]');
      continue;
    }
    if (!["square", "diamond"].includes(vertex.type)) {
      report.warn(nodeWhere, `uses the ${vertex.type} shape; the format uses ["..."] for steps and {"..."} for decisions`);
    }
    checkWordCap(report, nodeWhere, vertex.text, LIMITS.labelWords, "label");
    checkPlainWords(report, nodeWhere, vertex.text, allowed, { allowQuestion: true });
    const unknown = classes.filter((name) => name !== "old" && name !== "new");
    if (unknown.length > 0) report.error(nodeWhere, `class ${unknown.join(", ")}; only :::old and :::new are allowed`);
    if (classes.includes("old") && classes.includes("new")) report.error(nodeWhere, "is marked both old and new");
    if (layout === "b" && chart.role === "Before" && classes.includes("new")) {
      report.error(nodeWhere, "the Before chart may use :::old only");
    }
    if (layout === "b" && chart.role === "Now" && classes.includes("old")) {
      report.error(nodeWhere, "the Now chart may use :::new only");
    }
  }
  for (const edge of edges) {
    const label = (edge.text ?? "").trim();
    if (label === "") continue;
    const edgeWhere = `${where}, edge ${edge.start} to ${edge.end}`;
    if (countWords(label) > LIMITS.edgeLabelWords) {
      report.warn(edgeWhere, `edge label "${label}" is long; keep edge labels to a few words`);
    }
    checkPlainWords(report, edgeWhere, label, allowed, { allowQuestion: true });
    if (layout === "a" && /\b(?:before|now|previously|old|new|after this)\b/i.test(label)) {
      report.error(edgeWhere, `edge label "${label}" tells old from new; use layout (b) with a Before and a Now chart`);
    }
  }
  if (layout === "a") {
    const marked = vertices.flatMap((vertex) => classOf.get(vertex.id));
    if (!marked.includes("old") && !marked.includes("new")) {
      report.warn(where, "no step is marked :::old or :::new, so the chart does not show the change");
    }
    for (const vertex of vertices) {
      if (classOf.get(vertex.id).length > 0) continue;
      const sources = edges.filter((edge) => edge.end === vertex.id).flatMap((edge) => classOf.get(edge.start) ?? []);
      if (sources.includes("old") && sources.includes("new")) {
        report.error(
          `${where}, node ${vertex.id}`,
          "is reached from both the old and the new path, so the lines tangle; use layout (b)",
        );
      }
    }
  }
}

// ---------------------------------------------------------------- main

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help || options.file === null) {
    console.log(usage);
    process.exitCode = options.help ? 0 : 2;
    return;
  }
  const allowed = new Set([...BRAND_NAMES, ...options.allow.map((word) => word.trim()).filter(Boolean)]);
  const body = (await readBody(options.file)).replaceAll("\r\n", "\n");
  const report = createReport();
  let couldNotCheck = null;

  if (options.title !== null) checkTitle(report, options.title, allowed);

  const lines = body.split("\n");
  const story = splitStory(report, lines);
  let layoutName = null;
  if (story) {
    const lineNumber = (index) => story.first + index + 1;
    const blocks = readBlocks(report, story.storyLines, lineNumber);
    checkSequence(report, blocks);
    const layout = detectLayout(report, blocks);
    layoutName = layout.name;
    if (layout.groups?.length) checkGroups(report, layout.groups, allowed);
    checkCells(report, blocks, allowed);
    checkListen(report, blocks, allowed);

    const charts = layout.charts.map((chart, index) => ({
      ...chart,
      where: chart.role && chart.role !== "only" ? `${chart.role} chart` : `chart ${index + 1}`,
    }));
    charts.forEach((chart) => checkChartSource(report, chart, chart.where));
    if (charts.length > 0) {
      const mermaid = await loadParser();
      if (mermaid.missing) {
        const scriptsDir = path.dirname(fileURLToPath(import.meta.url));
        couldNotCheck =
          `The Mermaid parser could not be installed (${mermaid.missing.message}), so the charts were not parsed. Install it with:\n` +
          `  npm ci --prefix "${scriptsDir}"\n` +
          `If it cannot be installed, publish layout (c) instead of an unparsed chart.`;
      } else {
        for (const chart of charts) {
          await checkChartWithParser(report, mermaid, chart, chart.where, layout.name, allowed);
        }
      }
    }
  }

  const errors = report.problems.filter((problem) => problem.level === "error");
  const warnings = report.problems.filter((problem) => problem.level === "warning");
  for (const problem of [...errors, ...warnings]) {
    console.log(`${problem.level === "error" ? "ERROR" : "warn "}  ${problem.where}: ${problem.message}`);
  }
  if (couldNotCheck) {
    console.log(`CANNOT CHECK  ${couldNotCheck}`);
    process.exitCode = errors.length > 0 ? 1 : 2;
    return;
  }
  const summary = `${errors.length} error(s), ${warnings.length} warning(s)`;
  console.log(errors.length === 0 ? `OK  layout (${layoutName ?? "?"}): ${summary}` : `FAIL  ${summary}`);
  process.exitCode = errors.length === 0 ? 0 : 1;
}

main().catch((error) => {
  console.error(`CANNOT CHECK  ${error.message}\n${usage}`);
  process.exitCode = 2;
});
