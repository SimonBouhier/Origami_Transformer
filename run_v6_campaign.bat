@echo off
setlocal EnableExtensions
cd /d %~dp0
REM ============================================================================
REM  Campagne v6 (H-D) — PREREGISTRATION_v6.md, gel 10b6c89
REM  8 runs : 4 modeles x {fisher, shuffle} sur consensual_v6 UNIQUEMENT
REM  (le bras conteste reutilise les mesures v5 — decision gelee).
REM  CPU float32 seed=0. ETA ~2 h 15.
REM ============================================================================
set PY=.venv\Scripts\python.exe
if not exist results\logs mkdir results\logs

echo [%date% %time%] === selftest (hashes + folds, aucune mesure lue) ===
%PY% analysis_v6.py --selftest
if errorlevel 1 goto :fail

echo [%date% %time%] === CAMPAGNE v6 : depart ===
call :one gpt2        gpt2
call :one pythia410m  EleutherAI/pythia-410m
call :one opt350m     facebook/opt-350m
call :one bloom560m   bigscience/bloom-560m

echo [%date% %time%] === 8 runs termines — verdict aux seuils geles ===
%PY% analysis_v6.py --results results --out results\analysis_v6_report.json
echo [%date% %time%] === FIN — rapport : results\analysis_v6_report.json ===
goto :eof

:one
set SHORT=%1
set HF=%2
echo [%date% %time%] --- %SHORT% (%HF%) : fisher consensual_v6 ---
%PY% probe_fisher.py --model %HF% --corpus corpora\consensual_v6.txt --out results\%SHORT%_consensualv6_fisher.json > results\logs\%SHORT%_consensualv6_fisher.log 2>&1
echo [%date% %time%] --- %SHORT% : shuffle consensual_v6 ---
%PY% probe_fisher_shuffle.py --model %HF% --corpus corpora\consensual_v6.txt --out results\%SHORT%_consensualv6_shuffle.json > results\logs\%SHORT%_consensualv6_shuffle.log 2>&1
echo [%date% %time%] --- %SHORT% : 2/2 OK ---
goto :eof

:fail
echo [%date% %time%] SELFTEST EN ECHEC — campagne NON lancee.
exit /b 1
