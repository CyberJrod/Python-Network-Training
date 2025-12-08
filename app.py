import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import streamlit as st


st.set_page_config(page_title="Python Network Orchestrator", layout="wide")

ROOT = Path(__file__).parent


def find_jobs_dir(root: Path) -> Path:
    # support both `jobs` and `Jobs`
    for name in ("jobs", "Jobs"):
        p = root / name
        if p.exists() and p.is_dir():
            return p
    # create default `jobs`
    p = root / "jobs"
    p.mkdir(exist_ok=True)
    return p


JOBS_DIR = find_jobs_dir(ROOT)


def script_description(path: Path) -> str:
    try:
        src = path.read_text(encoding="utf-8")
        module = ast.parse(src)
        doc = ast.get_docstring(module)
        if doc:
            return doc.strip().splitlines()[0]
    except Exception:
        pass

    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s.startswith("#"):
                    return s.lstrip("# ")
                if s:
                    break
    except Exception:
        pass
    return "(no description)"


def load_config(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return None
        return json.loads(text)
    except Exception:
        return None


CONFIG_PATH = ROOT / "config" / "config.json"
config = load_config(CONFIG_PATH)


def load_device_names_from_csv(csv_path: Path) -> List[str]:
    names: List[str] = []
    if not csv_path.exists():
        return names
    try:
        import csv  # local import to avoid unused global if not used

        with csv_path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                for row in reader:
                    hostname = (row.get("hostname") or "").strip()
                    ip = (row.get("ip") or row.get("device_ips") or "").strip()
                    label = hostname or ip
                    if label:
                        names.append(label)
            if not names:
                f.seek(0)
                reader2 = csv.reader(f)
                for idx, row in enumerate(reader2):
                    if not row:
                        continue
                    val = row[0].strip()
                    if idx == 0 and val.lower() in ("hostname", "device_ips", "ip"):
                        continue
                    if val:
                        names.append(val)
    except Exception:
        pass
    return names


def resolve_script_path(file_field: str) -> Optional[Path]:
    p = Path(file_field)
    if not p.is_absolute():
        # try relative to repo root
        cand = ROOT / file_field
        if cand.exists():
            return cand
        # try relative to jobs dir
        cand = JOBS_DIR / file_field
        if cand.exists():
            return cand
        # try only name in jobs dir
        cand = JOBS_DIR / Path(file_field).name
        if cand.exists():
            return cand
        return None
    else:
        return p if p.exists() else None


def build_cli_args_from_inputs(inputs: List[Dict[str, Any]], values: Dict[str, Any]) -> List[str]:
    args: List[str] = []
    for inp in inputs:
        name = inp.get("name")
        arg_name = inp.get("arg")  # e.g. "--count" or "count"
        typ = inp.get("type", "text")
        val = values.get(name)
        if val is None:
            continue
        # handle boolean flags
        if typ == "bool":
            if val:
                if arg_name:
                    args.append(str(arg_name))
                else:
                    args.append(f"--{name}")
            continue
        if typ == "password":
            # strip to avoid trailing spaces while keeping actual value
            cleaned = str(val).strip()
            if arg_name:
                args.append(str(arg_name))
                args.append(cleaned)
            else:
                args.append(cleaned)
            continue
        if typ == "multiselect_devices":
            if not val:
                continue
            if arg_name:
                args.append(str(arg_name))
            # already comma-separated string
            args.append(str(val))
            continue
        # if arg name provided, pass as flag + value, otherwise pass value alone
        if arg_name:
            args.append(str(arg_name))
            args.append(str(val))
        else:
            args.append(str(val))
    return args


st.title("Python Network Orchestrator")


scripts_catalog: List[Dict[str, Any]] = []

if config and isinstance(config.get("scripts"), list):
    for s in config.get("scripts", []):
        # ensure we can resolve the file
        file_field = s.get("file")
        path = resolve_script_path(file_field) if file_field else None
        s_copy = dict(s)
        s_copy["_path"] = str(path) if path else None
        scripts_catalog.append(s_copy)

# If config is missing or empty, fall back to scanning jobs directory
if not scripts_catalog:
    py_files = sorted([p for p in JOBS_DIR.glob("*.py")])
    for p in py_files:
        scripts_catalog.append({
            "id": p.stem,
            "name": p.name,
            "file": str(p.relative_to(ROOT)),
            "description": script_description(p),
            "_path": str(p),
            "inputs": [],
        })

if not scripts_catalog:
    st.warning("No scripts found. Add `.py` files to the `jobs/` folder or define them in `config/config.json`.")
    st.info("See `config/config.json` for the app schema example.")

selected_idx = st.selectbox(
    "Select a script",
    options=list(range(len(scripts_catalog))) if scripts_catalog else [],
    format_func=lambda i: scripts_catalog[i]["name"] if scripts_catalog else "",
)

if scripts_catalog:
    script = scripts_catalog[selected_idx]
    script_path_str = script.get("_path")
    if not script_path_str:
        st.error("Configured script file not found: {}".format(script.get("file")))
    else:
        script_path = Path(script_path_str)
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Info")
            st.write("**Name:**", script.get("name"))
            st.write("**Path:**", script_path)
            st.write("**Description:**", script.get("description") or script_description(script_path))

            # build inputs
            inputs = script.get("inputs", []) or []
            values: Dict[str, Any] = {}
            if inputs:
                st.markdown("**Inputs**")
                for inp in inputs:
                    key = inp.get("name")
                    label = inp.get("label") or key
                    typ = inp.get("type", "text")
                    default = inp.get("default")
                    if typ == "int":
                        values[key] = st.number_input(label, value=int(default) if default is not None else 0, step=1)
                    elif typ == "float":
                        values[key] = st.number_input(label, value=float(default) if default is not None else 0.0)
                    elif typ == "select":
                        choices = inp.get("choices", [])
                        values[key] = st.selectbox(label, choices, index=0 if default is None else (choices.index(default) if default in choices else 0))
                    elif typ == "password":
                        values[key] = st.text_input(label, value=str(default) if default is not None else "", type="password")
                    elif typ == "multiselect":
                        choices = inp.get("choices", [])
                        default_list = default if isinstance(default, list) else (choices if default is True else [])
                        values[key] = st.multiselect(label, choices, default=default_list)
                    elif typ == "multiselect_devices":
                        csv_input = inp.get("csv_input") or "devices_csv"
                        csv_path_str = values.get(csv_input) or default or ""
                        csv_path = Path(csv_path_str) if csv_path_str else None
                        device_choices: List[str] = []
                        if csv_path:
                            device_choices = load_device_names_from_csv(csv_path)
                        if inp.get("include_all_option", True):
                            device_choices = ["all"] + device_choices
                        if inp.get("include_none_option", True):
                            device_choices = device_choices + ["none"]
                        default_list = default if isinstance(default, list) else (["all"] if default is True else [])
                        selection = st.multiselect(label, device_choices, default=default_list)
                        # store as comma-separated string for CLI arg
                        values[key] = ",".join(selection)
                    elif typ == "bool":
                        values[key] = st.checkbox(label, value=bool(default))
                    else:
                        values[key] = st.text_input(label, value=str(default) if default is not None else "")

            run_btn = st.button("Run script")

        with col2:
            show_source = st.checkbox("Show source code", value=False)
            if show_source:
                st.subheader("Source")
                try:
                    code = script_path.read_text(encoding="utf-8")
                    st.code(code, language="python")
                except Exception as e:
                    st.error(f"Could not read file: {e}")

        if run_btn:
            cmd = [sys.executable, str(script_path)]
            # if config provided inputs, convert to args
            args_from_inputs = build_cli_args_from_inputs(inputs, values)
            if args_from_inputs:
                cmd += args_from_inputs

            st.subheader("Execution")
            st.write("Running:", " ".join(cmd))
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                st.markdown(f"**Return code:** {proc.returncode}")
                st.subheader("Stdout")
                st.text(proc.stdout)
                st.subheader("Stderr")
                st.text(proc.stderr)
            except subprocess.TimeoutExpired:
                st.error("Script timed out (300s)")
            except Exception as e:
                st.error(f"Error running script: {e}")

st.sidebar.title("About")
if config:
    st.sidebar.info("UI driven by `config/config.json`. Edit it to control displayed scripts and inputs.")
else:
    st.sidebar.info("No config found; app is showing scripts discovered in the `jobs/` folder.")
