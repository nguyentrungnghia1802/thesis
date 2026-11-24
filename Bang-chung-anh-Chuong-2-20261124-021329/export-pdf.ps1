param([string]$InputDoc,[string]$OutputPdf)
$ErrorActionPreference='Stop'
$word=New-Object -ComObject Word.Application
try {
    $word.DisplayAlerts=0
    $doc=$word.Documents.Open($InputDoc,$false,$true)
    $doc.Repaginate()
    $doc.ExportAsFixedFormat($OutputPdf,17)
    $doc.Close(0)
} finally {
    $word.Quit()
}
