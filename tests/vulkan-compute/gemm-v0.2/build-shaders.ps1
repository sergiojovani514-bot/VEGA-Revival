param([Parameter(Mandatory=$true)][string]$GlslangExe)
$ErrorActionPreference='Stop'
$compiler=(Resolve-Path -LiteralPath $GlslangExe).Path
$src=Join-Path $PSScriptRoot 'matmul_tuned.comp'
$config=@('-V','--target-env','vulkan1.2','-S','comp','-DREG_M=4','-DREG_N=4','-DWG_X=8','-DWG_Y=8','-DBK=32','-DLDS_PAD=1','-DVECTOR_LOADS=1')
foreach($mode in @('FP32','FP16_ACC16','FP16_ACC32')){
  $name='bounded_'+$mode.ToLower()+'.spv'
  $compilerArgs=$config+@("-DMODE_$mode=1",'-o',(Join-Path $PSScriptRoot $name),$src)
  & $compiler @compilerArgs
  if($LASTEXITCODE){throw "shader compile failed: $mode"}
}
$compilerArgs=$config+@('-DMODE_FP16_ACC16=1','-DPACKED_F16=1','-o',(Join-Path $PSScriptRoot 'packed_fp16_acc16.spv'),$src)
& $compiler @compilerArgs
if($LASTEXITCODE){throw 'packed shader compile failed'}

