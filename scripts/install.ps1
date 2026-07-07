<#
.SYNOPSIS
  Install aclab skills into a coding agent's skill home (Windows / PowerShell).
.EXAMPLE
  ./scripts/install.ps1 claude
  ./scripts/install.ps1 codex
  $env:SKILLS_TARGET = "C:\skills"; ./scripts/install.ps1 claude
.NOTES
  <agent> = opencode | claude | codex | kiro   (default: opencode)
  SKILLS_TARGET wins over <agent>.
  Layout is FLAT single-level only — every skill installs to <target>\<skill>\SKILL.md.
  One-level skill loaders (Claude Code, and most agent homes) only scan a single
  directory level, so a nested <category>\<skill>\ tree would be invisible to them.
#>
[CmdletBinding()]
param(
  [Parameter(Position = 0)]
  [string]$Agent = "opencode",
  [switch]$WithCli
)
$ErrorActionPreference = "Stop"

$CliRepo = "austinyuch/skills"; $CliTag = "review-cli-v0.15.0"
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
Write-Host "🧭 Layout: flat (single-level)`n"

if (-not (Test-Path $Manifest)) { Write-Error "Manifest not found: $Manifest"; exit 1 }
New-Item -ItemType Directory -Force -Path $Target | Out-Null

$m = Get-Content -Raw -Path $Manifest | ConvertFrom-Json
$installed = 0; $missing = 0

function Copy-Skill([string]$src, [string]$dst, [string]$name) {
  if (-not (Test-Path $src)) { Write-Host "   ⚠️  missing: $name"; $script:missing++; return }
  if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
  Copy-Item -Recurse -Force $src $dst
  Write-Host "   ✅ $name"; $script:installed++
}

foreach ($skill in $m.skills) {
  Copy-Skill (Join-Path $Source $skill) (Join-Path $Target $skill) $skill
}

if ($m.standalone_files) {
  foreach ($row in $m.standalone_files) {
    $src = Join-Path $Source $row.file
    $dst = Join-Path $Target $row.target_path
    if (-not (Test-Path $src)) { Write-Host "   ⚠️  missing file: $($row.file)"; $missing++; continue }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
    Copy-Item -Force $src $dst
    Write-Host "   ✅ $($row.target_path)"; $installed++
  }
}

Write-Host ("`n" + ("━" * 32))
Write-Host "📊 Installed: $installed   ⚠️  Missing: $missing"
Write-Host ("━" * 32)
Write-Host "Skills are now in: $Target"

$CodeReviewDir = Join-Path $Target "code-review"
if (Test-Path $CodeReviewDir) {
  if ($WithCli) {
    if ($IsMacOS) { $os = "darwin"; $ext = "" } elseif ($IsLinux) { $os = "linux"; $ext = "" } else { $os = "windows"; $ext = ".exe" }
    $pa = [System.Runtime.InteropServices.RuntimeInformation]::ProcessArchitecture.ToString().ToLower()
    $arch = if ($pa -eq "arm64") { "arm64" } elseif ($pa -in @("x64", "amd64")) { "amd64" } else { "unsupported" }
    $asset = "review-cli-$os-$arch$ext"
    $dest = Join-Path $CodeReviewDir "scripts"
    if ($arch -eq "unsupported") {
      Write-Host "   ⚠️  unsupported platform for review-cli ($pa)"
    } elseif (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
      Write-Host "   ⚠️  GitHub CLI (gh) not found. Install gh + auth, then:"
      Write-Host "      gh release download $CliTag -R $CliRepo -p $asset -D `"$dest`" --clobber"
    } else {
      Write-Host "⬇️  fetching $asset from $CliRepo@$CliTag (gh) …"
      gh release download $CliTag -R $CliRepo -p $asset -D $dest --clobber
      if ($LASTEXITCODE -eq 0) {
        if (-not $IsWindows) { & chmod +x (Join-Path $dest $asset) }
        Write-Host "   ✅ review-cli installed: $(Join-Path $dest $asset)"
      } else {
        Write-Host "   ⚠️  download failed — retry: gh release download $CliTag -R $CliRepo -p $asset -D `"$dest`" --clobber"
      }
    }
  } else {
    Write-Host 'ℹ️  code-review''s review-cli binary is not bundled — re-run with -WithCli to fetch it (needs gh auth; repo is private). See README "Native binaries".'
  }
}
