# =============================================================================
# Cross-Agents Symlink Bridge — init.ps1 (Windows)
#
# Hybrid initialization for repo-local agent surfaces:
#   1. Keep .claude/, .kiro/, .codex/ as real directories
#   2. Junction only <agent>\skills -> ..\.agents\skills
#   3. Manage <agent>\specs via explicit mode: sync | symlink | skip
#   4. Leave all other config / permission surfaces untouched so an existing
#      sync workflow can continue owning them
#   5. Recursively create CLAUDE.md -> AGENTS.md symlinks
#   6. Rewrite managed .gitignore sections to avoid stale bridge entries
# =============================================================================
param(
    [ValidateSet("sync", "symlink", "skip")]
    [string]$SpecsMode = "sync"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Get-Location).Path

# Canonical skill source lives under the workspace agent home (.agents\skills),
# NOT a repo-root skills\. A top-level skills\ is only a convention for GLOBAL
# config homes (e.g. ~/.config/opencode/, ~/.claude/). Inside a repo, skills are
# owned by .agents\skills and bridged into .claude/.kiro/.codex — mirroring how
# specs are owned by .agents\specs.
$SourceSkills = ".agents\skills"
$SourceSpecs = ".agents\specs"
$SkillsLinkSource = "..\.agents\skills"
$SpecsLinkSource = "..\.agents\specs"
$AgentRoots = @(".claude", ".kiro", ".codex")
$BridgeBegin = "# cross-agents symlink bridge: managed begin"
$BridgeEnd = "# cross-agents symlink bridge: managed end"
$ManagedLinks = New-Object System.Collections.Generic.List[string]

Write-Host "🔍 Cross-Agents Symlink Bridge — Initialization" -ForegroundColor White
Write-Host "   Project root: $ProjectRoot"
Write-Host "   Skills mode: symlink-only"
Write-Host "   Specs mode:  $SpecsMode"
Write-Host ""

$IsGit = $true
try {
    $null = git rev-parse --git-dir 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
} catch {
    Write-Host "⚠️  WARNING: Not a git repository. Paths will be created, but .gitignore won't be managed." -ForegroundColor Yellow
    $IsGit = $false
}

function Add-UniqueManagedLink([string]$Entry) {
    if (-not $ManagedLinks.Contains($Entry)) {
        $ManagedLinks.Add($Entry) | Out-Null
    }
}

function Backup-Path([string]$TargetPath) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupPath = "$TargetPath.cross-agents-backup-$stamp"
    Move-Item -LiteralPath $TargetPath -Destination $backupPath
    Write-Host "   📦 Backed up $TargetPath -> $backupPath" -ForegroundColor Cyan
}

function Ensure-AgentRoot([string]$RootPath) {
    $item = Get-Item -LiteralPath $RootPath -ErrorAction SilentlyContinue
    if ($item -and (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -or -not $item.PSIsContainer)) {
        Backup-Path $RootPath
        Write-Host "   ⚠️  Legacy root bridge for $RootPath was backed up; non-skill config is not auto-copied. Re-run your normal sync flow if you need repo-local settings restored." -ForegroundColor Yellow
    }

    if (-not (Test-Path $RootPath -PathType Container)) {
        New-Item -Path $RootPath -ItemType Directory | Out-Null
        Write-Host "   ℹ️  Created real agent root $RootPath/" -ForegroundColor Cyan
    }
}

function Get-LinkTarget([string]$TargetPath) {
    $match = (cmd /c "dir /AL `"$TargetPath`" 2>nul" | Select-String "\[(.*)\]").Matches
    if ($match.Count -gt 0) {
        return $match[0].Groups[1].Value
    }
    return ""
}

function Resolve-NormalizedPath([string]$BasePath, [string]$PathValue) {
    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return ""
    }

    $full = if ([System.IO.Path]::IsPathRooted($PathValue)) {
        $PathValue
    } else {
        [System.IO.Path]::Combine($BasePath, $PathValue)
    }

    return [System.IO.Path]::GetFullPath($full)
}

function Resolve-ExpectedLinkTarget([string]$TargetPath, [string]$LinkSource) {
    $parent = Split-Path -Parent $TargetPath
    return Resolve-NormalizedPath $parent $LinkSource
}

function Rewrite-GitignoreSection([string]$BeginMarker, [string]$EndMarker, [string[]]$Entries) {
    if (-not $IsGit) {
        return
    }

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
    while ($filtered.Count -gt 0 -and [string]::IsNullOrWhiteSpace($filtered[0])) {
        $filtered.RemoveAt(0)
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

function Sync-Directory([string]$SourcePath, [string]$TargetPath) {
    New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null

    $RoboArgs = @("`"$SourcePath`"", "`"$TargetPath`"", "/MIR", "/NP", "/R:3", "/W:1", "/NJH", "/NJS")
    $Process = Start-Process -FilePath "robocopy.exe" -ArgumentList $RoboArgs -NoNewWindow -PassThru -Wait
    if ($Process.ExitCode -ge 8) {
        throw "Robocopy failed with exit code $($Process.ExitCode)"
    }
}

function Ensure-JunctionTarget([string]$TargetPath, [string]$LinkSource, [string]$DisplaySource) {
    $parent = Split-Path -Parent $TargetPath
    $expectedTarget = Resolve-ExpectedLinkTarget $TargetPath $LinkSource
    if ($parent -and -not (Test-Path $parent -PathType Container)) {
        New-Item -Path $parent -ItemType Directory -Force | Out-Null
    }

    $item = Get-Item -LiteralPath $TargetPath -ErrorAction SilentlyContinue
    if ($item -and ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        $currentTarget = Get-LinkTarget $TargetPath
        if ((Resolve-NormalizedPath $parent $currentTarget) -eq $expectedTarget) {
            Write-Host "   ✅ $TargetPath -> $DisplaySource (already correct)" -ForegroundColor Green
            Add-UniqueManagedLink($TargetPath)
            return
        }

        Write-Host "   ⚠️  $TargetPath points to '$currentTarget', replacing with '$DisplaySource'..." -ForegroundColor Yellow
        cmd /c "rmdir `"$TargetPath`"" | Out-Null
    } elseif ($item) {
        Backup-Path $TargetPath
    }

    $result = cmd /c "mklink /j `"$TargetPath`" `"$LinkSource`" 2>&1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ❌ Failed to create junction for $TargetPath" -ForegroundColor Red
        Write-Host "   $result"
        Write-Host "   If source and target are on different drives, use: cmd /c mklink /d $TargetPath $LinkSource"
        Write-Host "   (Requires Developer Mode enabled in Windows Settings)"
        exit 1
    }

    Write-Host "   🔗 Created: $TargetPath -> $DisplaySource" -ForegroundColor Cyan
    Add-UniqueManagedLink($TargetPath)
}

function Handle-SpecsTarget([string]$RootPath) {
    $targetPath = Join-Path $RootPath "specs"

    switch ($SpecsMode) {
        "skip" {
            Write-Host "   ℹ️  Leaving $targetPath untouched (specs mode: skip)" -ForegroundColor Cyan
        }
        "sync" {
            if (-not (Test-Path $SourceSpecs -PathType Container)) {
                Write-Host "   ⚠️  Source $SourceSpecs not found, skipping $targetPath sync" -ForegroundColor Yellow
                return
            }

            $item = Get-Item -LiteralPath $targetPath -ErrorAction SilentlyContinue
            if ($item -and (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -or -not $item.PSIsContainer)) {
                Backup-Path $targetPath
            }

            Sync-Directory $SourceSpecs $targetPath
            Write-Host "   🔄 Synced: $targetPath <= $SourceSpecs" -ForegroundColor Green
        }
        "symlink" {
            if (-not (Test-Path $SourceSpecs -PathType Container)) {
                Write-Host "   ⚠️  Source $SourceSpecs not found, skipping $targetPath symlink" -ForegroundColor Yellow
                return
            }

            $item = Get-Item -LiteralPath $targetPath -ErrorAction SilentlyContinue
            if ($item -and $item.PSIsContainer -and -not ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
                Write-Host "   📥 Merging existing $targetPath into $SourceSpecs before linking" -ForegroundColor Cyan
                Sync-Directory $targetPath $SourceSpecs
                Remove-Item -LiteralPath $targetPath -Recurse -Force
            } elseif ($item -and -not ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
                Backup-Path $targetPath
            }

            Ensure-JunctionTarget $targetPath $SpecsLinkSource $SourceSpecs
        }
    }
}

Write-Host "── Step 1: Normalize agent roots ─────────────────" -ForegroundColor White
Write-Host ""
foreach ($root in $AgentRoots) {
    Ensure-AgentRoot $root
}

Write-Host ""
Write-Host "── Step 2: Repo-local skills symlinks ────────────" -ForegroundColor White
Write-Host ""

if (-not (Test-Path $SourceSkills -PathType Container)) {
    New-Item -Path $SourceSkills -ItemType Directory -Force | Out-Null
    Write-Host "   ℹ️  Created canonical skills source $SourceSkills/ (workspace agent home)" -ForegroundColor Cyan
}

foreach ($root in $AgentRoots) {
    Ensure-JunctionTarget (Join-Path $root "skills") $SkillsLinkSource $SourceSkills
}

Write-Host ""
Write-Host "── Step 3: Repo-local specs ($SpecsMode) ─────────" -ForegroundColor White
Write-Host ""

foreach ($root in $AgentRoots) {
    Handle-SpecsTarget $root
}

Write-Host ""
Write-Host "── Step 4: CLAUDE.md symlinks (recursive) ───────" -ForegroundColor White
Write-Host ""

$ClaudeSyncScript = Join-Path $ScriptDir "sync-claude-md.ps1"
if (Test-Path $ClaudeSyncScript) {
    & powershell -ExecutionPolicy Bypass -File $ClaudeSyncScript
} else {
    Write-Host "   ⚠️  sync-claude-md.ps1 not found at $ClaudeSyncScript" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "── Step 5: .gitignore ───────────────────────────" -ForegroundColor White
Write-Host ""

if ($SpecsMode -eq "symlink") {
    Add-UniqueManagedLink ".claude/specs"
    Add-UniqueManagedLink ".kiro/specs"
    Add-UniqueManagedLink ".codex/specs"
}

if (-not $IsGit) {
    Write-Host "   Skipped (not a git repository)"
} else {
    Rewrite-GitignoreSection $BridgeBegin $BridgeEnd $ManagedLinks.ToArray()
    Write-Host "   📝 Rewrote managed bridge entries in .gitignore" -ForegroundColor Green
}

Write-Host ""
Write-Host "── Verification ──────────────────────────────────" -ForegroundColor White
Write-Host ""

$allOk = $true
foreach ($root in $AgentRoots) {
    $rootItem = Get-Item -LiteralPath $root -ErrorAction SilentlyContinue
    if (-not $rootItem -or -not $rootItem.PSIsContainer -or ($rootItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        Write-Host "   ❌ $root must remain a real directory" -ForegroundColor Red
        $allOk = $false
    } else {
        Write-Host "   ✅ $root/ is a real directory" -ForegroundColor Green
    }

    $skillsPath = Join-Path $root "skills"
    $skillsItem = Get-Item -LiteralPath $skillsPath -ErrorAction SilentlyContinue
    if ($skillsItem -and ($skillsItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -and ((Resolve-NormalizedPath (Split-Path -Parent $skillsPath) (Get-LinkTarget $skillsPath)) -eq (Resolve-ExpectedLinkTarget $skillsPath $SkillsLinkSource))) {
        Write-Host "   ✅ $skillsPath -> $SourceSkills" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $skillsPath is missing or points to the wrong target" -ForegroundColor Red
        $allOk = $false
    }

    $specsPath = Join-Path $root "specs"
    if ($SpecsMode -eq "sync" -and (Test-Path $SourceSpecs -PathType Container)) {
        $specsItem = Get-Item -LiteralPath $specsPath -ErrorAction SilentlyContinue
        if ($specsItem -and $specsItem.PSIsContainer -and -not ($specsItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
            Write-Host "   ✅ $specsPath is a real synced directory" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $specsPath should be a real directory in sync mode" -ForegroundColor Red
            $allOk = $false
        }
    }

    if ($SpecsMode -eq "symlink" -and (Test-Path $SourceSpecs -PathType Container)) {
        $specsItem = Get-Item -LiteralPath $specsPath -ErrorAction SilentlyContinue
        if ($specsItem -and ($specsItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -and ((Resolve-NormalizedPath (Split-Path -Parent $specsPath) (Get-LinkTarget $specsPath)) -eq (Resolve-ExpectedLinkTarget $specsPath $SpecsLinkSource))) {
            Write-Host "   ✅ $specsPath -> $SourceSpecs" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $specsPath is missing or points to the wrong target" -ForegroundColor Red
            $allOk = $false
        }
    }
}

Write-Host ""
if ($allOk) {
    Write-Host "🎯 Hybrid bridge initialization completed successfully." -ForegroundColor Green
} else {
    Write-Host "❌ Verification failed. Review the output above." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "── Notes ─────────────────────────────────────────"
Write-Host "   • Only repo-local skills are symlinked by this workflow"
Write-Host "   • specs mode is '$SpecsMode' and can be changed on the next run"
Write-Host "   • Other config / permission surfaces are intentionally left real"
Write-Host "   • Run scripts/install-hook.ps1 to auto-sync CLAUDE.md on commit"
