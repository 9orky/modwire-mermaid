import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const lane = process.argv[2];
if (!lane || !["minimum", "latest-11"].includes(lane)) {
  throw new Error("Usage: node compatibility/runner.mjs <minimum|latest-11>");
}
if (process.version !== "v24.17.0") {
  throw new Error(`Compatibility evidence requires Node v24.17.0, received ${process.version}`);
}

const toolchain = join(root, "compatibility", "toolchains", lane);
const require = createRequire(join(toolchain, "package.json"));
const puppeteerEntry = require.resolve("puppeteer");
const puppeteer = (await import(pathToFileURL(puppeteerEntry))).default;
const mermaidPackage = JSON.parse(readFileSync(join(toolchain, "node_modules", "mermaid", "package.json"), "utf8"));
const cliRoot = join(toolchain, "node_modules", "@mermaid-js", "mermaid-cli");
const cliPackage = JSON.parse(readFileSync(join(cliRoot, "package.json"), "utf8"));
const cliEntry = join(cliRoot, cliPackage.bin.mmdc);
const puppeteerPackage = JSON.parse(readFileSync(join(toolchain, "node_modules", "puppeteer", "package.json"), "utf8"));
const catalog = JSON.parse(readFileSync(join(root, "compatibility", "catalog.json"), "utf8"));
const artifacts = join(root, ".compatibility-artifacts", lane);
mkdirSync(artifacts, { recursive: true });
const diagnostics = {
  lane,
  node: process.version,
  mermaid: mermaidPackage.version,
  cli: cliPackage.version,
  puppeteer: puppeteerPackage.version,
  cases: [],
};

const browser = await puppeteer.launch({ headless: true });
diagnostics.browser = await browser.version();
const page = await browser.newPage();
await page.setContent("<!doctype html><html><body></body></html>");
await page.addScriptTag({ path: join(toolchain, "node_modules", "mermaid", "dist", "mermaid.min.js") });
await page.evaluate(() => window.mermaid.initialize({ startOnLoad: false, securityLevel: "strict" }));
for (const fixture of catalog) {
  const source = readFileSync(join(root, fixture.source), "utf8");
  const result = { id: fixture.id, kind: fixture.kind, compiler: fixture.compiler, parsed: false, rendered: false };
  try {
    await page.evaluate(async (value) => {
      await window.mermaid.parse(value);
    }, source);
    result.parsed = true;
    if (fixture.render_required) {
      const output = join(artifacts, `${fixture.id}.svg`);
      execFileSync(process.execPath, [cliEntry, "-i", join(root, fixture.source), "-o", output], {
        encoding: "utf8",
        stdio: "pipe",
      });
      result.rendered = true;
      result.artifact = output.slice(root.length + 1);
    }
  } catch (error) {
    result.error = error instanceof Error ? `${error.name}: ${error.message}` : String(error);
    if (error?.stderr) result.stderr = String(error.stderr);
  }
  diagnostics.cases.push(result);
}
await browser.close();
writeFileSync(join(artifacts, "diagnostics.json"), `${JSON.stringify(diagnostics, null, 2)}\n`);
const failed = diagnostics.cases.filter((item) => !item.parsed || (catalog.find((fixture) => fixture.id === item.id).render_required && !item.rendered));
if (failed.length) {
  throw new Error(`Mermaid compatibility failed for: ${failed.map((item) => item.id).join(", ")}`);
}
