@echo off
setlocal EnableExtensions
cd /d %~dp0
REM ============================================================================
REM  Campagne v5 (H-C) — PREREGISTRATION_v5.md, gel ca588c3
REM  16 runs sequentiels : 4 modeles x {contested, consensual} x {fisher, shuffle}
REM  CPU float32 seed=0 (protocole gele). ETA total ~6-7 h.
REM  Relance sure : chaque run ecrase proprement sa propre sortie JSON.
REM ============================================================================
set PY=.venv\Scripts\python.exe
if not exist results\logs mkdir results\logs

echo [%date% %time%] === CAMPAGNE v5 : depart ===

call :one gpt2        gpt2
call :one pythia410m  EleutherAI/pythia-410m
call :one opt350m     facebook/opt-350m
call :one bloom560m   bigscience/bloom-560m

echo [%date% %time%] === 16 runs termines — verdict aux seuils geles ===
%PY% analysis_v5.py --results results --out results\analysis_v5_report.json
echo [%date% %time%] === FIN — rapport : results\analysis_v5_report.json ===
goto :eof

:one
set SHORT=%1
set HF=%2
echo [%date% %time%] --- %SHORT% (%HF%) : fisher contested ---
%PY% probe_fisher.py --model %HF% --corpus corpora\contested.txt --out results\%SHORT%_contested_fisher.json > results\logs\%SHORT%_contested_fisher.log 2>&1
echo [%date% %time%] --- %SHORT% : fisher consensual ---
%PY% probe_fisher.py --model %HF% --corpus corpora\consensual.txt --out results\%SHORT%_consensual_fisher.json > results\logs\%SHORT%_consensual_fisher.log 2>&1
echo [%date% %time%] --- %SHORT% : shuffle contested ---
%PY% probe_fisher_shuffle.py --model %HF% --corpus corpora\contested.txt --out results\%SHORT%_contested_shuffle.json > results\logs\%SHORT%_contested_shuffle.log 2>&1
echo [%date% %time%] --- %SHORT% : shuffle consensual ---
%PY% probe_fisher_shuffle.py --model %HF% --corpus corpora\consensual.txt --out results\%SHORT%_consensual_shuffle.json > results\logs\%SHORT%_consensual_shuffle.log 2>&1
echo [%date% %time%] --- %SHORT% : 4/4 OK ---
goto :eof
