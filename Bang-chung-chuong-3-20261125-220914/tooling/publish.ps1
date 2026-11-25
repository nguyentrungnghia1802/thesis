$ErrorActionPreference='Stop'
$source='C:\Users\NTNghia\OneDrive\Desktop\Thesis\Thesis\thesis - fixx.docx'
$before='C:\Users\NTNghia\OneDrive\Desktop\Thesis\Thesis\2, Backup\thesis - fixx - truoc-bien-tap-chuong-3 - 20261125-220914.docx'
$expected='1CD4CDE046EDCE8D1B6FDA3FF10CF2DAD5CE1F0B34F940FE3DA324B99583B7E1'
$approved='C:\Users\NTNghia\OneDrive\Desktop\Thesis\Thesis\Bang-chung-chuong-3-20261125-220914\_qa\reviewed.docx'
$pdf='C:\Users\NTNghia\OneDrive\Desktop\Thesis\Thesis\Bang-chung-chuong-3-20261125-220914\_qa\published.pdf'
function SharedHash([string]$path){
    $stream=[IO.File]::Open($path,[IO.FileMode]::Open,[IO.FileAccess]::Read,([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete))
    try {(Get-FileHash -InputStream $stream).Hash} finally {$stream.Dispose()}
}
if((SharedHash $before) -ne $expected){throw 'Backup differs from initial copy.'}
if((SharedHash $source) -ne $expected){throw 'The live thesis has changed since the backup.'}
$expectedFinal=(Get-FileHash -LiteralPath $approved).Hash
$application=$null
try{$application=[Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application')}catch{}
$targetDocs=@()
if($null -ne $application){
  for($i=1;$i -le $application.Documents.Count;$i++){
    $observed=$application.Documents.Item($i)
    $path=([string]$observed.FullName).Replace('%20',' ')
    if($path -eq $source -or $path.EndsWith('/Desktop/Thesis/Thesis/thesis - fixx.docx',[StringComparison]::OrdinalIgnoreCase)){
        $targetDocs += $observed
    }
  }
}
if($targetDocs.Count -gt 1){throw 'Multiple open instances of the thesis.'}
if($targetDocs.Count -eq 1){
    if(-not $targetDocs[0].Saved){throw 'Word contains unsaved user edits.'}
    $targetDocs[0].Close(0)
}
if((SharedHash $source) -ne $expected){throw 'The thesis changed while Word closed.'}
$tmp=Join-Path ([IO.Path]::GetDirectoryName($source)) ('.thesis-chapter3-'+[Guid]::NewGuid().ToString('N')+'.docx')
try{
  [IO.File]::Copy($approved,$tmp,$false)
  [IO.File]::Replace($tmp,$source,[NullString]::Value)
} finally {
  if(Test-Path -LiteralPath $tmp){Remove-Item -LiteralPath $tmp}
}
if((SharedHash $source) -ne $expectedFinal){throw 'Saved file differs from the reviewed document.'}
if($null -eq $application){$application=New-Object -ComObject Word.Application}
$doc=$application.Documents.Open($source,$false,$false)
$application.Visible=$true
$doc.Repaginate()
$doc.ExportAsFixedFormat($pdf,17)
if((SharedHash $source) -ne $expectedFinal){throw 'File changed when reopened.'}
"Saved path: $source"
"Backup: $before"
"SHA-256: $expectedFinal"
"Reopened: $($doc.Name)"
"PDF: $pdf"

