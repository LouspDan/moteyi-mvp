@echo off
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

REM -----------------------------------------------------------------------------
REM Pipeline Moteyi : manifest -> normalize -> reconcile -> index -> eval -> report
REM Usage:
REM   tools\pipeline_refresh.bat
REM Options:
REM   FAIL_COV5 / FAIL_HIT1 (env) : seuils d'échec eval (défaut 0.50 / 0.35)
REM -----------------------------------------------------------------------------

set ROOT_DIR=%~dp0..
cd /d "%ROOT_DIR%"

set CATALOG=data\rag_seed\rag_seed_catalog.csv
set MANIFEST=data\index\manifest.json
set GOLD=data\eval\gold.jsonl

if "%FAIL_COV5%"=="" set FAIL_COV5=0.50
if "%FAIL_HIT1%"=="" set FAIL_HIT1=0.35

echo ==^> 1) Catalog -^> Manifest
python tools\catalog_to_manifest.py --catalog "%CATALOG%" --out "%MANIFEST%"
if errorlevel 1 goto :err

echo ==^> 2) Normalize naming (apply)
python tools\normalize_rag_seed_naming.py --catalog "%CATALOG%" --apply
if errorlevel 1 goto :err

echo ==^> 3) Reconcile gold.jsonl (apply)
python tools\reconcile_gold_ids.py --apply
if errorlevel 1 goto :err

echo ==^> 4) Index retriever config
python scripts\rag_index.py
if errorlevel 1 goto :err

echo ==^> 5) Eval (k=5) avec seuils FAIL_COV5=%FAIL_COV5%, FAIL_HIT1=%FAIL_HIT1%
if not exist artifacts mkdir artifacts
set FAIL_COV5=%FAIL_COV5%
set FAIL_HIT1=%FAIL_HIT1%
python scripts\rag_eval.py --gold "%GOLD%" --k 5 --out artifacts\metrics.csv
REM on ne stoppe pas si les seuils échouent, on continue le rapport

echo ==^> 6) Rapport HTML
python scripts\eval_report.py
if errorlevel 1 goto :err

echo.
echo ==^> ✅ DONE
echo  - Manifest : %MANIFEST%
echo  - Metrics  : artifacts\metrics.csv
echo  - Report   : artifacts\rag_eval_report.html
goto :eof

:err
echo.
echo ❌ ERREUR: l'etape precedente a echoue (code %errorlevel%)
exit /b %errorlevel%
