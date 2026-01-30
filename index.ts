#!/usr/bin/env bun

import * as dotenv from "dotenv";
import { Command } from "commander";
import Groq from "groq-sdk";
import { simpleGit, type SimpleGit } from "simple-git";
import * as readline from "node:readline/promises";

dotenv.config();

const program = new Command();
const git: SimpleGit = simpleGit();
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

program
  .name("commit-ai")
  .description("AI-powered git analysis and auto-committer")
  .version("1.2.2")
  .option("-c, --commit", "enable commit mode (prompts to commit changes)")
  .option("-y, --yes", "skip confirmation prompt (requires -c)");

program.action(async (options) => {
  const apiKey = process.env.GROQ_API_KEY;

  if (!apiKey) {
    console.error("❌ Error: GROQ_API_KEY is not set.");
    process.exit(1);
  }

  const groq = new Groq({ apiKey });

  try {
    const isRepo = await git.checkIsRepo();
    if (!isRepo) {
      console.error("❌ Not a Git repo.");
      return;
    }

    console.log("🔍 commit-ai is scanning your changes...");
    await git.add(["--intent-to-add", "."]);

    const excludePatterns = [
      ":!package-lock.json",
      ":!bun.lockb",
      ":!yarn.lock",
      ":!pnpm-lock.yaml",
      ":!node_modules",
      ":!dist",
      ":!*.log",
    ];

    let diff: string = "";
    try {
      diff = await git.diff(["HEAD", "--", ".", ...excludePatterns]);
    } catch (e) {
      const EMPTY_TREE_HASH = "4b825dc642cb6eb9a060e54bf8d69288fbee4904";
      diff = await git.diff([EMPTY_TREE_HASH, "--", ".", ...excludePatterns]);
    }

    if (!diff || diff.trim() === "") {
      console.log("✅ No changes found.");
      return;
    }

    const MAX_CHAR = 5000;
    if (diff.length > MAX_CHAR) {
      diff = diff.substring(0, MAX_CHAR) + "\n\n...[TRUNCATED]...";
    }

    const prompt = `
      Analyze this Git diff.
      1. Provide a bulleted "REPORT" of changes.
      2. Provide a "COMMIT_MESSAGE" following Conventional Commits.
      
      STRICT RULES:
      - Do NOT use a scope (e.g., "feat: description").
      - Use imperative mood ("add" not "added").
      - No period at the end of the COMMIT_MESSAGE.

      Response Format:
      REPORT:
      - detail
      COMMIT_MESSAGE:
      type: description

      Diff:
      ${diff}
    `;

    console.log("🚀 AI is drafting your professional report...");

    const chatCompletion = await groq.chat.completions.create({
      messages: [
        {
          role: "system",
          content: "You are commit-ai, a professional Git assistant.",
        },
        { role: "user", content: prompt },
      ],
      model: "llama-3.1-8b-instant",
      temperature: 0.2,
    });

    const response = chatCompletion.choices[0]?.message?.content || "";

    // Parse the Response
    const reportPart =
      response
        .split(/COMMIT_MESSAGE:/i)[0]
        ?.replace(/REPORT:/i, "")
        .trim() || "";
    let titlePart = response.split(/COMMIT_MESSAGE:/i)[1]?.trim() || "";

    // Cleanup title (remove scope/period if AI failed instructions)
    titlePart = titlePart
      .replace(/^(\w+)\s*\([^)]+\):/, "$1:")
      .replace(/\.$/, "");

    // Combine for Git (Title \n\n Body)
    const fullCommitMessage = `${titlePart}\n\n${reportPart}`;

    console.log("\n--- 📝 commit-ai: PROFESSIONAL REPORT ---");
    console.log(response);
    console.log("------------------------------------------\n");

    if (options.commit && titlePart) {
      let shouldCommit = false;
      if (options.yes) {
        shouldCommit = true;
      } else {
        const confirm = await rl.question(
          `🤔 Commit with message: "${titlePart}"? (y/n): `,
        );
        if (confirm.toLowerCase() === "y") shouldCommit = true;
      }

      if (shouldCommit) {
        await git.add(".");
        // We pass the array to commit to handle the multi-line body correctly
        await git.commit([titlePart, reportPart]);
        console.log("✅ Changes committed with full report!");
      }
    } else if (!options.commit) {
      console.log("💡 Note: Run with '-c' to enable commit mode.");
    }
  } catch (error: any) {
    console.error("❌ commit-ai Error:", error.message);
  } finally {
    rl.close();
  }
});

program.parse(process.argv);
