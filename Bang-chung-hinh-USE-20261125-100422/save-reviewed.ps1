$ErrorActionPreference='Stop'
$live='C:\Users\NTNghia\OneDrive\Desktop\Thesis\Thesis\thesis - fixx.docx'
$approved='C:\Users\NTNghia\OneDrive\Desktop\Thesis\Thesis\Bang-chung-hinh-USE-20261125-100422\reviewed.docx'
$expected='D36400EC5DE3299F78720477AD09691A99AD76D539596667038C2360A8906DAF'
$pdf='C:\Users\NTNghia\OneDrive\Desktop\Thesis\Thesis\Bang-chung-hinh-USE-20261125-100422\thesis - fixx - kiem-tra.pdf'
function SharedSha([string]$source) {
    $stream=[IO.File]::Open($source,[IO.FileMode]::Open,[IO.FileAccess]::Read,([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete))
    try { (Get-FileHash -InputStream $stream).Hash } finally { $stream.Dispose() }
}
if ((SharedSha $live) -ne $expected) {throw 'Bản Word hiện tại đã thay đổi kể từ khi sao lưu.'}
$app=$null
try { $app=[Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application') } catch { }
$matches=@()
if($null -ne $app){
  $urlSuffix='/Desktop/Thesis/Thesis/thesis - fixx.docx'
  for($i=1;$i -le $app.Documents.Count;$i++){
    $candidate=$app.Documents.Item($i)
    $candidatePath=$candidate.FullName
    if($candidatePath -eq $live -or ([string]$candidatePath).EndsWith($urlSuffix,[StringComparison]::OrdinalIgnoreCase)){
      $matches += $candidate
    }
  }
}
if($matches.Count -gt 1){throw 'Có nhiều cửa sổ Word cho cùng tài liệu.'}
if($matches.Count -eq 1){
  if(-not $matches[0].Saved){throw 'Bản Word đang có thay đổi chưa lưu.'}
  $matches[0].Close(0)
}
if((SharedSha $live) -ne $expected){throw 'Nội dung trên đĩa đã thay đổi sau khi đóng Word.'}
$temp=Join-Path ([IO.Path]::GetDirectoryName($live)) ('.thesis-commit-' + [Guid]::NewGuid().ToString('N') + '.docx')
try {
  [IO.File]::Copy($approved,$temp,$false)
  [IO.File]::Replace($temp,$live,[NullString]::Value)
} finally {
  if(Test-Path -LiteralPath $temp){Remove-Item -LiteralPath $temp}
}
$sha=SharedSha $live
if($sha -ne (Get-FileHash -LiteralPath $approved).Hash){throw 'Bản Word sau khi lưu không khớp bản đã kiểm tra.'}
if($null -eq $app){$app=New-Object -ComObject Word.Application}
$doc=$app.Documents.Open($live,$false,$false)
$app.Visible=$true
$doc.Repaginate()
$doc.ExportAsFixedFormat($pdf,17)
"Saved: $live"
"SHA-256: $sha"
"Exported: $pdf"

