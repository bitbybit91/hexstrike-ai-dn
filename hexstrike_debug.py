#!/usr/bin/env python3
"""
HexStrike AI - Comprehensive Debug & Production-Readiness Diagnostic Tool

Performs a full audit of the HexStrike AI project to ensure it is:
  - Correctly installed and configured
  - Running production-ready without debug flags or exposed secrets
  - Fully functional with all API endpoints responding correctly
  - Equipped with the required system tools and Python packages

Checks performed:
  1. Environment & Dependency Validation
  2. Configuration Validation
  3. Server Health & Functionality Testing
  4. Network & Port Diagnostics
  5. File Integrity Checks
  6. Production Readiness Checks
  7. Summary Report

Usage:
    python3 hexstrike_debug.py              # Full diagnostic (colored output)
    python3 hexstrike_debug.py --json       # JSON output for CI/CD
    python3 hexstrike_debug.py --fix        # Attempt to auto-fix common issues

Exit codes:
    0  All critical checks passed
    1  One or more critical checks failed

⚠️  Legal Notice: Only use on systems you own or have explicit written
    authorization to test. Unauthorized access is illegal.
"""

import argparse
import ast
import importlib
import importlib.util
import json
import os
import platform
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# ANSI colour scheme (matches hexstrike_setup.py)
# ---------------------------------------------------------------------------
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Resolved at runtime: disable colour when writing JSON or when stdout is not
# a TTY (e.g. redirected to a file).
_USE_COLOR = True

def _c(code: str) -> str:
    """Return the ANSI code only when colour output is enabled."""
    return code if _USE_COLOR else ""


# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------

class Result:
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


RESULTS: List[Dict[str, Any]] = []


def _record(section: str, name: str, status: str, detail: str = "") -> Dict[str, Any]:
    entry = {"section": section, "name": name, "status": status, "detail": detail}
    RESULTS.append(entry)
    return entry


# ---------------------------------------------------------------------------
# Pretty-printing helpers
# ---------------------------------------------------------------------------

def _section(title: str) -> None:
    width = 62
    print(f"\n{_c(RED)}{_c(BOLD)}{'═' * width}{_c(RESET)}")
    print(f"{_c(RED)}{_c(BOLD)}  {title}{_c(RESET)}")
    print(f"{_c(RED)}{_c(BOLD)}{'═' * width}{_c(RESET)}\n")


def _ok(name: str, detail: str = "") -> None:
    suffix = f"  {_c(CYAN)}{detail}{_c(RESET)}" if detail else ""
    print(f"  {_c(GREEN)}[✔]{_c(RESET)} {name}{suffix}")


def _fail(name: str, detail: str = "") -> None:
    suffix = f"  {_c(YELLOW)}{detail}{_c(RESET)}" if detail else ""
    print(f"  {_c(RED)}[✘]{_c(RESET)} {name}{suffix}")


def _warn(name: str, detail: str = "") -> None:
    suffix = f"  {_c(CYAN)}{detail}{_c(RESET)}" if detail else ""
    print(f"  {_c(YELLOW)}[!]{_c(RESET)} {name}{suffix}")


def _info(name: str, detail: str = "") -> None:
    suffix = f"  {_c(CYAN)}{detail}{_c(RESET)}" if detail else ""
    print(f"  {_c(CYAN)}[*]{_c(RESET)} {name}{suffix}")


def _check(section: str, name: str, passed: bool, detail: str = "",
           critical: bool = True, warn_on_fail: bool = False) -> bool:
    """
    Record a check result and print it.

    Returns True if the check passed (or is only a warning).
    """
    if passed:
        status = Result.PASS
        _ok(name, detail)
    elif warn_on_fail:
        status = Result.WARN
        _warn(name, detail)
    else:
        status = Result.FAIL
        _fail(name, detail)
    _record(section, name, status, detail)
    return passed


# ---------------------------------------------------------------------------
# Constants – project layout
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent

EXPECTED_FILES = [
    "hexstrike_server.py",
    "hexstrike_mcp.py",
    "hexstrike_setup.py",
    "hexstrike-ai-mcp.json",
    "requirements.txt",
    "README.md",
    "LICENSE",
]

# Packages that are imported under a different name than their distribution name
IMPORT_NAME_MAP = {
    "beautifulsoup4": "bs4",
    "webdriver-manager": "webdriver_manager",
    "fastmcp": "mcp",
    "pwntools": "pwn",
}

# Packages that are genuinely optional (may not build on all platforms)
OPTIONAL_PACKAGES = {"pwntools", "angr"}

# System command-line tools to detect
SYSTEM_TOOLS = [
    "nmap", "gobuster", "nuclei", "sqlmap", "nikto", "hydra", "john",
    "hashcat", "masscan", "dirb", "ffuf", "feroxbuster", "wpscan",
    "subfinder", "httpx", "katana", "amass", "gau", "waybackurls",
    "radare2", "gdb", "binwalk", "checksec", "tor", "proxychains4",
    "torsocks",
]

MCP_JSON_PATH = SCRIPT_DIR / "hexstrike-ai-mcp.json"
REQUIREMENTS_PATH = SCRIPT_DIR / "requirements.txt"
VENV_DIR = SCRIPT_DIR / "hexstrike-env"
PROXYCHAINS_CONF = Path("/etc/proxychains4.conf")

TEST_PORT = 18888
DEFAULT_PORT = 8888
TOR_SOCKS_PORT = 9050

# Patterns that suggest hardcoded secrets (simple heuristic)
SECRET_PATTERNS = [
    re.compile(r'(?i)(password|passwd|secret|api[_-]?key|token|auth[_-]?key)\s*=\s*["\'][^"\']{4,}["\']'),
    re.compile(r'(?i)private[_-]?key\s*=\s*["\'][^"\']{4,}["\']'),
    re.compile(r'(?i)(aws|gcp|azure)[_-]?(access|secret|key)\s*=\s*["\'][^"\']{4,}["\']'),
]


# ===========================================================================
# SECTION 1 – Environment & Dependency Validation
# ===========================================================================

def check_python_version(section: str) -> None:
    """Require Python 3.8+."""
    major, minor = sys.version_info[:2]
    ok = (major, minor) >= (3, 8)
    detail = f"Python {major}.{minor}.{sys.version_info[2]}"
    _check(section, "Python 3.8+ runtime", ok, detail, critical=True)


def check_pip_packages(section: str, fix: bool) -> None:
    """Verify every package in requirements.txt is importable."""
    if not REQUIREMENTS_PATH.exists():
        _check(section, "requirements.txt readable", False,
               "File not found – skipping package checks", critical=True)
        return

    packages = _parse_requirements()

    for pkg in packages:
        import_name = IMPORT_NAME_MAP.get(pkg, pkg.replace("-", "_"))
        is_optional = pkg in OPTIONAL_PACKAGES

        try:
            importlib.import_module(import_name)
            _check(section, f"Package '{pkg}' importable", True, import_name)
        except ImportError as exc:
            if fix:
                _info(f"Auto-fix: pip install {pkg}")
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", pkg],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=120,
                    )
                    importlib.import_module(import_name)
                    _check(section, f"Package '{pkg}' importable (fixed)", True, import_name)
                    continue
                except Exception as fix_exc:
                    detail = f"Auto-fix failed: {fix_exc}"
                    _check(section, f"Package '{pkg}' importable", False, detail,
                           warn_on_fail=is_optional)
            else:
                detail = str(exc)
                _check(section, f"Package '{pkg}' importable", False, detail,
                       warn_on_fail=is_optional)


def check_venv(section: str) -> None:
    """Check that the hexstrike-env virtual environment directory exists."""
    exists = VENV_DIR.is_dir()
    _check(section, "hexstrike-env venv directory exists", exists,
           str(VENV_DIR), warn_on_fail=True)

    # Check whether the current interpreter is *inside* that venv
    venv_python = VENV_DIR / "bin" / "python3"
    activated = str(Path(sys.executable).resolve()).startswith(str(VENV_DIR.resolve()))
    _check(section, "hexstrike-env is active (current interpreter)",
           activated, sys.executable, warn_on_fail=True)


def check_system_tools(section: str) -> None:
    """Report which system security tools are installed."""
    for tool in SYSTEM_TOOLS:
        found = shutil.which(tool) is not None
        _check(section, f"System tool '{tool}' available", found,
               shutil.which(tool) or "not found", warn_on_fail=True)


# ===========================================================================
# SECTION 2 – Configuration Validation
# ===========================================================================

def check_mcp_config(section: str) -> None:
    """Validate hexstrike-ai-mcp.json structure and referenced paths."""
    if not _check(section, "hexstrike-ai-mcp.json exists",
                  MCP_JSON_PATH.exists(), str(MCP_JSON_PATH)):
        return

    try:
        with MCP_JSON_PATH.open(encoding="utf-8") as fh:
            cfg = json.load(fh)
    except json.JSONDecodeError as exc:
        _check(section, "hexstrike-ai-mcp.json is valid JSON", False, str(exc))
        return

    _check(section, "hexstrike-ai-mcp.json is valid JSON", True)

    # Schema: { "mcpServers": { "hexstrike-ai": { "command": ..., "args": [...], "timeout": ... } } }
    servers = cfg.get("mcpServers", {})
    has_key = "hexstrike-ai" in servers
    _check(section, "mcpServers.hexstrike-ai key present", has_key,
           f"keys found: {list(servers.keys())}")

    if has_key:
        entry = servers["hexstrike-ai"]
        for required_key in ("command", "args", "timeout"):
            present = required_key in entry
            _check(section, f"mcpServers.hexstrike-ai.{required_key} present", present,
                   warn_on_fail=not present)

        # Check that the script path in args actually exists
        args = entry.get("args", [])
        for arg in args:
            if arg.endswith(".py"):
                p = Path(arg)
                if not p.is_absolute():
                    p = SCRIPT_DIR / arg
                _check(section, f"MCP arg script path exists: {arg}",
                       p.exists(), str(p), warn_on_fail=True)


def check_requirements_txt(section: str) -> None:
    """Verify requirements.txt is parseable."""
    if not REQUIREMENTS_PATH.exists():
        _check(section, "requirements.txt exists", False)
        return
    _check(section, "requirements.txt exists", True)
    pkgs = _parse_requirements()
    _check(section, "requirements.txt is parseable (>0 packages)", len(pkgs) > 0,
           f"{len(pkgs)} packages found")


# ===========================================================================
# SECTION 3 – Server Health & Functionality Testing
# ===========================================================================

def check_module_imports(section: str) -> None:
    """Try importing hexstrike_server and hexstrike_mcp."""
    for module_file in ("hexstrike_server", "hexstrike_mcp"):
        path = SCRIPT_DIR / f"{module_file}.py"
        if not path.exists():
            _check(section, f"Import {module_file}", False, "File not found")
            continue
        spec = importlib.util.spec_from_file_location(module_file, path)
        loader = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        try:
            spec.loader.exec_module(loader)  # type: ignore[union-attr]
            _check(section, f"Import {module_file}", True)
        except Exception as exc:
            tb = traceback.format_exc()
            _check(section, f"Import {module_file}", False,
                   f"{type(exc).__name__}: {exc}\n{tb}")


def check_syntax_all_py(section: str) -> None:
    """AST-parse every .py file in the project."""
    py_files = sorted(SCRIPT_DIR.glob("*.py"))
    if not py_files:
        _check(section, "Python source files found", False, "No .py files in project root")
        return

    all_ok = True
    for pyfile in py_files:
        try:
            source = pyfile.read_text(encoding="utf-8", errors="replace")
            ast.parse(source, filename=str(pyfile))
            _check(section, f"Syntax OK: {pyfile.name}", True)
        except SyntaxError as exc:
            all_ok = False
            _check(section, f"Syntax OK: {pyfile.name}", False,
                   f"line {exc.lineno}: {exc.msg}")
        except Exception as exc:
            all_ok = False
            _check(section, f"Syntax OK: {pyfile.name}", False, str(exc))


def check_server_endpoints(section: str) -> None:
    """
    Start hexstrike_server.py in a subprocess on TEST_PORT, exercise the
    health/telemetry/cache/processes endpoints, then shut it down.
    """
    server_path = SCRIPT_DIR / "hexstrike_server.py"
    if not server_path.exists():
        _check(section, "hexstrike_server.py exists for endpoint testing", False)
        return

    if not _is_port_free(TEST_PORT):
        _warn(f"Test port {TEST_PORT} already in use — skipping live server tests")
        _record(section, f"Server start on port {TEST_PORT}", Result.SKIP,
                "Port already in use")
        return

    env = os.environ.copy()
    env["HEXSTRIKE_PORT"] = str(TEST_PORT)
    env["HEXSTRIKE_HOST"] = "127.0.0.1"

    _info(f"Starting hexstrike_server.py on port {TEST_PORT} …")
    proc: Optional[subprocess.Popen] = None
    try:
        proc = subprocess.Popen(
            [sys.executable, str(server_path)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait up to 15 s for the server to accept connections
        started = _wait_for_port("127.0.0.1", TEST_PORT, timeout=15)
        if not started:
            stderr_out = ""
            try:
                proc.terminate()
                _, stderr_bytes = proc.communicate(timeout=5)
                stderr_out = stderr_bytes.decode(errors="replace")
            except Exception:
                pass
            _check(section, f"Server started on port {TEST_PORT}", False,
                   f"Did not open port within 15 s. stderr:\n{stderr_out}")
            return

        _check(section, f"Server started on port {TEST_PORT}", True)

        base = f"http://127.0.0.1:{TEST_PORT}"
        _probe_endpoint(section, base, "/health", expect_key="status")
        _probe_endpoint(section, base, "/api/telemetry")
        _probe_endpoint(section, base, "/api/cache/stats")
        _probe_endpoint(section, base, "/api/processes/list")

    except Exception as exc:
        _check(section, f"Server start on port {TEST_PORT}", False,
               f"{type(exc).__name__}: {exc}")
    finally:
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=10)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            _info("Server subprocess stopped")


def _probe_endpoint(section: str, base: str, path: str,
                    expect_key: Optional[str] = None) -> None:
    """
    Issue a GET request to base+path and record the result.
    Uses only the standard-library urllib so requests is not required at
    import time (it may not be installed in all environments).
    """
    import urllib.request
    import urllib.error

    url = base + path
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = resp.read().decode(errors="replace")
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = None

            if expect_key and (data is None or expect_key not in data):
                _check(section, f"GET {path}", False,
                       f"Expected key '{expect_key}' not in response: {body[:120]}")
            else:
                _check(section, f"GET {path}", True,
                       f"HTTP {resp.status}")
    except Exception as exc:
        _check(section, f"GET {path}", False, str(exc))


# ===========================================================================
# SECTION 4 – Network & Port Diagnostics
# ===========================================================================

def check_network(section: str) -> None:
    """Check port 8888, Tor SOCKS proxy, and proxychains config."""
    # Default production port
    free = _is_port_free(DEFAULT_PORT)
    _check(section, f"Default port {DEFAULT_PORT} is free", free,
           "in use" if not free else "available", warn_on_fail=True)

    # Tor SOCKS proxy on 9050
    tor_up = _is_port_open("127.0.0.1", TOR_SOCKS_PORT, timeout=2)
    _check(section, f"Tor SOCKS proxy on port {TOR_SOCKS_PORT} reachable",
           tor_up, "reachable" if tor_up else "not reachable", warn_on_fail=True)

    # proxychains4 config
    if shutil.which("proxychains4") or tor_up:
        _check(section, f"proxychains4 config at {PROXYCHAINS_CONF}",
               PROXYCHAINS_CONF.exists(), str(PROXYCHAINS_CONF), warn_on_fail=True)


# ===========================================================================
# SECTION 5 – File Integrity Checks
# ===========================================================================

def check_file_integrity(section: str) -> None:
    """Verify expected files exist, are non-empty, and are valid UTF-8."""
    for fname in EXPECTED_FILES:
        fpath = SCRIPT_DIR / fname
        if not _check(section, f"File exists: {fname}", fpath.exists(), str(fpath)):
            continue

        size = fpath.stat().st_size
        if not _check(section, f"File non-empty: {fname}", size > 0,
                      f"{size} bytes"):
            continue

        try:
            fpath.read_text(encoding="utf-8")
            _check(section, f"File valid UTF-8: {fname}", True)
        except UnicodeDecodeError as exc:
            _check(section, f"File valid UTF-8: {fname}", False, str(exc),
                   warn_on_fail=True)


# ===========================================================================
# SECTION 6 – Production Readiness Checks
# ===========================================================================

def check_production_readiness(section: str) -> None:
    """Check debug mode, hardcoded secrets, logging, and system resources."""
    _check_debug_mode(section)
    _check_hardcoded_secrets(section)
    _check_logging_configured(section)
    _check_system_resources(section)


def _check_debug_mode(section: str) -> None:
    """Grep for Flask debug=True in source files."""
    debug_pattern = re.compile(r'\bapp\.run\s*\(.*\bdebug\s*=\s*True', re.IGNORECASE)
    found_debug = []
    for pyfile in SCRIPT_DIR.glob("*.py"):
        try:
            text = pyfile.read_text(encoding="utf-8", errors="replace")
            if debug_pattern.search(text):
                found_debug.append(pyfile.name)
        except Exception:
            pass
    _check(section, "Flask debug=True NOT in production source",
           len(found_debug) == 0,
           f"Found in: {found_debug}" if found_debug else "")


def _check_hardcoded_secrets(section: str) -> None:
    """Simple heuristic scan for hardcoded credentials in .py files."""
    hits: List[str] = []
    for pyfile in SCRIPT_DIR.glob("*.py"):
        # Skip this very script
        if pyfile.name == Path(__file__).name:
            continue
        try:
            text = pyfile.read_text(encoding="utf-8", errors="replace")
            for pattern in SECRET_PATTERNS:
                for m in pattern.finditer(text):
                    lineno = text[: m.start()].count("\n") + 1
                    hits.append(f"{pyfile.name}:{lineno}")
        except Exception:
            pass
    _check(section, "No hardcoded secrets/API keys detected",
           len(hits) == 0,
           f"Potential hits: {hits[:5]}" if hits else "",
           warn_on_fail=True)


def _check_logging_configured(section: str) -> None:
    """Verify hexstrike_server.py calls logging.basicConfig."""
    server = SCRIPT_DIR / "hexstrike_server.py"
    if not server.exists():
        _check(section, "Logging configured in hexstrike_server.py", False,
               "File not found", warn_on_fail=True)
        return
    text = server.read_text(encoding="utf-8", errors="replace")
    configured = "logging.basicConfig" in text or "logging.getLogger" in text
    _check(section, "Logging configured in hexstrike_server.py", configured,
           warn_on_fail=True)


def _check_system_resources(section: str) -> None:
    """Check disk space, RAM, and CPU count."""
    # Disk space (root filesystem, or SCRIPT_DIR's mount)
    try:
        import shutil as _shutil
        total, used, free = _shutil.disk_usage(str(SCRIPT_DIR))
        free_gb = free / (1024 ** 3)
        ok = free_gb >= 1.0
        _check(section, "Disk space ≥ 1 GB free", ok,
               f"{free_gb:.1f} GB free", warn_on_fail=True)
    except Exception as exc:
        _check(section, "Disk space check", False, str(exc), warn_on_fail=True)

    # RAM
    try:
        import psutil as _psutil
        vm = _psutil.virtual_memory()
        total_gb = vm.total / (1024 ** 3)
        avail_gb = vm.available / (1024 ** 3)
        ok = avail_gb >= 0.5
        _check(section, "Available RAM ≥ 512 MB", ok,
               f"{avail_gb:.1f} GB available / {total_gb:.1f} GB total",
               warn_on_fail=True)
    except ImportError:
        _warn("psutil not available — skipping RAM check")
        _record(section, "Available RAM check", Result.SKIP, "psutil not installed")
    except Exception as exc:
        _check(section, "RAM check", False, str(exc), warn_on_fail=True)

    # CPU count
    try:
        cpus = os.cpu_count() or 1
        _check(section, "CPU count ≥ 1", cpus >= 1, f"{cpus} logical CPU(s)",
               warn_on_fail=True)
    except Exception as exc:
        _check(section, "CPU count", False, str(exc), warn_on_fail=True)


# ===========================================================================
# Helpers
# ===========================================================================

def _parse_requirements() -> List[str]:
    """
    Return a list of distribution package names from requirements.txt.
    Lines starting with # or empty lines are ignored.
    Version specifiers and extras are stripped.
    """
    packages: List[str] = []
    try:
        for raw_line in REQUIREMENTS_PATH.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            # Strip inline comment
            line = line.split("#")[0].strip()
            if not line:
                continue
            # Strip version specifiers: pkg>=1.0,<2.0 -> pkg
            pkg = re.split(r"[>=<!;\[\s]", line)[0].strip()
            if pkg:
                packages.append(pkg.lower())
    except Exception:
        pass
    return packages


def _is_port_free(port: int, host: str = "127.0.0.1") -> bool:
    """Return True if *port* is not currently bound on *host*."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def _is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """Return True if a TCP connection to host:port can be established."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False


def _wait_for_port(host: str, port: int, timeout: float = 15.0,
                   interval: float = 0.5) -> bool:
    """Poll until host:port accepts a connection or *timeout* seconds elapse."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _is_port_open(host, port, timeout=0.5):
            return True
        time.sleep(interval)
    return False


# ===========================================================================
# Reporting
# ===========================================================================

def _print_summary() -> Tuple[int, int, int, int]:
    """Print a summary table and return (total, passed, failed, warned)."""
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["status"] == Result.PASS)
    failed = sum(1 for r in RESULTS if r["status"] == Result.FAIL)
    warned = sum(1 for r in RESULTS if r["status"] == Result.WARN)
    skipped = sum(1 for r in RESULTS if r["status"] == Result.SKIP)

    width = 62
    print(f"\n{_c(RED)}{_c(BOLD)}{'═' * width}{_c(RESET)}")
    print(f"{_c(RED)}{_c(BOLD)}  DIAGNOSTIC SUMMARY{_c(RESET)}")
    print(f"{_c(RED)}{_c(BOLD)}{'═' * width}{_c(RESET)}\n")
    print(f"  Total checks : {_c(BOLD)}{total}{_c(RESET)}")
    print(f"  {_c(GREEN)}Passed{_c(RESET)}       : {_c(GREEN)}{_c(BOLD)}{passed}{_c(RESET)}")
    print(f"  {_c(RED)}Failed{_c(RESET)}       : {_c(RED)}{_c(BOLD)}{failed}{_c(RESET)}")
    print(f"  {_c(YELLOW)}Warnings{_c(RESET)}     : {_c(YELLOW)}{_c(BOLD)}{warned}{_c(RESET)}")
    print(f"  {_c(CYAN)}Skipped{_c(RESET)}      : {_c(CYAN)}{_c(BOLD)}{skipped}{_c(RESET)}")

    if failed == 0:
        print(f"\n  {_c(GREEN)}{_c(BOLD)}✔ All critical checks passed — production ready!{_c(RESET)}")
    else:
        print(f"\n  {_c(RED)}{_c(BOLD)}✘ {failed} critical check(s) failed — review output above.{_c(RESET)}")

    print(f"{_c(RED)}{_c(BOLD)}{'═' * width}{_c(RESET)}\n")
    return total, passed, failed, warned


def _output_json() -> None:
    """Emit JSON results to stdout."""
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["status"] == Result.PASS)
    failed = sum(1 for r in RESULTS if r["status"] == Result.FAIL)
    warned = sum(1 for r in RESULTS if r["status"] == Result.WARN)
    skipped = sum(1 for r in RESULTS if r["status"] == Result.SKIP)
    payload = {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "warnings": warned,
            "skipped": skipped,
            "production_ready": failed == 0,
        },
        "checks": RESULTS,
    }
    print(json.dumps(payload, indent=2))


def _banner() -> None:
    print(f"""
{_c(RED)}{_c(BOLD)}
 ██╗  ██╗███████╗██╗  ██╗███████╗████████╗██████╗ ██╗██╗  ██╗███████╗
 ██║  ██║██╔════╝╚██╗██╔╝██╔════╝╚══██╔══╝██╔══██╗██║██║ ██╔╝██╔════╝
 ███████║█████╗   ╚███╔╝ ███████╗   ██║   ██████╔╝██║█████╔╝ █████╗
 ██╔══██║██╔══╝   ██╔██╗ ╚════██║   ██║   ██╔══██╗██║██╔═██╗ ██╔══╝
 ██║  ██║███████╗██╔╝ ██╗███████║   ██║   ██║  ██║██║██║  ██╗███████╗
 ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝
{_c(RESET)}
{_c(CYAN)}{_c(BOLD)}  🔍 HexStrike AI — Debug & Production-Readiness Diagnostic{_c(RESET)}
{_c(YELLOW)}  v6.0 — github.com/bitbybit91/hexstrike-ai-dn{_c(RESET)}
""")


# ===========================================================================
# Main
# ===========================================================================

def main() -> int:
    global _USE_COLOR

    parser = argparse.ArgumentParser(
        description="HexStrike AI debug & production-readiness diagnostic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (disables colour, suitable for CI/CD)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to auto-fix common issues (e.g. install missing pip packages)",
    )
    parser.add_argument(
        "--skip-server",
        action="store_true",
        help="Skip the live server endpoint tests (faster, no subprocess spawned)",
    )
    args = parser.parse_args()

    # Disable colour for JSON mode or non-TTY stdout
    if args.json or not sys.stdout.isatty():
        _USE_COLOR = False

    if not args.json:
        _banner()

    # ------------------------------------------------------------------
    # Section 1: Environment & Dependency Validation
    # ------------------------------------------------------------------
    if not args.json:
        _section("1 · Environment & Dependency Validation")
    s = "environment"
    check_python_version(s)
    check_pip_packages(s, fix=args.fix)
    check_venv(s)
    check_system_tools(s)

    # ------------------------------------------------------------------
    # Section 2: Configuration Validation
    # ------------------------------------------------------------------
    if not args.json:
        _section("2 · Configuration Validation")
    s = "configuration"
    check_mcp_config(s)
    check_requirements_txt(s)

    # ------------------------------------------------------------------
    # Section 3: Server Health & Functionality Testing
    # ------------------------------------------------------------------
    if not args.json:
        _section("3 · Server Health & Functionality Testing")
    s = "server"
    check_syntax_all_py(s)
    if not args.skip_server:
        check_server_endpoints(s)
    else:
        _info("Skipping live server tests (--skip-server)")
        _record(s, "Live server endpoint tests", Result.SKIP, "--skip-server flag set")

    # ------------------------------------------------------------------
    # Section 4: Network & Port Diagnostics
    # ------------------------------------------------------------------
    if not args.json:
        _section("4 · Network & Port Diagnostics")
    s = "network"
    check_network(s)

    # ------------------------------------------------------------------
    # Section 5: File Integrity Checks
    # ------------------------------------------------------------------
    if not args.json:
        _section("5 · File Integrity Checks")
    s = "file_integrity"
    check_file_integrity(s)

    # ------------------------------------------------------------------
    # Section 6: Production Readiness Checks
    # ------------------------------------------------------------------
    if not args.json:
        _section("6 · Production Readiness Checks")
    s = "production"
    check_production_readiness(s)

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    if args.json:
        _output_json()
        failed = sum(1 for r in RESULTS if r["status"] == Result.FAIL)
        return 1 if failed > 0 else 0
    else:
        _, _, failed, _ = _print_summary()
        return 1 if failed > 0 else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # pragma: no cover – script-level safety net
        print(f"\n{RED}{BOLD}[FATAL] The debug script itself encountered an unexpected error:{RESET}")
        print(f"{YELLOW}{traceback.format_exc()}{RESET}")
        sys.exit(2)
