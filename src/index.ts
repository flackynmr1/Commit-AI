#!/usr/bin/env bun

import "dotenv/config";
import { Command } from "commander";
import Groq from "groq-sdk";
import { simpleGit, type SimpleGit } from "simple-git";
import * as readline from "node:readline/promises";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import chalk from "chalk";

const program = new Command();
const git: SimpleGit = simpleGit();

const origin = chalk.bold.magenta("[Commit-AI]");

const log = {
  info: (msg: string) =>
    console.log(`${origin} ${chalk.blue("[Info]")}: ${msg}`),
  success: (msg: string) =>
    console.log(`${origin} ${chalk.green("[Success]")}: ${msg}`),
  warn: (msg: string) =>
    console.log(`${origin} ${chalk.yellow("[Warn]")}: ${msg}`),
  error: (msg: string) =>
    console.error(`${origin} ${chalk.red("[Error]")}: ${msg}`),
  ai: (msg: string) => console.log(`${origin} ${chalk.cyan("[AI]")}: ${msg}`),
};

async function getIgnorePatterns(): Promise<string[]> {
  const defaultExcludes = [
    "package-lock.json",
    "bun.lockb",
    "yarn.lock",
    "pnpm-lock.yaml",
    "node_modules",
    "dist",
    "*.log",
  ];
  try {
    const gitignorePath = join(process.cwd(), ".gitignore");
    const content = await readFile(gitignorePath, "utf-8");
    const gitignoreLines = content
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter((l) => l && !l.startsWith("#"));
    return Array.from(new Set([...defaultExcludes, ...gitignoreLines])).map(
      (p) => `:(exclude)${p}`,
    );
  } catch {
    return defaultExcludes.map((p) => `:(exclude)${p}`);
  }
}

program
  .name("commit-ai")
  .description("AI-powered git analysis and auto-committer")
  .version("1.2.4")
  .option("-c, --commit", "enable commit mode")
  .option("-y, --yes", "skip confirmation prompt");

program.action(async (options) => {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) {
    log.error("GROQ_API_KEY is missing.");
    process.exit(1);
  }

  const groq = new Groq({ apiKey });

  try {
    const isRepo = await git.checkIsRepo();
    if (!isRepo) {
      log.error("Not a Git repository.");
      return;
    }

    log.info("Analyzing modified files...");
    await git.add(["--intent-to-add", "."]);

    const excludePatterns = await getIgnorePatterns();
    let diff = "";
    try {
      diff = await git.diff(["HEAD", "--", ".", ...excludePatterns]);
    } catch {
      const EMPTY_TREE_HASH = "4b825dc642cb6eb9a060e54bf8d69288fbee4904";
      diff = await git.diff([EMPTY_TREE_HASH, "--", ".", ...excludePatterns]);
    }

    if (!diff || diff.trim() === "") {
      log.success("No changes detected.");
      return;
    }

    const prompt = `
      Analyze this Git diff and provide a professional report.
      1. Provide a bulleted "REPORT" of technical changes.
      2. Provide a "COMMIT_MESSAGE" following these strict rules:
      3. Provide a "COMMIT_MESSAGE" in "type: description" format.
      
      STRICT RULES:
      - Format: type: description
      - NO BRACKETS (e.g., use "feat: message" NOT "[feat]: message")
      - NO SCOPES (e.g., use "feat: message" NOT "feat(scope): message")
      - Use imperative mood.
      - No period at the end.

      Diff:
      ${diff.substring(0, 5000)}
    `;

    log.ai("Generating commit suggestion...");

    const chatCompletion = await groq.chat.completions.create({
      messages: [
        {
          role: "system",
          content:
            "You are commit-ai. Only return the requested REPORT and COMMIT_MESSAGE sections.",
        },
        { role: "user", content: prompt },
      ],
      model: "llama-3.1-8b-instant",
      temperature: 0.1,
    });

    const response = chatCompletion.choices[0]?.message?.content || "";

    // --- ROBUST PARSING WITH REGEX ---
    const reportMatch = response.match(
      /REPORT:?([\s\S]*?)(?=COMMIT_MESSAGE|$)/i,
    );
    const commitMatch = response.match(/COMMIT_MESSAGE:?([\s\S]*?)$/i);

    let report = (reportMatch?.[1] || "Minor updates.")
      .replace(/\*\*/g, "")
      .replace(/REPORT:?/gi, "")
      .trim();

    let title = (
      (commitMatch?.[1] || "feat: update files")
        .replace(/\*\*/g, "")
        .split("\n")[0] ?? "feat: update files"
    )
      .replace(/^\[(\w+)\]:?\s*/, "$1: ")
      .replace(/^(\w+)\([^)]+\):?\s*/, "$1: ")
      .replace(/\.$/, "")
      .trim();

    // Ensure title has the colon format
    if (!title.includes(":")) {
      title = `feat: ${title}`;
    }

    console.log(`\n${chalk.bold.cyan("─── AI SUGGESTION ───")}`);
    console.log(chalk.white(`REPORT:\n${report}`));
    console.log(chalk.white(`\nCOMMIT_MESSAGE: ${title}`));
    console.log(`${chalk.bold.cyan("─────────────────────")}\n`);

    if (options.commit) {
      let shouldCommit = options.yes;
      if (!options.yes) {
        const rl = readline.createInterface({
          input: process.stdin,
          output: process.stdout,
        });
        const confirm = await rl.question(
          `${origin} ${chalk.yellow("[Prompt]")}: Use this commit message? (y/n): `,
        );
        if (confirm.toLowerCase() === "y") shouldCommit = true;
        rl.close();
      }

      if (shouldCommit) {
        await git.add(".");
        await git.commit([title, report]);
        log.success(`Changes committed: ${chalk.dim(title)}`);
      } else {
        log.warn("Commit aborted.");
      }
    } else {
      log.info("Run with '-c' to perform the actual commit.");
    }
  } catch (error: any) {
    log.error(`Critical Failure: ${error.message}`);
  }
});

async function main() {
  await program.parseAsync(process.argv);
}

main();
