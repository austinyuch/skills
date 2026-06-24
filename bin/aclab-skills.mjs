#!/usr/bin/env node
// aclab-skills — cross-platform skill installer (Node, zero deps).
//
//   npx  -y github:austinyuch/skills <agent>
//   bunx    github:austinyuch/skills <agent>
//   node bin/aclab-skills.mjs <agent>            (from a checkout)
//
// <agent> = opencode | claude | codex | kiro   (default: opencode)
// Override the destination with --target <dir> or SKILLS_TARGET=<dir>.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const AGENT_HOMES = {
  opencode: () => process.env.XDG_CONFIG_HOME
    ? path.join(process.env.XDG_CONFIG_HOME, 'opencode', 'skills')
    : path.join(os.homedir(), '.config', 'opencode', 'skills'),
  claude: () => path.join(os.homedir(), '.claude', 'skills'),
  codex:  () => path.join(os.homedir(), '.codex', 'skills'),
  kiro:   () => path.join(os.homedir(), '.kiro', 'skills'),
};

function usage(code = 0) {
  console.log(`aclab-skills — install aclab skills into a coding agent's skill home

Usage:
  aclab-skills <agent> [--target <dir>] [--dry-run]
  <agent> = opencode | claude | codex | kiro   (default: opencode)

Examples:
  npx -y github:austinyuch/skills claude
  bunx github:austinyuch/skills codex
  SKILLS_TARGET=/custom/path npx -y github:austinyuch/skills

Env:  SKILLS_TARGET overrides the destination (wins over <agent>).`);
  process.exit(code);
}

// Find the repo data root (holds skills-manifest.json) by walking up from this file.
function findDataRoot(start) {
  let dir = start;
  for (let i = 0; i < 8; i++) {
    if (fs.existsSync(path.join(dir, 'skills-manifest.json')) &&
        fs.existsSync(path.join(dir, 'skills'))) return dir;
    const up = path.dirname(dir);
    if (up === dir) break;
    dir = up;
  }
  return null;
}

function main() {
  const argv = process.argv.slice(2);
  let agent = null, target = process.env.SKILLS_TARGET || null, dryRun = false;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '-h' || a === '--help') usage(0);
    else if (a === '--dry-run') dryRun = true;
    else if (a === '--target') target = argv[++i];
    else if (a.startsWith('--target=')) target = a.slice('--target='.length);
    else if (!a.startsWith('-') && !agent) agent = a;
  }
  agent = agent || 'opencode';
  if (!target && !(agent in AGENT_HOMES)) {
    console.error(`✖ Unknown agent: ${agent} (use opencode|claude|codex|kiro, or --target)`);
    process.exit(2);
  }
  if (!target) target = AGENT_HOMES[agent]();

  const root = findDataRoot(__dirname);
  if (!root) {
    console.error('✖ Could not locate skills-manifest.json / skills/. Run from a checkout or via `npx github:austinyuch/skills`.');
    process.exit(1);
  }
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'skills-manifest.json'), 'utf8'));
  const source = path.join(root, 'skills');

  console.log(`📦 aclab skills from: ${root}`);
  console.log(`🤖 Agent: ${target === process.env.SKILLS_TARGET ? 'custom' : agent}`);
  console.log(`🎯 Target: ${target}${dryRun ? '  (dry-run)' : ''}\n`);
  if (!dryRun) fs.mkdirSync(target, { recursive: true });

  let installed = 0, missing = 0;
  const copyDir = (src, dst, name) => {
    if (!fs.existsSync(src)) { console.log(`   ⚠️  missing: ${name}`); missing++; return; }
    if (!dryRun) fs.cpSync(src, dst, { recursive: true });
    console.log(`   ✅ ${name}`); installed++;
  };

  for (const group of ['families', 'categories']) {
    for (const [key, val] of Object.entries(manifest[group] || {})) {
      for (const skill of val.skills || []) {
        copyDir(path.join(source, key, skill), path.join(target, skill), skill);
      }
    }
  }
  for (const row of manifest.standalone_files || []) {
    const src = path.join(source, row.category, row.target_path);
    const dst = path.join(target, row.file);
    if (!fs.existsSync(src)) { console.log(`   ⚠️  missing file: ${row.file}`); missing++; continue; }
    if (!dryRun) { fs.mkdirSync(path.dirname(dst), { recursive: true }); fs.copyFileSync(src, dst); }
    console.log(`   ✅ ${row.file}`); installed++;
  }

  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`📊 ${dryRun ? 'Would install' : 'Installed'}: ${installed}   ⚠️  Missing: ${missing}`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`Skills ${dryRun ? 'would be' : 'are now'} in: ${target}`);
  if (fs.existsSync(path.join(target, 'code-review'))) {
    console.log(`ℹ️  code-review needs a review-cli-<os>-<arch> binary (not bundled) — see README "Native binaries".`);
  }
}

main();
