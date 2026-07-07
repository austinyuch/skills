# =============================================================================
# Cross-Agents Symlink Bridge — sync-claude-md.ps1 (Windows)
#
# Recursively scans for AGENTS.md files and creates CLAUDE.md -> AGENTS.md
# symlinks in each directory. Supports full-scan and git-diff modes.
#
# .gitignore policy:
#   - Rewrite a dedicated managed section for generated CLAUDE.md symlinks
#   - Do not git-add generated symlinks
# =============================================================================
param(
    [switch]$Staged
)

$ErrorActionPreference = "Stop"

$Created = 0
$SkippedCorrect = 0
$SkippedConflict = 0
$SectionBegin = "# cross-agents symlink bridge: claude-md begin"
$SectionEnd = "# cross-agents symlink bridge: claude-md end"
$ManagedClaude = New-Object System.Collections.Generic.List[string]

function Add-UniqueClaude([string]$Entry) {
    if (-not $ManagedClaude.Contains($Entry)) {
        $ManagedClaude.Add($Entry) | Out-Null
    }
}

function Rewrite-GitignoreSection([string]$BeginMarker, [string]$EndMarker, [string[]]$Entries) {
    if (-not (Test-Path ".gitignore")) {
        New-Item -Path ".gitignore" -ItemType File | Out-Null
    }

    $lines = @(Get-Content ".gitignore" -ErrorAction SilentlyContinue)
    $filtered = New-Object System.Collections.Generic.List[string]
    $skip = $false

    foreach ($line in $lines) {
        if ($line -eq $BeginMarker) {
            $skip = $true
            continue
        }
        if ($line -eq $EndMarker) {
            $skip = $false
            continue
        }
        if (-not $skip) {
            $filtered.Add($line) | Out-Null
        }
    }

    while ($filtered.Count -gt 0 -and [string]::IsNullOrWhiteSpace($filtered[$filtered.Count - 1])) {
        $filtered.RemoveAt($filtered.Count - 1)
    }

    if ($Entries.Count -gt 0) {
        if ($filtered.Count -gt 0) {
            $filtered.Add("") | Out-Null
        }
        $filtered.Add($BeginMarker) | Out-Null
        foreach ($entry in $Entries) {
            $filtered.Add($entry) | Out-Null
        }
        $filtered.Add($EndMarker) | Out-Null
    }

    Set-Content -Path ".gitignore" -Value $filtered -Encoding utf8
}

function Test-IsManagedAgentSubtree([string]$RelativePath) {
    return $RelativePath -match '^(\.git|node_modules|\.claude|\.kiro|\.codex)([/\\]|$)'
}

function Collect-ManagedClaudeSymlinks {
    $ManagedClaude.Clear()
    $claudeFiles = @(Get-ChildItem -Path "." -Name "CLAUDE.md" -Recurse -File |
        Where-Object { -not (Test-IsManagedAgentSubtree $_) } |
        Sort-Object)

    foreach ($claudeFile in $claudeFiles) {
        $normalized = $claudeFile -replace '^\.[/\\]', ''
        $claudeItem = Get-Item -Path $normalized -ErrorAction SilentlyContinue
        if ($claudeItem -and ($claudeItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
            $currentTarget = (cmd /c "dir /AL `"$normalized`" 2>nul" | Select-String "\[(.*)\]").Matches.Groups[1].Value
            if ($currentTarget -eq "AGENTS.md") {
                Add-UniqueClaude($normalized)
            }
        }
    }
}

Write-Host "🔍 Scanning $($(if ($Staged) { 'staged' } else { 'full' })) directories for AGENTS.md..." -ForegroundColor White

$AgentsFiles = @()
if ($Staged) {
    try {
        $null = git rev-parse --git-dir 2>$null
        if ($LASTEXITCODE -ne 0) { throw }
    } catch {
        Write-Host "❌ ERROR: Not a git repository. --staged mode requires git." -ForegroundColor Red
        exit 1
    }

    $diffOutput = git diff --cached --name-only --diff-filter=ACMR 2>$null
    if ($diffOutput) {
        foreach ($line in ($diffOutput -split "`n")) {
            if ($line -match '(?:^|/)AGENTS\.md$') {
                $AgentsFiles += $line.Trim()
            }
        }
    }
} else {
    $AgentsFiles = @(Get-ChildItem -Path "." -Name "AGENTS.md" -Recurse -File |
        Where-Object { -not (Test-IsManagedAgentSubtree $_) } |
        Sort-Object)
}

if ($AgentsFiles.Count -eq 0) {
    Write-Host "   No AGENTS.md files found."

    if ($Staged) {
        Write-Host "   Preserving managed CLAUDE.md entries from current symlink state."
        Collect-ManagedClaudeSymlinks
        Rewrite-GitignoreSection $SectionBegin $SectionEnd $ManagedClaude.ToArray()
        exit 0
    }

    Rewrite-GitignoreSection $SectionBegin $SectionEnd @()
    exit 0
}

Write-Host "   Found $($AgentsFiles.Count) AGENTS.md file(s)"
Write-Host ""

foreach ($agentsFile in $AgentsFiles) {
    $dir = Split-Path -Parent $agentsFile
    if (-not $dir) { $dir = "." }

    $claudeFile = Join-Path $dir "CLAUDE.md"
    $claudeFile = $claudeFile -replace '^\.[/\\]', ''
    $claudeItem = Get-Item -Path $claudeFile -ErrorAction SilentlyContinue

    if ($claudeItem -and ($claudeItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        $currentTarget = (cmd /c "dir /AL `"$claudeFile`" 2>nul" | Select-String "\[(.*)\]").Matches.Groups[1].Value
        if ($currentTarget -eq "AGENTS.md") {
            Write-Host "   ✅ $claudeFile -> AGENTS.md (correct)" -ForegroundColor Green
            Add-UniqueClaude($claudeFile)
            $SkippedCorrect++
            continue
        }

        Write-Host "   ⚠️  $claudeFile points elsewhere, replacing..." -ForegroundColor Yellow
        Remove-Item -Path $claudeFile -Force
    } elseif ($claudeItem) {
        Write-Host "   ⚠️  $claudeFile is a real file — skipping (not overwriting)" -ForegroundColor Yellow
        $SkippedConflict++
        continue
    }

    Push-Location $dir
    try {
        $result = cmd /c "mklink `"CLAUDE.md`" `"AGENTS.md`" 2>&1"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   ❌ Failed to create symlink for $claudeFile" -ForegroundColor Red
            Write-Host "   $result"
            continue
        }
    } finally {
        Pop-Location
    }

    Write-Host "   🔗 Created: $claudeFile -> AGENTS.md" -ForegroundColor Cyan
    Add-UniqueClaude($claudeFile)
    $Created++
}

Collect-ManagedClaudeSymlinks
Rewrite-GitignoreSection $SectionBegin $SectionEnd $ManagedClaude.ToArray()

Write-Host ""
Write-Host "   Created: $Created  |  Skipped (correct): $SkippedCorrect  |  Skipped (conflict): $SkippedConflict"
