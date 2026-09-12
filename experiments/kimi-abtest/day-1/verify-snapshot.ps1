param([string]$DayRoot = $PSScriptRoot)
$ErrorActionPreference = 'Stop'
$manifest = Get-Content -LiteralPath (Join-Path $DayRoot 'snapshot-hashes.json') -Encoding UTF8 | ConvertFrom-Json
$projectRoot = Split-Path (Split-Path (Split-Path $DayRoot))
$checks = foreach ($row in $manifest) {
    foreach ($dir in @('input-snapshot', 'kimi-workspace')) {
        $path = Join-Path (Join-Path $DayRoot $dir) $row.path
        $exists = Test-Path -LiteralPath $path -PathType Leaf
        $actual = if ($exists) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash } else { $null }
        [pscustomobject]@{scope=$dir;path=$row.path;exists=$exists;expected=$row.sha256;actual=$actual;matches=($actual -eq $row.sha256)}
    }
}
$sourceChecks = foreach ($row in $manifest) {
    $path = Join-Path $projectRoot $row.path
    $exists = Test-Path -LiteralPath $path -PathType Leaf
    $actual = if ($exists) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash } else { $null }
    [pscustomobject]@{path=$row.path;matches_snapshot=($actual -eq $row.sha256);note='Any live changes may originate from concurrent work; not attributed to Kimi without tool evidence.'}
}
$allowed = @($manifest.path) + @('TASK.md', 'kimi-output.md')
$workRoot = Join-Path $DayRoot 'kimi-workspace'
$files = @(Get-ChildItem -LiteralPath $workRoot -File -Recurse -Force | ForEach-Object {$_.FullName.Substring($workRoot.Length + 1).Replace('\','/')})
$unexpected = @($files | Where-Object {$_ -notin $allowed})
$utf8 = New-Object System.Text.UTF8Encoding($false, $true)
$outputChecks = foreach($relative in @('codex-direct.md','kimi-workspace/kimi-output.md')) {
    $path = Join-Path $DayRoot $relative
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        try { $text = $utf8.GetString([IO.File]::ReadAllBytes($path)); $valid=$true } catch { $text=''; $valid=$false }
        [pscustomobject]@{path=$relative;exists=$true;valid_utf8=$valid;sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash;characters=$text.Length}
    } else { [pscustomobject]@{path=$relative;exists=$false;valid_utf8=$null} }
}
$report = [ordered]@{checked_at=(Get-Date).ToString('o');snapshot_checks=@($checks);all_snapshot_hashes_match=(@($checks|Where-Object {-not $_.matches}).Count -eq 0);workspace_files=$files;unexpected_workspace_files=$unexpected;task_matches_plan=((Get-FileHash -LiteralPath (Join-Path $workRoot 'TASK.md')).Hash -eq (Get-FileHash -LiteralPath (Join-Path $DayRoot 'kimi-plan.md')).Hash);outputs=@($outputChecks);live_source_checks=@($sourceChecks);limitations='Hash checks verify listed paths and workspace files, not the full disk. Review tool logs for observed scope; no OS-enforced read isolation claimed.'}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $DayRoot 'verification.json') -Encoding UTF8
[pscustomobject]@{AllSnapshotHashesMatch=$report.all_snapshot_hashes_match;UnexpectedFiles=$unexpected.Count;TaskMatchesPlan=$report.task_matches_plan;LiveSourceDifferences=@($sourceChecks|Where-Object {-not $_.matches_snapshot}).Count}
