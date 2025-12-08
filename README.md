# Python Network Automation Lab Runner (Streamlit)

This Streamlit app helps run and preview your Python network automation training labs. Drop each lab script into `jobs/` (or configure them in `config/config.json`), then use the UI to read the source, pass arguments, and execute the script from the browser.

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
python - m streamlit run app.py
```

## How it works
- Scans `config/config.json` for scripts (falls back to any `.py` files under `jobs/` / `Jobs/`).
- Shows docstring/first comment as the description and displays the source code.
- Runs the selected script with inputs converted to CLI args and shows return code, stdout, and stderr.

## Tips
- Keep each lab in its own `.py` file under `jobs/` or point to it via `config/config.json`.
- The app uses the same Python interpreter that launched Streamlit (ideally your venv).
- Review scripts before running them, especially if they connect to network gear.
