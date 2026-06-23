# =============================================================================
# Cross-Agents Symlink Bridge — install-hook.ps1 (Windows)
#
# Installs a git pre-commit hook that automatically runs sync-claude-md.ps1 --staged
# to keep CLAUDE.md symlinks in sync with AGENTS.md on every commit.
#
# If a pre-commit hook already exists, the cross-agents sync logic is appended.
#
# Usage:
#   cd <project-root>
#   powershell -ExecutionPolicy Bypass -File scripts/install-hook.ps1
# =============================================================================
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "🔧 Cross-Agents Symlink Bridge — Hook Installer" -ForegroundColor White
Write-Host ""

try {
    $null = git rev-parse --git-dir 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
} catch {
    Write-Host "❌ ERROR: Not a git repository." -ForegroundColor Red
    exit 1
}

$HookPath = ".git/hooks/pre-commit"
$SyncScript = Join-Path $ScriptDir "sync-claude-md.ps1"

if (-not (Test-Path $SyncScript)) {
    Write-Host "❌ ERROR: sync-claude-md.ps1 not found at $SyncScript" -ForegroundColor Red
    exit 1
}

$Marker = "# === cross-agents-symlink-bridge (auto-generated) ==="

$SyncScriptEscaped = $SyncScript -replace '\\', '\\'

$HookContent = @"

$Marker
# Auto-sync CLAUDE.md symlinks on each commit (staged mode, warnings only).
`$syncScript = "$SyncScriptEscaped"
if (Test-Path `$syncScript) {
    powershell -ExecutionPolicy Bypass -File `$syncScript --Staged
}
# === end cross-agents-symlink-bridge ===
"@

if (Test-Path $HookPath) {
    $existingContent = Get-Content $HookPath -Raw
    if ($existingContent -match [regex]::Escape($Marker)) {
        Write-Host "✅ pre-commit hook already contains cross-agents sync logic." -ForegroundColor Green
    } else {
        Write-Host "⚠️  pre-commit hook exists. Appending cross-agents sync logic..." -ForegroundColor Yellow
        Add-Content -Path $HookPath -Value "`r`n$HookContent"
        Write-Host "✅ Appended to existing hook." -ForegroundColor Green
    }
} else {
    "#!powershell" | Out-File -FilePath $HookPath -Encoding ASCII
    Add-Content -Path $HookPath -Value $HookContent
    Write-Host "✅ Created .git/hooks/pre-commit with cross-agents sync logic." -ForegroundColor Green
}

Write-Host "🔗 Hook installed." -ForegroundColor Cyan
Write-Host ""
Write-Host "   On each commit, CLAUDE.md symlinks will be synced from staged AGENTS.md changes."
