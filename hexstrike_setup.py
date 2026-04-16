#!/usr/bin/env python3
"""
HexStrike AI - Automated Kali Linux Setup & Hidden Service Pentesting

Automates the full installation of HexStrike AI on Kali Linux, including:
  - System package dependencies
  - Python virtual environment and pip packages
  - Go-based security tools (subfinder, httpx, nuclei, etc.)
  - Tor, proxychains-ng, and torsocks for hidden service pentesting
  - Configuration generation for Tor SOCKS proxy routing
  - Verification of all installed components

Usage:
    sudo python3 hexstrike_setup.py              # Full setup
    sudo python3 hexstrike_setup.py --verify      # Verify installation
    sudo python3 hexstrike_setup.py --tor-only    # Setup Tor/proxychains only
    sudo python3 hexstrike_setup.py --tools-only  # Install security tools only

⚠️ Legal Notice: Only use on systems you own or have explicit written
   authorization to test. Unauthorized access is illegal.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
import textwrap
from pathlib import Path


# ============================================================================
# CONSTANTS
# ============================================================================

SCRIPT_DIR = Path(__file__).resolve().parent
VENV_DIR = SCRIPT_DIR / "hexstrike-env"
RESULTS_DIR = SCRIPT_DIR / "results"
PROXYCHAINS_CONF = Path("/etc/proxychains4.conf")
TORRC_PATH = Path("/etc/tor/torrc")

# ANSI colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# ============================================================================
# APT PACKAGES
# ============================================================================

APT_CORE = [
    "python3",
    "python3-pip",
    "python3-venv",
    "git",
    "curl",
    "wget",
    "build-essential",
    "libssl-dev",
    "libffi-dev",
    "python3-dev",
]

APT_SECURITY_TOOLS = [
    # Network & Recon
    "nmap",
    "masscan",
    "fierce",
    "dnsenum",
    "theharvester",
    "responder",
    "enum4linux",
    "nbtscan",
    "arp-scan",
    # Web Application
    "gobuster",
    "dirb",
    "nikto",
    "sqlmap",
    "wpscan",
    "wafw00f",
    "whatweb",
    # Password & Auth
    "hydra",
    "john",
    "hashcat",
    "medusa",
    "hashid",
    "ophcrack",
    # Binary & RE
    "gdb",
    "radare2",
    "binwalk",
    "checksec",
    "upx-ucl",
    "exiftool",
    # Forensics & Stego
    "foremost",
    "steghide",
    "testdisk",
    "scalpel",
    "bulk-extractor",
    "sleuthkit",
    # Misc
    "jq",
    "chromium",
    "chromium-driver",
    "seclists",
    "wordlists",
]

APT_TOR_PACKAGES = [
    "tor",
    "torsocks",
    "proxychains4",
    "nyx",
]

# Go tools: (binary name, go install path)
GO_TOOLS = [
    ("subfinder", "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"),
    ("httpx", "github.com/projectdiscovery/httpx/cmd/httpx@latest"),
    ("nuclei", "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"),
    ("katana", "github.com/projectdiscovery/katana/cmd/katana@latest"),
    ("ffuf", "github.com/ffuf/ffuf/v2@latest"),
    ("feroxbuster", None),  # installed via apt or cargo
    ("gau", "github.com/lc/gau/v2/cmd/gau@latest"),
    ("hakrawler", "github.com/hakluke/hakrawler@latest"),
    ("anew", "github.com/tomnomnom/anew@latest"),
    ("qsreplace", "github.com/tomnomnom/qsreplace@latest"),
    ("waybackurls", "github.com/tomnomnom/waybackurls@latest"),
]


# ============================================================================
# HELPERS
# ============================================================================

def banner():
    print(f"""
{RED}{BOLD}
 ██╗  ██╗███████╗██╗  ██╗███████╗████████╗██████╗ ██╗██╗  ██╗███████╗
 ██║  ██║██╔════╝╚██╗██╔╝██╔════╝╚══██╔══╝██╔══██╗██║██║ ██╔╝██╔════╝
 ███████║█████╗   ╚███╔╝ ███████╗   ██║   ██████╔╝██║█████╔╝ █████╗
 ██╔══██║██╔══╝   ██╔██╗ ╚════██║   ██║   ██╔══██╗██║██╔═██╗ ██╔══╝
 ██║  ██║███████╗██╔╝ ██╗███████║   ██║   ██║  ██║██║██║  ██╗███████╗
 ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝
{RESET}
{CYAN}{BOLD}  ⚡ Automated Kali Linux Setup & Hidden Service Pentesting ⚡{RESET}
{YELLOW}  HexStrike AI v6.0 — github.com/0x4m4/hexstrike-ai{RESET}
""")


def log_info(msg):
    print(f"  {CYAN}[*]{RESET} {msg}")


def log_ok(msg):
    print(f"  {GREEN}[✔]{RESET} {msg}")


def log_warn(msg):
    print(f"  {YELLOW}[!]{RESET} {msg}")


def log_err(msg):
    print(f"  {RED}[✘]{RESET} {msg}")


def log_section(title):
    width = 60
    print(f"\n{RED}{BOLD}{'═' * width}{RESET}")
    print(f"{RED}{BOLD}  {title}{RESET}")
    print(f"{RED}{BOLD}{'═' * width}{RESET}\n")


def run(cmd, check=True, capture=False, env=None):
    """Run a shell command with optional output capture."""
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    try:
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            check=check,
            capture_output=capture,
            text=True,
            env=merged_env,
            timeout=600,
        )
        return result
    except subprocess.CalledProcessError as exc:
        if check:
            log_err(f"Command failed: {cmd}")
            if capture and exc.stderr:
                for line in exc.stderr.strip().splitlines()[:5]:
                    log_err(f"  {line}")
        return exc
    except subprocess.TimeoutExpired:
        log_warn(f"Command timed out: {cmd}")
        return None


def is_root():
    return os.geteuid() == 0


def which(binary):
    return shutil.which(binary) is not None


# ============================================================================
# INSTALLATION STEPS
# ============================================================================

def check_platform():
    """Verify we are on a Debian/Kali system."""
    log_section("Platform Check")
    if not Path("/etc/debian_version").exists():
        log_warn("This script is designed for Debian/Kali Linux.")
        log_warn("Proceeding anyway — some packages may not be available.")
    else:
        try:
            os_release = Path("/etc/os-release").read_text()
        except OSError:
            os_release = ""
        if "kali" in os_release.lower():
            log_ok("Detected Kali Linux")
        else:
            log_ok("Detected Debian-based system")


def install_apt_packages(packages, label="packages"):
    """Install a list of apt packages, skipping unavailable ones."""
    log_info(f"Installing {label} ({len(packages)} packages)...")
    run("apt-get update -qq", check=False)

    failed = []
    for pkg in packages:
        result = run(
            f"apt-get install -y -qq {pkg}",
            check=False,
            capture=True,
        )
        if isinstance(result, subprocess.CalledProcessError) or result is None:
            failed.append(pkg)
        else:
            log_ok(f"  {pkg}")

    if failed:
        log_warn(f"Could not install: {', '.join(failed)}")
        log_warn("Install them manually or from their upstream sources.")
    return failed


def setup_python_venv():
    """Create the Python virtual environment and install pip deps."""
    log_section("Python Environment")

    if VENV_DIR.exists():
        log_info(f"Virtual environment already exists at {VENV_DIR}")
    else:
        log_info(f"Creating virtual environment at {VENV_DIR}")
        run(f"python3 -m venv {VENV_DIR}")

    pip = VENV_DIR / "bin" / "pip"
    log_info("Upgrading pip...")
    run(f"{pip} install --upgrade pip setuptools wheel", capture=True, check=False)

    req_file = SCRIPT_DIR / "requirements.txt"
    if req_file.exists():
        log_info("Installing Python dependencies from requirements.txt...")
        result = run(f"{pip} install -r {req_file}", check=False, capture=True)
        if isinstance(result, subprocess.CalledProcessError):
            log_warn("Some Python packages failed — check requirements.txt")
        else:
            log_ok("Python dependencies installed")
    else:
        log_warn("requirements.txt not found — skipping pip install")

    log_ok(f"Activate with: source {VENV_DIR}/bin/activate")


def install_go_tools():
    """Install Go-based security tools."""
    log_section("Go-Based Security Tools")

    if not which("go"):
        log_info("Go not found — installing golang...")
        run("apt-get install -y -qq golang", check=False)

    if not which("go"):
        log_warn("Go installation failed. Skipping Go tools.")
        return

    go_bin = Path.home() / "go" / "bin"
    go_env = {"GOPATH": str(Path.home() / "go"), "GOBIN": str(go_bin)}

    for binary, install_path in GO_TOOLS:
        if install_path is None:
            # Try apt fallback (e.g., feroxbuster)
            if not which(binary):
                run(f"apt-get install -y -qq {binary}", check=False, capture=True)
            if which(binary):
                log_ok(f"  {binary} (apt)")
            else:
                log_warn(f"  {binary} — not available via apt or go")
            continue

        if which(binary) or (go_bin / binary).exists():
            log_ok(f"  {binary} (already installed)")
            continue

        log_info(f"  Installing {binary}...")
        result = run(
            f"go install {install_path}",
            check=False,
            capture=True,
            env=go_env,
        )
        if result and not isinstance(result, subprocess.CalledProcessError):
            log_ok(f"  {binary}")
        else:
            log_warn(f"  {binary} — go install failed")

    # Ensure go/bin is on PATH
    profile_line = f'export PATH="$PATH:{go_bin}"'
    bashrc = Path.home() / ".bashrc"
    try:
        existing = bashrc.read_text() if bashrc.exists() else ""
        if str(go_bin) not in existing:
            with open(bashrc, "a") as fh:
                fh.write(f"\n# HexStrike Go tools\n{profile_line}\n")
            log_ok(f"Added {go_bin} to PATH in ~/.bashrc")
    except OSError:
        log_warn("Could not update ~/.bashrc — add Go bin to PATH manually")


def install_rustscan():
    """Install RustScan from GitHub releases."""
    log_section("RustScan")
    if which("rustscan"):
        log_ok("RustScan already installed")
        return
    log_info("Downloading RustScan .deb...")
    url = (
        "https://github.com/RustScan/RustScan/releases/download/2.3.0/"
        "rustscan_2.3.0_amd64.deb"
    )
    deb = "/tmp/rustscan.deb"
    result = run(f"wget -q -O {deb} {url}", check=False, capture=True)
    if result and not isinstance(result, subprocess.CalledProcessError):
        run(f"dpkg -i {deb}", check=False, capture=True)
        run("apt-get install -f -y -qq", check=False, capture=True)
        if which("rustscan"):
            log_ok("RustScan installed")
        else:
            log_warn("RustScan installation failed")
    else:
        log_warn("Could not download RustScan — install manually")


# ============================================================================
# TOR & HIDDEN SERVICE PENTESTING
# ============================================================================

def setup_tor():
    """Install and configure Tor, proxychains, and torsocks."""
    log_section("Tor & Hidden Service Pentesting Setup")

    # 1. Install packages
    install_apt_packages(APT_TOR_PACKAGES, label="Tor packages")

    # 2. Configure Tor
    configure_torrc()

    # 3. Configure proxychains
    configure_proxychains()

    # 4. Enable and start Tor service
    log_info("Enabling and starting Tor service...")
    run("systemctl enable tor", check=False, capture=True)
    run("systemctl restart tor", check=False, capture=True)

    # Wait briefly for Tor to bootstrap
    log_info("Waiting for Tor to bootstrap...")
    time.sleep(5)

    # Verify Tor is running
    result = run("systemctl is-active tor", check=False, capture=True)
    if result and hasattr(result, "stdout") and "active" in result.stdout.strip():
        log_ok("Tor service is active")
    else:
        log_warn("Tor service may not be running — check: systemctl status tor")

    # 5. Print usage examples
    print_tor_usage()


def configure_torrc():
    """Write a pentesting-friendly torrc configuration."""
    log_info("Configuring Tor (torrc)...")

    torrc_content = textwrap.dedent("""\
        ## HexStrike AI — Tor Configuration for Pentesting
        ## Generated by hexstrike_setup.py

        # SOCKS proxy for local tools
        SocksPort 9050
        # Additional SOCKS port for parallel sessions
        SocksPort 9052

        # DNS resolution over Tor
        DNSPort 5353
        AutomapHostsOnResolve 1

        # Allow .onion resolution
        AutomapHostsSuffixes .onion,.exit

        # Transparent proxy (optional — used by some iptables setups)
        TransPort 9040

        # Logging
        Log notice file /var/log/tor/notices.log

        # Circuit settings for pentesting
        MaxCircuitDirtiness 600
        NewCircuitPeriod 30
        CircuitBuildTimeout 30

        # Safety: reject connections from non-localhost
        SocksPolicy accept 127.0.0.1
        SocksPolicy reject *
    """)

    backup = TORRC_PATH.with_suffix(".bak")
    try:
        if TORRC_PATH.exists() and not backup.exists():
            shutil.copy2(TORRC_PATH, backup)
            log_info(f"Backed up original torrc to {backup}")
        TORRC_PATH.write_text(torrc_content)
        log_ok("torrc configured")
    except OSError as exc:
        log_err(f"Failed to write torrc: {exc}")


def configure_proxychains():
    """Write a proxychains4 config that routes through Tor."""
    log_info("Configuring proxychains4...")

    proxychains_content = textwrap.dedent("""\
        ## HexStrike AI — proxychains4 configuration
        ## Generated by hexstrike_setup.py
        ##
        ## Usage:
        ##   proxychains4 nmap -sT -Pn <target.onion>
        ##   proxychains4 curl http://<target.onion>
        ##   proxychains4 python3 hexstrike_server.py

        # Use dynamic_chain for better reliability
        dynamic_chain

        # Quiet mode — suppress DNS/connection messages
        quiet_mode

        # Proxy DNS through the proxy chain
        proxy_dns

        # Timeouts (ms)
        tcp_read_time_out 30000
        tcp_connect_time_out 15000

        # Proxy list — route through Tor SOCKS5
        [ProxyList]
        socks5 127.0.0.1 9050
    """)

    backup = PROXYCHAINS_CONF.with_suffix(".bak")
    try:
        if PROXYCHAINS_CONF.exists() and not backup.exists():
            shutil.copy2(PROXYCHAINS_CONF, backup)
            log_info(f"Backed up original proxychains config to {backup}")
        PROXYCHAINS_CONF.write_text(proxychains_content)
        log_ok("proxychains4.conf configured")
    except OSError as exc:
        log_err(f"Failed to write proxychains config: {exc}")


def print_tor_usage():
    """Print a usage guide for hidden service pentesting."""
    print(f"""
{CYAN}{BOLD}┌──────────────────────────────────────────────────────────────┐
│           Hidden Service Pentesting — Quick Reference       │
├──────────────────────────────────────────────────────────────┤{RESET}
│                                                              │
│  {GREEN}Scan an .onion target:{RESET}                                      │
│    proxychains4 nmap -sT -Pn -n <target>.onion               │
│                                                              │
│  {GREEN}HTTP requests through Tor:{RESET}                                  │
│    proxychains4 curl http://<target>.onion                    │
│    torsocks curl http://<target>.onion                        │
│                                                              │
│  {GREEN}Web directory bruteforce:{RESET}                                   │
│    proxychains4 gobuster dir -u http://<target>.onion \\       │
│      -w /usr/share/wordlists/dirb/common.txt                 │
│                                                              │
│  {GREEN}SQLMap through Tor:{RESET}                                         │
│    sqlmap -u "http://<target>.onion/page?id=1" \\              │
│      --proxy="socks5://127.0.0.1:9050" --tor --check-tor     │
│                                                              │
│  {GREEN}Nikto through Tor:{RESET}                                          │
│    proxychains4 nikto -h http://<target>.onion                │
│                                                              │
│  {GREEN}Run HexStrike server through Tor:{RESET}                           │
│    source hexstrike-env/bin/activate                          │
│    proxychains4 python3 hexstrike_server.py                   │
│                                                              │
│  {GREEN}Verify Tor connectivity:{RESET}                                    │
│    torsocks curl -s https://check.torproject.org/api/ip       │
│                                                              │
│  {GREEN}New Tor identity (new IP):{RESET}                                  │
│    sudo systemctl reload tor                                  │
│                                                              │
│  {YELLOW}⚠  Only test .onion services you own or have written{RESET}       │
│  {YELLOW}   authorization to test.{RESET}                                  │
│                                                              │
{CYAN}{BOLD}└──────────────────────────────────────────────────────────────┘{RESET}
""")


# ============================================================================
# VERIFICATION
# ============================================================================

def verify_installation():
    """Check that key components are installed and working."""
    log_section("Installation Verification")

    checks = {
        "Python 3": ("python3 --version", None),
        "pip": (f"{VENV_DIR / 'bin' / 'pip'} --version", None),
        "Flask (venv)": (f"{VENV_DIR / 'bin' / 'python'} -c \"import flask\"", None),
        "Nmap": ("nmap --version", "nmap"),
        "Gobuster": ("gobuster version", "gobuster"),
        "SQLMap": ("sqlmap --version", "sqlmap"),
        "Nikto": ("nikto -Version", "nikto"),
        "Hydra": ("hydra -h", "hydra"),
        "John": ("john --help", "john"),
        "Nuclei": ("nuclei -version", "nuclei"),
        "Subfinder": ("subfinder -version", "subfinder"),
        "HTTPx": ("httpx -version", "httpx"),
        "FFuf": ("ffuf -V", "ffuf"),
        "RustScan": ("rustscan --version", "rustscan"),
        "Tor": ("tor --version", "tor"),
        "Proxychains4": ("proxychains4 -h", "proxychains4"),
        "Torsocks": ("torsocks --version", "torsocks"),
        "GDB": ("gdb --version", "gdb"),
        "Radare2": ("r2 -v", "r2"),
        "Binwalk": ("binwalk --help", "binwalk"),
    }

    installed = 0
    missing = []

    for name, (cmd, binary) in checks.items():
        if binary and not which(binary):
            log_warn(f"  {name}: not found in PATH")
            missing.append(name)
            continue
        result = run(cmd, check=False, capture=True)
        if result and not isinstance(result, subprocess.CalledProcessError):
            log_ok(f"  {name}")
            installed += 1
        else:
            log_warn(f"  {name}: check failed")
            missing.append(name)

    total = len(checks)
    print(f"\n  {GREEN}{BOLD}Results: {installed}/{total} verified{RESET}")
    if missing:
        print(f"  {YELLOW}Missing/failed: {', '.join(missing)}{RESET}")

    # Check Tor connectivity
    log_info("Checking Tor connectivity...")
    result = run(
        "torsocks curl -s --max-time 15 https://check.torproject.org/api/ip",
        check=False,
        capture=True,
    )
    if result and hasattr(result, "stdout") and "true" in result.stdout.lower():
        log_ok("Tor connectivity verified — traffic is routed through Tor")
    else:
        log_warn("Tor connectivity check failed — Tor may still be bootstrapping")

    return installed, missing


def create_results_directory():
    """Create a directory for scan results."""
    RESULTS_DIR.mkdir(exist_ok=True)
    log_ok(f"Results directory: {RESULTS_DIR}")


# ============================================================================
# MAIN
# ============================================================================

def full_setup():
    """Run the complete setup pipeline."""
    banner()

    if not is_root():
        log_err("This script must be run as root (sudo).")
        log_err("Usage: sudo python3 hexstrike_setup.py")
        sys.exit(1)

    check_platform()

    # 1. Core system packages
    log_section("Core System Packages")
    install_apt_packages(APT_CORE, label="core system packages")

    # 2. Security tools via apt
    log_section("Security Tools (apt)")
    install_apt_packages(APT_SECURITY_TOOLS, label="security tools")

    # 3. Python environment
    setup_python_venv()

    # 4. Go tools
    install_go_tools()

    # 5. RustScan
    install_rustscan()

    # 6. Tor & hidden service setup
    setup_tor()

    # 7. Results directory
    create_results_directory()

    # 8. Verify
    installed, missing = verify_installation()

    # Final summary
    log_section("Setup Complete")
    log_ok("HexStrike AI environment is ready!")
    print(f"""
  {CYAN}To start HexStrike:{RESET}
    cd {SCRIPT_DIR}
    source hexstrike-env/bin/activate
    python3 hexstrike_server.py

  {CYAN}To pentest hidden services:{RESET}
    proxychains4 python3 hexstrike_server.py

  {CYAN}To verify installation later:{RESET}
    sudo python3 hexstrike_setup.py --verify
""")


def main():
    parser = argparse.ArgumentParser(
        description="HexStrike AI — Automated Kali Linux Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              sudo python3 hexstrike_setup.py              # Full setup
              sudo python3 hexstrike_setup.py --verify      # Verify only
              sudo python3 hexstrike_setup.py --tor-only    # Tor setup only
              sudo python3 hexstrike_setup.py --tools-only  # Security tools only

            ⚠️  Always obtain proper authorization before testing any system.
        """),
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify installation without installing anything",
    )
    parser.add_argument(
        "--tor-only",
        action="store_true",
        help="Only install and configure Tor/proxychains/torsocks",
    )
    parser.add_argument(
        "--tools-only",
        action="store_true",
        help="Only install security tools (apt + Go)",
    )
    args = parser.parse_args()

    if args.verify:
        banner()
        verify_installation()
    elif args.tor_only:
        banner()
        if not is_root():
            log_err("Root required. Run with sudo.")
            sys.exit(1)
        setup_tor()
        log_ok("Tor setup complete!")
    elif args.tools_only:
        banner()
        if not is_root():
            log_err("Root required. Run with sudo.")
            sys.exit(1)
        log_section("Security Tools (apt)")
        install_apt_packages(APT_SECURITY_TOOLS, label="security tools")
        install_go_tools()
        install_rustscan()
        log_ok("Tool installation complete!")
    else:
        full_setup()


if __name__ == "__main__":
    main()
