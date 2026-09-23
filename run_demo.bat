@echo off
cd /d "%~dp0"
echo Starting GreenPaper Sales Order Management with LIVE SAP synchronization...
python backend\server.py
pause
