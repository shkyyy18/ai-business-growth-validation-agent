param([string]$DayRoot = $PSScriptRoot)
$records = foreach($file in Get-ChildItem -LiteralPath $DayRoot -Filter 'kimi-attempt-*.stdout.jsonl' -File) {
    $parseErrors=0
    $events=@(Get-Content -LiteralPath $file.FullName | ForEach-Object {try{$_|ConvertFrom-Json -ErrorAction Stop}catch{$parseErrors++}})
    $tools=@(foreach($event in $events){foreach($call in $event.tool_calls){if($call){[pscustomobject]@{id=$call.id;name=$call.function.name;arguments=$call.function.arguments}}}})
    [pscustomobject]@{file=$file.Name;parse_errors=$parseErrors;meta=@($events|Where-Object {$_.role -eq 'meta'});tools=$tools;tool_responses=@($events|Where-Object {$_.role -eq 'tool'}).Count;assistant_messages=@($events|Where-Object {$_.role -eq 'assistant' -and $_.content});limitations='Tools reported by CLI only; not proof of backend model identity or complete OS-level access history.'}
}
$records | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath (Join-Path $DayRoot 'tool-audit.json') -Encoding UTF8
$records | ForEach-Object {[pscustomobject]@{File=$_.file;Tools=$_.tools.Count;Responses=$_.tool_responses;ParseErrors=$_.parse_errors}}
