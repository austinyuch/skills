<#
.SYNOPSIS
  Install aclab skills into a coding agent's skill home (Windows / PowerShell).
.EXAMPLE
  ./scripts/install.ps1 claude
  ./scripts/install.ps1 codex
  $env:SKILLS_TARGET = "C:\skills"; ./scripts/install.ps1
.NOTES
  <agent> = opencode | claude | codex | kiro   (default: opencode)
  SKILLS_TARGET wins over <agent>. Mirrors scripts/install.sh.
#>
[CmdletBinding()]
param(
  [Parameter(Position = 0)]
  [string]$Agent = "opencode"
)
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Manifest = Join-Path $RepoRoot "skills-manifest.json"
$Source   = Join-Path $RepoRoot "skills"

$homes = @{
  opencode = if ($env:XDG_CONFIG_HOME) { Join-Path $env:XDG_CONFIG_HOME "opencode\skills" } else { Join-Path $HOME ".config\opencode\skills" }
  claude   = Join-Path $HOME ".claude\skills"
  codex    = Join-Path $HOME ".codex\skills"
  kiro     = Join-Path $HOME ".kiro\skills"
}

$Target = $env:SKILLS_TARGET
if (-not $Target) {
  if (-not $homes.ContainsKey($Agent)) {
    Write-Error "Unknown agent: $Agent (use opencode|claude|codex|kiro, or set `$env:SKILLS_TARGET)"
    exit 2
  }
  $Target = $homes[$Agent]
}

Write-Host "📦 aclab skills from: $RepoRoot"
Write-Host ("🤖 Agent: {0}" -f $(if ($env:SKILLS_TARGET) { "custom" } else { $Agent }))
Write-Host "🎯 Target: $Target`n"

if (-not (Test-Path $Manifest)) { Write-Error "Manifest not found: $Manifest"; exit 1 }
New-Item -ItemType Directory -Force -Path $Target | Out-Null

$m = Get-Content -Raw -Path $Manifest | ConvertFrom-Json
$installed = 0; $missing = 0

function Copy-Skill([string]$src, [string]$dst, [string]$name) {
  if (-not (Test-Path $src)) { Write-Host "   ⚠️  missing: $name"; $script:missing++; return }
  if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
  Copy-Item -Recurse -Force $src $dst
  Write-Host "   ✅ $name"; $script:installed++
}

foreach ($group in @("families", "categories")) {
  if (-not $m.$group) { continue }
  foreach ($key in $m.$group.PSObject.Properties.Name) {
    foreach ($skill in $m.$group.$key.skills) {
      Copy-Skill (Join-Path $Source (Join-Path $key $skill)) (Join-Path $Target $skill) $skill
    }
  }
}

if ($m.standalone_files) {
  foreach ($row in $m.standalone_files) {
    $src = Join-Path $Source (Join-Path $row.category $row.target_path)
    $dst = Join-Path $Target $row.file
    if (-not (Test-Path $src)) { Write-Host "   ⚠️  missing file: $($row.file)"; $missing++; continue }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
    Copy-Item -Force $src $dst
    Write-Host "   ✅ $($row.file)"; $installed++
  }
}

Write-Host ("`n" + ("━" * 32))
Write-Host "📊 Installed: $installed   ⚠️  Missing: $missing"
Write-Host ("━" * 32)
Write-Host "Skills are now in: $Target"
if (Test-Path (Join-Path $Target "code-review")) {
  Write-Host 'ℹ️  code-review needs a review-cli-<os>-<arch> binary (not bundled) — see README "Native binaries".'
}
