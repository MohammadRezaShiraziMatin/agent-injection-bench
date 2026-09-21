param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$Args
)

$quoted = ($Args | ForEach-Object {
  if ($_ -match '\s') { "'$($_ -replace "'", "''")'" } else { $_ }
}) -join ' '

wsl.exe -e bash -lc "export PATH=\"`$HOME/.openclaw/bin:`$PATH\"; openclaw $quoted"
