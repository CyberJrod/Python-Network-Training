# Python Network Automation Lab Runner (Streamlit)

This Streamlit app helps run and preview your Python network automation training labs. Drop each lab script into `jobs/` (or configure them in `config/config.json`), then use the UI to read the source (optional), pass arguments, and execute the script from the browser.

## Setup (Windows)
1) Create the virtual environment with the helper script:
```powershell
powershell -ExecutionPolicy Bypass -File .\init_venv.ps1
```
2) Activate the venv:
- PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```
- Command Prompt (cmd.exe):
```cmd
.\.venv\Scripts\activate.bat
```
3) Install dependencies inside the venv (init_venv.ps1 already does this once, but you can rerun to update):
```powershell
python -m pip install -r requirements.txt
```

## Running the app
```powershell
streamlit run app.py
```

## Current labs
- **Lab 1 - Variables and Print**: Demonstrates variables and print statements. Prompts for device username/password via the UI.
- **Lab 2 - Netmiko Connection**: Connects to devices from a CSV (default `data/lab2.csv`) and runs selected show commands. Prompts for username/password and lets you choose which commands to run (show ip interface brief, show ip route, show version). You can override the CSV path in the UI.

## Configuration
- Scripts and their inputs are defined in `config/config.json`. The app prefers this config; if it cannot load it, it falls back to auto-discovering `.py` files under `jobs/` / `Jobs/` (no inputs in that mode).
- Typical input types used:
  - `text` for credentials and paths (e.g., username, password, CSV path)
  - `bool` for toggling commands (checkboxes in the UI)

## Notes
- The app uses the same Python interpreter that launched Streamlit (ideally your venv).
- You can optionally toggle source display per script in the UI.
- Review scripts before running them, especially if they connect to network gear.
