# Commit-AI 🤖

<div>

**Professionalize your Git history with AI-generated Conventional Commits.**

[![Version](https://img.shields.io/badge/version-1.3.2-magenta?style=flat-square)](https://github.com/NeelFrostrain/commit-ai)
[![Node.js](https://img.shields.io/badge/node-%3E%3D18.0.0-339933?style=flat-square&logo=node.js&logoColor=white)](https://nodejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-%3E%3D5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Groq](https://img.shields.io/badge/Groq-AI-cyan?style=flat-square)](https://groq.com)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

Stop writing "fixed stuff" and start writing commits that tell a story.

</div>

---

## 📖 About Commit-AI

**Commit-AI** was born out of a common developer frustration: the "Lazy Commit" syndrome. We've all written messages like `fixed bug`, `update index.ts`, or the dreaded `..........`.

This tool transforms raw, technical code changes into **human-readable, professional documentation**. By leveraging the **Llama 3.1 8B** model via Groq's ultra-fast inference engine, Commit-AI acts as a bridge between your terminal and your project's history.

### 🧠 The Logic

The tool doesn't just look at filenames; it reads the **Git Diff**. It understands:

- **Intent:** Are you adding a feature or fixing a regression?
- **Impact:** What specific logic changed within the functions?
- **Context:** It filters out noise like `package-lock.json` or `node_modules` to focus on your actual contributions.

### 🏗️ Built With

- **[Bun](https://www.google.com/search?q=https://bun.sh/):** High-performance runtime and bundler.
- **[Groq SDK](https://www.google.com/search?q=https://groq.com/):** Lightning-fast AI inference.
- **[Commander.js](https://www.google.com/search?q=https://github.com/tj/commander.js/):** CLI interface and flag management.
- **[Simple-Git](https://www.google.com/search?q=https://github.com/steveukx/git-js):** Local Git interaction layer.
- **[Chalk](https://www.google.com/search?q=https://github.com/chalk/chalk):** Beautiful, colored terminal logs.

---

## ⚡ Quick Start

### 1️⃣ Installation

Install the tool globally using npm:

```bash
npm i @neelfrostrain/commit-ai -g

```

### 2️⃣ Get your API Key

1. Visit [Groq Cloud Console](https://www.google.com/search?q=https://console.groq.com/keys).
2. Create a new API Key and copy it.

### 3️⃣ Configure Environment (Windows)

To use Commit-AI, you must set your `GROQ_API_KEY` as an environment variable. Choose your preferred terminal below:

#### **Option A: Command Prompt (CMD)**

Run this command (replace `your_key_here` with your actual key):

```cmd
setx GROQ_API_KEY "your_key_here"

```

#### **Option B: PowerShell**

Run this command:

```powershell
[System.Environment]::SetEnvironmentVariable('GROQ_API_KEY', 'your_key_here', 'User')

```

> **⚠️ Important:** You **must restart** your terminal (CMD, PowerShell, or VS Code) after running these commands for the changes to take effect.

---

## ✨ Features

| Feature                   | Description                                                      |
| ------------------------- | ---------------------------------------------------------------- |
| **🧠 Deep Diff Analysis** | Understands code logic, not just file metadata.                  |
| **📝 Conventional Style** | Strictly follows the `type: description` standard.               |
| **📊 Technical Reports**  | Generates a detailed bulleted summary for the commit body.       |
| **🛡️ Smart Filtering**    | Respects `.gitignore` and ignores heavy lockfiles automatically. |
| **🚀 Sub-second Speed**   | Powered by Groq for nearly instant commit generation.            |

---

## 📖 Usage

### Command Flags

| Flag        | Short | Description                                             |
| ----------- | ----- | ------------------------------------------------------- |
| `--commit`  | `-c`  | Performs the `git commit` after generating the message. |
| `--yes`     | `-y`  | Skips the confirmation prompt (Auto-pilot).             |
| `--version` | `-v`  | Displays the current version.                           |
| `--help`    | `-h`  | Displays the help menu.                                 |

### Example Workflow

1. **Stage your changes:**

```bash
git add .

```

2. **Run Commit-AI:**

```bash
commit-ai -c

```

3. **Review & Confirm:** The AI will show you a report and the suggested message. Type `y` to finalize!

---

## ⚙️ Standards & Security

### Conventional Commit Types

Commit-AI automatically categorizes your work into:

- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation updates
- `style`: Formatting/Linting
- `refactor`: Code restructuring
- `chore`: Build tasks/dependencies

### 🛡️ Privacy

- **Local Keys:** Your API key stays on your machine and is never shared.
- **Diffs Only:** Only the `git diff` of your **staged** files is sent to the AI for processing. No other system data is accessed.

---

## 📄 License

MIT © [Neel Frostrain](https://www.google.com/search?q=https://github.com/NeelFrostrain)

---
