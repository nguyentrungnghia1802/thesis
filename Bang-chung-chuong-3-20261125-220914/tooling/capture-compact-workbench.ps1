param([string[]]$Only)
$ErrorActionPreference='Stop'
$env:THESIS_PLAYWRIGHT='C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1123-915-0_26.1123.915.0_x64__3k8sg7r9htsxt\dependencies\node\node_modules\playwright'
$inst=(Resolve-Path -LiteralPath 'use-assembly\target\new-staging').Path
$tool='C:\Users\NTNghia\OneDrive\Desktop\Thesis\Thesis\Bang-chung-chuong-3-20261125-220914\tooling'
$old='C:\Users\NTNghia\OneDrive\Desktop\Thesis\Thesis\Bang-chung-4-cum-anh-20261124-170243'
$examples=(Resolve-Path 'use-plugin\src\main\resources\example').Path
$cases=[ordered]@{
  'TN05-chuyen-giao'=@("$old\TN05-loi-chuyen-giao\project\auction.mrv",'goal')
  'TN01'=@("$examples\auction\auction.mrv",'mapping')
  'TN03'=@("$examples\counter\counter.mrv",'counterbase')
  'TN06-chuyen-giao'=@("$old\TN06-thieu-chuyen-giao\project\auction.mrv",'missing')
  'TN07-giu-am'=@("$old\TN07-counter-giu-am\project\counter.mrv",'counter')
  'TN07-khoi-phuc'=@("$old\TN07-counter-khoi-phuc\project\counter.mrv",'restored')
}
foreach($id in $cases.Keys) {
  if($Only -and $id -notin $Only){continue}
  $where=Join-Path 'C:\Users\NTNghia\OneDrive\Desktop\Thesis\Thesis\Bang-chung-chuong-3-20261125-220914' ($id+'-trinhbay')
  if(Test-Path -LiteralPath "$where\selection.txt"){throw "Valid existing run in $where"}
  $null=New-Item -ItemType Directory -Path $where -Force
  $inputFile,$mode=$cases[$id]
  $javaArgs=@('-cp',"$tool;$inst\lib\*",'CaptureChapter3',$inst,$where,$inputFile,$mode,'C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1123-915-0_26.1123.915.0_x64__3k8sg7r9htsxt\dependencies\node\bin\node.exe',"$tool\capture-moise.cjs")
  (Get-FileHash -LiteralPath $inputFile).Hash | Set-Content -Encoding utf8 -LiteralPath "$where\mrv.sha256"
  ('java '+(($javaArgs | ForEach-Object {'"'+$_+'"'}) -join ' ')) | Set-Content -Encoding utf8 -LiteralPath "$where\command.txt"
  "Running $id"
  java @javaArgs 2>&1 | Out-File -Encoding utf8 -LiteralPath "$where\capture.log"
  "$id result $LASTEXITCODE"
  Get-Content -LiteralPath "$where\capture.log" -Tail 10
}

