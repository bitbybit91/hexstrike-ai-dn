<!-- HexStrike AI DN — VPS Edition README -->
<div align="center">

<img src="assets/hexstrike-logo.png" alt="HexStrike AI Logo" width="220" style="margin-bottom: 20px;"/>

# HexStrike AI DN — VPS Edition
### Autonomous Pentesting via Telegram · Venice AI · Tor · 150+ Tools

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Penetration%20Testing-red.svg)](https://github.com/bitbybit91/hexstrike-ai-dn)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-purple.svg)](https://github.com/bitbybit91/hexstrike-ai-dn)
[![Version](https://img.shields.io/badge/Version-6.0.0-orange.svg)](https://github.com/bitbybit91/hexstrike-ai-dn)
[![Tools](https://img.shields.io/badge/Security%20Tools-150%2B-brightgreen.svg)](https://github.com/bitbybit91/hexstrike-ai-dn)
[![Tor](https://img.shields.io/badge/Network-Tor%20Anonymized-7D4698.svg)](https://www.torproject.org/)

**Headless Linux VPS deployment · No GUI · No Claude Desktop · Telegram C2 only**

[📋 Overview](#1-project-overview) • [⚙️ Prerequisites](#2-prerequisites) • [🖥️ VPS Setup](#3-vps-environment-setup-no-gui-required) • [🔧 Configuration](#4-configuration) • [🚀 Installation](#5-installation) • [🤖 Telegram Bot](#6-telegram-bot--command-reference) • [🧅 Tor Integration](#7-tor-integration) • [🏗️ Deployment](#8-build--deployment) • [🧪 Testing](#9-running-tests) • [🛠️ Troubleshooting](#10-common-issues--troubleshooting) • [📁 Structure](#11-project-structure)

</div>

---

> **⚠️ Legal Notice:** HexStrike AI DN is designed exclusively for authorised penetration testing, red team engagements, CTF competitions, and security research on systems you own or have explicit written permission to test. Unauthorised use against systems you do not own is illegal. The authors accept no liability for misuse.

---

## 1. Project Overview

HexStrike AI DN is a **fully headless, VPS-native offensive security automation platform** that turns a bare Linux server into a persistent, Tor-anonymised pentesting agent controllable entirely through Telegram.

There is no web UI, no desktop application, and no interactive prompts. Every command is issued via Telegram message; every result is returned as a Telegram reply or file attachment. The underlying intelligence layer is provided by **Venice AI** using **abliterated (uncensored) LLM models** — meaning the AI can reason about offensive security tasks without the content-filtering restrictions present in mainstream models.

### Key Features

| Feature | Detail |
|---------|--------|
| **Telegram C2 interface** | Send commands, receive structured output, and trigger multi-tool chains from any device |
| **Venice AI integration** | Abliterated models (`dolphin-2.9-llama3-70b`, `dolphin-mixtral-8x22b`, etc.) via the Venice AI API — no content filtering for security tasks |
| **Full Tor anonymisation** | All outbound traffic — tool executions, API calls, HTTP requests — routed through Tor via `torsocks` / SOCKS5 proxy |
| **150+ integrated tools** | Network scanning, web app testing, exploitation, OSINT, binary analysis, cloud auditing, password cracking, and more |
| **Headless VPS-native** | No display server required; persistent via `systemd` or `tmux`; survives reboots and SSH disconnects |
| **FastMCP architecture** | `hexstrike_server.py` (Flask REST API + tool handlers) + `hexstrike_mcp.py` (FastMCP bridge for LLM agents) |
| **Autonomous chaining** | Venice AI selects and chains tools based on target analysis — no manual step-by-step required |

### Full Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| API server | Flask 3.x |
| MCP bridge | FastMCP 0.2+ |
| LLM backend | Venice AI API (abliterated models) |
| C2 interface | python-telegram-bot v20+ |
| Traffic anonymisation | Tor + torsocks + SOCKS5 proxy |
| Browser automation | Chromium (headless) + Selenium 4 + ChromeDriver |
| HTTP proxy | mitmproxy 9+ |
| Binary analysis | pwntools 4.10+, angr 9.2+ |
| Async networking | aiohttp 3.8+ |
| HTML parsing | BeautifulSoup4 |

### Supported Operating Systems

| OS | Version |
|----|---------|
| Ubuntu | 22.04 LTS |
| Debian | 12 (Bookworm) |
| Kali Linux | 2024.1+ |

---

## 2. Prerequisites

Every prerequisite below must be present before beginning installation. Install them in the order listed.

### 2.1 System Packages

#### Python 3.11+

**Ubuntu 22.04 / Debian 12:**
```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
python3.11 --version   # Expected: Python 3.11.x
```

**Kali Linux 2024.1+:**
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
python3 --version      # Expected: Python 3.11.x or higher
```

#### Git

```bash
sudo apt install -y git
git --version          # Expected: git version 2.x.x
```

#### Tor

```bash
sudo apt install -y tor
sudo systemctl enable tor && sudo systemctl start tor
sudo systemctl status tor    # Expected: active (running)
```

#### torsocks

```bash
sudo apt install -y torsocks
torsocks --version     # Expected: torsocks version 2.x.x
```

#### tmux (for persistent sessions)

```bash
sudo apt install -y tmux
tmux -V                # Expected: tmux 3.x
```

#### UFW (firewall — Ubuntu/Debian only)

```bash
sudo apt install -y ufw
```

---

### 2.2 Venice AI API Key

Venice AI provides access to abliterated (uncensored) open-source LLM models via a standard OpenAI-compatible API.

1. Open a browser and navigate to **https://venice.ai**
2. Create an account or sign in
3. Click your avatar → **API Keys** → **Create API Key**
4. Copy the key — it is shown only once; store it securely
5. Note your preferred abliterated model ID (see [Section 4a](#4a-venice-ai-abliterated-models))

Verify the key works:
```bash
curl -s https://api.venice.ai/api/v1/models \
  -H "Authorization: Bearer YOUR_VENICE_API_KEY" | jq '.data[].id'
```

Expected output (sample):
```
"dolphin-2.9-llama3-70b"
"dolphin-mixtral-8x22b"
"dolphin-2.9.1-llama-3.1-8b"
"nous-hermes-2-mixtral-8x7b-dpo"
"llama-3.1-405b-akash"
```

---

### 2.3 Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Enter a display name, e.g., `HexStrike Operator`
4. Enter a username ending in `bot`, e.g., `hexstrike_op_bot`
5. BotFather replies with your token in the format `123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ`
6. Copy and store this token — it is your `TELEGRAM_BOT_TOKEN`

Verify the token:
```bash
curl -s https://api.telegram.org/bot<YOUR_TOKEN>/getMe | jq '.result.username'
```

Expected output:
```
"hexstrike_op_bot"
```

---

### 2.4 Telegram Chat ID

Your Chat ID is the numeric identifier of your personal Telegram account. The bot will reject all messages from any other Chat ID.

1. Send any message to your new bot
2. Run:
```bash
curl -s "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates" | jq '.result[0].message.chat.id'
```
3. The returned integer is your `TELEGRAM_AUTHORIZED_CHAT_ID`

---

### 2.5 Chrome/Chromium + ChromeDriver (Headless)

**Ubuntu 22.04 / Debian 12:**
```bash
sudo apt install -y chromium-browser chromium-chromedriver
chromium-browser --headless --no-sandbox --version
# Expected: Chromium 1xx.x.xxxx.xxx
```

**Kali Linux:**
```bash
sudo apt install -y chromium chromium-driver
chromium --headless --no-sandbox --version
```

---

### 2.6 External Security Tools (150+)

These are installed separately from the Python requirements. A complete automated install script is provided at `scripts/install_tools.sh`.

**Kali Linux 2024.1+ (most tools are pre-installed):**
```bash
sudo apt update && sudo apt install -y \
  nmap masscan rustscan amass subfinder theharvester fierce dnsenum \
  gobuster feroxbuster ffuf dirb dirsearch nikto sqlmap wpscan \
  hydra john hashcat medusa netexec enum4linux-ng evil-winrm \
  radare2 gdb binwalk ropgadget checksec volatility3 \
  steghide exiftool foremost scalpel testdisk photorec \
  responder \
  wafw00f whatweb nuclei httpx katana hakrawler gau \
  recon-ng maltego shodan \
  docker.io trivy
```

**Ubuntu 22.04 / Debian 12 (tools not in standard repos):**
```bash
# Install Go (required by many tools)
sudo apt install -y golang-go
export GOPATH="$HOME/go"
export PATH="$PATH:$GOPATH/bin"

# Go-based tools
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/owasp-amass/amass/v4/...@master
go install github.com/hakluke/hakrawler@latest
go install github.com/lc/gau/v2/cmd/gau@latest
go install github.com/ffuf/ffuf/v2@latest
go install github.com/OJ/gobuster/v3@latest

# Rust-based tools
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
cargo install rustscan

# Feroxbuster
curl -sL https://raw.githubusercontent.com/epi052/feroxbuster/main/install-nix.sh | bash

# Python-based tools
pip3 install dirsearch wpscan-python trufflesecurity checkov
pip3 install shodan censys

# Nuclei templates
nuclei -update-templates
```

---

## 3. VPS Environment Setup (No GUI Required)

### 3.1 Provision a Fresh VPS

**DigitalOcean CLI (`doctl`):**
```bash
# Install doctl
brew install doctl   # macOS  — or use the Linux binary
doctl auth init      # Paste your DO API token

# Create an Ubuntu 22.04 droplet (2 vCPU, 4 GB RAM recommended)
doctl compute droplet create hexstrike-vps \
  --image ubuntu-22-04-x64 \
  --size s-2vcpu-4gb \
  --region nyc3 \
  --ssh-keys $(doctl compute ssh-key list --format ID --no-header | head -1) \
  --wait
```

**Vultr CLI (`vultr-cli`):**
```bash
vultr-cli instance create \
  --os 1743 \         # Ubuntu 22.04 LTS ID
  --plan vc2-2c-4gb \
  --region ewr \
  --label hexstrike-vps
```

**Hetzner Cloud CLI (`hcloud`):**
```bash
hcloud server create \
  --name hexstrike-vps \
  --type cx21 \
  --image ubuntu-22.04 \
  --ssh-key ~/.ssh/id_rsa.pub
```

---

### 3.2 Initial Hardening

Log in as root, then run the following:

```bash
# 1. Create a non-root operator user
adduser hexstrike
usermod -aG sudo hexstrike

# 2. Copy SSH keys to the new user
rsync --archive --chown=hexstrike:hexstrike ~/.ssh /home/hexstrike

# 3. Disable password authentication and root SSH login
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl reload sshd

# 4. Enable UFW — allow only SSH and the MCP port
ufw allow OpenSSH
ufw allow 8888/tcp comment 'HexStrike MCP (localhost only — change if needed)'
ufw --force enable
ufw status verbose
```

> **Note:** Port 8888 is bound to `127.0.0.1` by default (`MCP_HOST=127.0.0.1` in `.env`), so exposing it via UFW is only required if you move it to a public interface. Keep it local unless you have a specific reason to expose it.

---

### 3.3 Install and Configure Tor

```bash
sudo apt install -y tor
```

Edit `/etc/tor/torrc` — add the following block:

```ini
# /etc/tor/torrc — HexStrike Tor configuration
SocksPort 9050              # SOCKS5 proxy for Python requests and torsocks
DNSPort 53                  # Tor-resolved DNS — prevents DNS leaks
TransPort 9040              # Transparent proxy port (optional, for iptables redirect)
AutomapHostsOnResolve 1
VirtualAddrNetworkIPv4 10.192.0.0/10
Log notice file /var/log/tor/notices.log
```

Restart and verify:
```bash
sudo systemctl restart tor
sudo systemctl enable tor
# Confirm Tor is routing traffic
torsocks curl -s https://check.torproject.org/api/ip
```

Expected output:
```json
{"IsTor":true,"IP":"185.220.xxx.xxx"}
```

---

### 3.4 Install Chromium in Headless Mode

No display server (X11/Wayland) is required for headless Chromium.

**Ubuntu 22.04:**
```bash
sudo apt install -y chromium-browser chromium-chromedriver
chromium-browser --headless --no-sandbox --disable-gpu --version
# Expected: Chromium 1xx.x.xxxx.xxx built on Ubuntu ...
```

**Kali Linux:**
```bash
sudo apt install -y chromium chromium-driver
chromium --headless --no-sandbox --disable-gpu --version
```

Verify ChromeDriver matches Chromium:
```bash
chromedriver --version       # Must match Chromium major version
chromium-browser --version   # or: chromium --version
```

---

### 3.5 Verify All Tools Are Present

Run the provided verification script:
```bash
bash scripts/tool_check.sh
```

The script checks every tool by name and reports missing ones:
```
[✔] nmap          found at /usr/bin/nmap
[✔] masscan       found at /usr/bin/masscan
[✔] nuclei        found at /home/hexstrike/go/bin/nuclei
[✗] rustscan      NOT FOUND — run: cargo install rustscan
...
[SUMMARY] 143/150 tools found. 7 missing — see above.
```

Fix any missing tools before proceeding.

---

## 4. Configuration

### 4.1 Environment Variables (`.env`)

Copy the template and fill in your values:

```bash
cp .env.example .env
nano .env
```

Full annotated `.env` file:

```dotenv
# ============================================================
# Venice AI
# ============================================================
VENICE_API_KEY=your_venice_api_key_here
# Abliterated model to use — see Section 4a for full list
VENICE_MODEL=dolphin-2.9-llama3-70b
VENICE_API_BASE=https://api.venice.ai/api/v1

# ============================================================
# Telegram Bot
# ============================================================
TELEGRAM_BOT_TOKEN=123456789:ABCDEF_your_bot_token_here
# Your personal Telegram chat ID — all other users are rejected
TELEGRAM_AUTHORIZED_CHAT_ID=987654321

# ============================================================
# HexStrike MCP Server
# ============================================================
# Bind to loopback — never expose to 0.0.0.0 unless behind a firewall
MCP_HOST=127.0.0.1
MCP_PORT=8888
# Generate with: openssl rand -hex 32
MCP_SECRET_KEY=replace_this_with_openssl_rand_hex_32_output

# ============================================================
# Tor
# ============================================================
TOR_SOCKS_HOST=127.0.0.1
TOR_SOCKS_PORT=9050
# Set to false only for local dev/testing without Tor
USE_TOR=true

# ============================================================
# Logging
# ============================================================
LOG_LEVEL=INFO
LOG_FILE=/var/log/hexstrike/hexstrike.log
```

Create the log directory:
```bash
sudo mkdir -p /var/log/hexstrike
sudo chown hexstrike:hexstrike /var/log/hexstrike
```

---

### 4a. Venice AI Abliterated Models

Abliterated models have had their refusal training removed, enabling them to reason about offensive security tasks without content-policy interruptions.

List available models via the API:
```bash
curl -s https://api.venice.ai/api/v1/models \
  -H "Authorization: Bearer $VENICE_API_KEY" | jq '.data[] | {id: .id, context: .context_length}'
```

**Currently available abliterated models and recommended use cases:**

| Model ID | Parameters | Best Use Case |
|----------|-----------|---------------|
| `dolphin-2.9-llama3-70b` | 70B | General pentesting reasoning, exploit chaining, report writing |
| `dolphin-mixtral-8x22b` | 8×22B MoE | Complex multi-step attack planning, CTF problem solving |
| `dolphin-2.9.1-llama-3.1-8b` | 8B | Fast interactive queries, command generation, quick pivots |
| `nous-hermes-2-mixtral-8x7b-dpo` | 8×7B MoE | OSINT analysis, social engineering script generation |
| `llama-3.1-405b-akash` | 405B | Deep vulnerability analysis, zero-day research reasoning |
| `mistral-31-24b` | 24B | Balanced performance — good for interactive Telegram sessions |

> **Recommendation:** Use `dolphin-2.9-llama3-70b` for most tasks. Fall back to the 8B model for low-latency Telegram interactions where speed matters more than depth.

Python example — direct Venice AI call over SOCKS5:
```python
import requests

proxies = {
    "http":  "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}

response = requests.post(
    "https://api.venice.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {VENICE_API_KEY}"},
    json={
        "model": "dolphin-2.9-llama3-70b",
        "messages": [
            {"role": "system", "content": "You are an expert offensive security engineer."},
            {"role": "user", "content": "Enumerate the attack surface for 10.10.10.1"},
        ],
        "temperature": 0.7,
    },
    proxies=proxies,
    timeout=120,
)
print(response.json()["choices"][0]["message"]["content"])
```

curl equivalent (without Tor for testing):
```bash
curl -s https://api.venice.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $VENICE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dolphin-2.9-llama3-70b",
    "messages": [
      {"role":"system","content":"You are an expert offensive security engineer."},
      {"role":"user","content":"List common SMB attack vectors."}
    ]
  }' | jq '.choices[0].message.content'
```

---

### 4.2 MCP Configuration File (`hexstrike-ai-mcp.json`)

This file tells the MCP host (Venice AI agent or any OpenAI-compatible client) how to launch `hexstrike_mcp.py` as a subprocess and which server to connect it to.

**Corrected production configuration:**

> **Note:** The path `/home/hexstrike/hexstrike-ai-dn/hexstrike_mcp.py` assumes the repository is cloned to the `hexstrike` user's home directory. If you use a different installation path, update this value accordingly in `hexstrike-ai-mcp.json`.

```json
{
  "mcpServers": {
    "hexstrike-ai": {
      "command": "python3",
      "args": [
        "/home/hexstrike/hexstrike-ai-dn/hexstrike_mcp.py",
        "--server",
        "http://127.0.0.1:8888"
      ],
      "description": "HexStrike AI v6.0 — Offensive Security Automation Platform. Set alwaysAllow to [] for manual approval of each tool call, or list specific tool names for autonomous execution.",
      "timeout": 300,
      "alwaysAllow": []
    }
  }
}
```

**Field reference:**

| Field | Description |
|-------|-------------|
| `command` | Python interpreter to use — must be the one with the venv activated, or the full venv path |
| `args[0]` | **Absolute path** to `hexstrike_mcp.py` on your VPS |
| `args[2]` | URL of the running `hexstrike_server.py` — must match `MCP_HOST:MCP_PORT` in `.env` |
| `timeout` | Seconds to wait for a tool response — 300s (5 min) is suitable for long-running scans |
| `alwaysAllow` | Tool names that execute without user confirmation. Empty `[]` = require approval for every call |

**How Venice AI replaces Claude/GPT:** Instead of routing tool calls through Claude Desktop or the OpenAI API, the `hexstrike_mcp.py` process is started directly by the Telegram bot (`telegram_bot.py`) or an autonomous Venice AI agent. The agent sends tool-call requests (e.g., `nmap_scan`, `run_nuclei`) via the MCP protocol; `hexstrike_mcp.py` translates them to HTTP requests against `hexstrike_server.py`; the server executes the system command and returns structured results.

---

## 5. Installation

Follow these steps on a **fresh Kali Linux 2024.1 or Ubuntu 22.04 VPS**. Every command must be run as the `hexstrike` user unless `sudo` is explicitly shown.

### Step 1 — Clone the Repository

```bash
cd ~
git clone https://github.com/bitbybit91/hexstrike-ai-dn.git
cd hexstrike-ai-dn
```

Expected output:
```
Cloning into 'hexstrike-ai-dn'...
remote: Enumerating objects: 42, done.
...
Resolving deltas: 100% (18/18), done.
```

---

### Step 2 — Create and Activate a Python Virtual Environment

```bash
python3.11 -m venv hexstrike_env        # Ubuntu 22.04
# or:
python3 -m venv hexstrike_env           # Kali Linux

source hexstrike_env/bin/activate
# Prompt changes to: (hexstrike_env) hexstrike@vps:~/hexstrike-ai-dn$
which python3    # Expected: ~/hexstrike-ai-dn/hexstrike_env/bin/python3
```

---

### Step 3 — Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Expected output (final lines):
```
Successfully installed aiohttp-3.9.5 beautifulsoup4-4.12.3 bcrypt-4.0.1
  fastmcp-0.2.3 flask-3.0.3 mitmproxy-10.2.4 psutil-5.9.8
  pwntools-4.12.0 requests-2.32.3 selenium-4.21.0 webdriver-manager-4.0.1
  ...
Successfully installed 38 packages.
```

**Common error — bcrypt conflict:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed...
```
Fix:
```bash
pip install bcrypt==4.0.1 --force-reinstall
```

---

### Step 4 — Install All External Security Tools

```bash
bash scripts/install_tools.sh
```

This script runs the full grouped `apt install` block and installs Go/Rust-based tools. It takes 10–20 minutes on a fresh VPS. When complete:
```
[✔] All 150 tools verified.
```

If the script is not yet present (first-time setup), run the grouped install manually (see [Section 2.6](#26-external-security-tools-150)).

---

### Step 5 — Install and Configure Tor

```bash
sudo apt install -y tor torsocks
sudo cp /etc/tor/torrc /etc/tor/torrc.backup
sudo tee -a /etc/tor/torrc <<'EOF'
SocksPort 9050
DNSPort 53
TransPort 9040
AutomapHostsOnResolve 1
VirtualAddrNetworkIPv4 10.192.0.0/10
Log notice file /var/log/tor/notices.log
EOF
sudo systemctl restart tor && sudo systemctl enable tor
torsocks curl -s https://check.torproject.org/api/ip
# Expected: {"IsTor":true,"IP":"..."}
```

---

### Step 6 — Create and Populate `.env`

```bash
cp .env.example .env
# Edit with your values:
nano .env
```

Generate a secure `MCP_SECRET_KEY`:
```bash
openssl rand -hex 32
# Example output: a3f8d1c2e4b5a6789012345678901234abcdef0123456789abcdef0123456789
```

Paste the output as `MCP_SECRET_KEY` in `.env`.

---

### Step 7 — Configure the Telegram Bot Integration

Create `telegram_bot.py` in the project root:

```python
#!/usr/bin/env python3
"""
HexStrike AI DN — Telegram C2 Bot
Dispatches commands to hexstrike_server.py and relays output to the operator.
"""
import os
import logging
import asyncio
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)

load_dotenv()

TELEGRAM_BOT_TOKEN      = os.environ["TELEGRAM_BOT_TOKEN"]
AUTHORIZED_CHAT_ID      = int(os.environ["TELEGRAM_AUTHORIZED_CHAT_ID"])
MCP_SERVER_URL          = f"http://{os.environ.get('MCP_HOST','127.0.0.1')}:{os.environ.get('MCP_PORT','8888')}"
USE_TOR                 = os.environ.get("USE_TOR", "true").lower() == "true"
TOR_SOCKS               = f"socks5h://{os.environ.get('TOR_SOCKS_HOST','127.0.0.1')}:{os.environ.get('TOR_SOCKS_PORT','9050')}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_proxies():
    return {"http": TOR_SOCKS, "https": TOR_SOCKS} if USE_TOR else {}


def mcp_post(endpoint: str, data: dict) -> str:
    try:
        r = requests.post(
            f"{MCP_SERVER_URL}/{endpoint}",
            json=data, proxies=get_proxies(), timeout=300
        )
        r.raise_for_status()
        return str(r.json())
    except Exception as e:
        return f"[ERROR] {e}"


def auth(update: Update) -> bool:
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        logger.warning(f"Rejected chat ID: {update.effective_chat.id}")
        return False
    return True


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    tor_ip = requests.get(
        "https://check.torproject.org/api/ip",
        proxies=get_proxies(), timeout=15
    ).json()
    health = requests.get(f"{MCP_SERVER_URL}/health", timeout=10).json()
    msg = (
        f"🔴 *HexStrike AI DN — Online*\n"
        f"Venice AI model: `{os.environ.get('VENICE_MODEL')}`\n"
        f"Tor exit IP: `{tor_ip.get('IP','unknown')}`\n"
        f"Server status: `{health.get('status','unknown')}`\n"
        f"Tools loaded: `{health.get('tools_count','150+')}`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    health = requests.get(f"{MCP_SERVER_URL}/health", timeout=10).json()
    tor_ip = requests.get(
        "https://check.torproject.org/api/ip",
        proxies=get_proxies(), timeout=15
    ).json()
    msg = (
        f"📊 *Status*\n"
        f"MCP Server: `{health.get('status','unknown')}`\n"
        f"Version: `{health.get('version','6.0')}`\n"
        f"Tor: `{'✅ Active' if tor_ip.get('IsTor') else '❌ Not routing'}`\n"
        f"Exit IP: `{tor_ip.get('IP','unknown')}`\n"
        f"Model: `{os.environ.get('VENICE_MODEL')}`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_scan(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not ctx.args:
        await update.message.reply_text("Usage: /scan <target>")
        return
    target = ctx.args[0]
    await update.message.reply_text(f"🔍 Scanning `{target}` via nmap + masscan...", parse_mode="Markdown")
    result = mcp_post("api/tools/nmap_scan", {"target": target, "scan_type": "-sV", "ports": ""})
    # Truncate long output and send as file if needed
    if len(result) > 4000:
        # Sanitize target to prevent path traversal — allow only alphanumeric, dots, hyphens, colons
        import re as _re
        safe_target = _re.sub(r"[^a-zA-Z0-9.\-:]", "_", target)
        out_path = f"/tmp/scan_{safe_target}.txt"
        with open(out_path, "w") as f:
            f.write(result)
        with open(out_path, "rb") as fh:
            await update.message.reply_document(
                document=fh,
                caption=f"Scan results for {target}"
            )
    else:
        await update.message.reply_text(f"```\n{result[:4000]}\n```", parse_mode="Markdown")


async def cmd_recon(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not ctx.args:
        await update.message.reply_text("Usage: /recon <domain>")
        return
    domain = ctx.args[0]
    await update.message.reply_text(f"🕵️ Starting recon on `{domain}`...", parse_mode="Markdown")
    result = mcp_post("api/tools/recon", {"target": domain, "tools": "amass,subfinder,httpx"})
    output = result[:4000] if len(result) > 4000 else result
    await update.message.reply_text(f"```\n{output}\n```", parse_mode="Markdown")


async def cmd_web(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not ctx.args:
        await update.message.reply_text("Usage: /web <url>")
        return
    url = ctx.args[0]
    await update.message.reply_text(f"🌐 Web scan: `{url}`...", parse_mode="Markdown")
    result = mcp_post("api/tools/web_scan", {"url": url, "tools": "nuclei,nikto,sqlmap"})
    await update.message.reply_text(f"```\n{result[:4000]}\n```", parse_mode="Markdown")


async def cmd_exploit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if len(ctx.args) < 2:
        await update.message.reply_text("Usage: /exploit <module> <target>")
        return
    module, target = ctx.args[0], ctx.args[1]
    result = mcp_post("api/tools/exploit", {"module": module, "target": target})
    await update.message.reply_text(f"```\n{result[:4000]}\n```", parse_mode="Markdown")


async def cmd_ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    if not ctx.args:
        await update.message.reply_text("Usage: /ask <your question>")
        return
    prompt = " ".join(ctx.args)
    proxies = get_proxies()
    resp = requests.post(
        f"{os.environ.get('VENICE_API_BASE','https://api.venice.ai/api/v1')}/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['VENICE_API_KEY']}"},
        json={
            "model": os.environ.get("VENICE_MODEL", "dolphin-2.9-llama3-70b"),
            "messages": [
                {"role": "system", "content": "You are an expert offensive security engineer."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        },
        proxies=proxies, timeout=120,
    )
    answer = resp.json()["choices"][0]["message"]["content"]
    await update.message.reply_text(answer[:4096])


async def cmd_tor_renew(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    try:
        from stem import Signal
        from stem.control import Controller
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
        await update.message.reply_text("🔄 New Tor circuit requested.")
    except Exception as e:
        await update.message.reply_text(f"[ERROR] {e}")


async def cmd_torcheck(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    data = requests.get(
        "https://check.torproject.org/api/ip",
        proxies=get_proxies(), timeout=15
    ).json()
    status = "✅ Routing through Tor" if data.get("IsTor") else "❌ NOT through Tor"
    await update.message.reply_text(f"{status}\nExit IP: `{data.get('IP','unknown')}`", parse_mode="Markdown")


async def cmd_logs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    n = int(ctx.args[0]) if ctx.args else 50
    log_file = os.environ.get("LOG_FILE", "/var/log/hexstrike/hexstrike.log")
    try:
        import subprocess
        lines = subprocess.check_output(["tail", f"-n{n}", log_file], text=True)
        await update.message.reply_text(f"```\n{lines[-4000:]}\n```", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"[ERROR] {e}")


async def cmd_stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not auth(update): return
    result = requests.post(f"{MCP_SERVER_URL}/api/shutdown", timeout=10)
    await update.message.reply_text(f"🛑 Shutdown signal sent: {result.status_code}")


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("status",   cmd_status))
    app.add_handler(CommandHandler("scan",     cmd_scan))
    app.add_handler(CommandHandler("recon",    cmd_recon))
    app.add_handler(CommandHandler("web",      cmd_web))
    app.add_handler(CommandHandler("exploit",  cmd_exploit))
    app.add_handler(CommandHandler("ask",      cmd_ask))
    app.add_handler(CommandHandler("tor",      cmd_tor_renew))
    app.add_handler(CommandHandler("torcheck", cmd_torcheck))
    app.add_handler(CommandHandler("logs",     cmd_logs))
    app.add_handler(CommandHandler("stop",     cmd_stop))
    logger.info("HexStrike Telegram bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
```

Install the additional Telegram and environment dependencies:
```bash
pip install python-telegram-bot==20.7 python-dotenv stem requests[socks]
```

---

### Step 8 — Configure Venice AI and Tor in the Server

#### 8a — Add Venice AI client (`venice_client.py`)

Create `venice_client.py`:
```python
#!/usr/bin/env python3
"""Venice AI API wrapper — abliterated model calls over SOCKS5/Tor."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

VENICE_API_BASE = os.environ.get("VENICE_API_BASE", "https://api.venice.ai/api/v1")
VENICE_API_KEY  = os.environ["VENICE_API_KEY"]
VENICE_MODEL    = os.environ.get("VENICE_MODEL", "dolphin-2.9-llama3-70b")
TOR_SOCKS_HOST  = os.environ.get("TOR_SOCKS_HOST", "127.0.0.1")
TOR_SOCKS_PORT  = os.environ.get("TOR_SOCKS_PORT", "9050")
USE_TOR         = os.environ.get("USE_TOR", "true").lower() == "true"

PROXIES = (
    {
        "http":  f"socks5h://{TOR_SOCKS_HOST}:{TOR_SOCKS_PORT}",
        "https": f"socks5h://{TOR_SOCKS_HOST}:{TOR_SOCKS_PORT}",
    }
    if USE_TOR else {}
)


def chat(prompt: str, system: str = "You are an expert offensive security engineer.",
         model: str = None, temperature: float = 0.7) -> str:
    """Send a prompt to Venice AI and return the text response."""
    response = requests.post(
        f"{VENICE_API_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {VENICE_API_KEY}"},
        json={
            "model": model or VENICE_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            "temperature": temperature,
        },
        proxies=PROXIES,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
```

#### 8b — Add Tor manager (`tor_manager.py`)

Create `tor_manager.py`:
```python
#!/usr/bin/env python3
"""Tor circuit control via stem — NEWNYM signal, IP check, DNS config."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOR_SOCKS_HOST = os.environ.get("TOR_SOCKS_HOST", "127.0.0.1")
TOR_SOCKS_PORT = int(os.environ.get("TOR_SOCKS_PORT", 9050))
TOR_CONTROL_PORT = 9051

PROXIES = {
    "http":  f"socks5h://{TOR_SOCKS_HOST}:{TOR_SOCKS_PORT}",
    "https": f"socks5h://{TOR_SOCKS_HOST}:{TOR_SOCKS_PORT}",
}


def renew_circuit() -> bool:
    """Request a new Tor exit node via NEWNYM signal."""
    try:
        from stem import Signal
        from stem.control import Controller
        with Controller.from_port(port=TOR_CONTROL_PORT) as ctrl:
            ctrl.authenticate()
            ctrl.signal(Signal.NEWNYM)
        return True
    except Exception as e:
        print(f"[TorManager] NEWNYM failed: {e}")
        return False


def current_exit_ip() -> dict:
    """Return current exit IP and Tor status from check.torproject.org."""
    resp = requests.get(
        "https://check.torproject.org/api/ip",
        proxies=PROXIES, timeout=20
    )
    return resp.json()


def is_tor_active() -> bool:
    return current_exit_ip().get("IsTor", False)
```

Enable the Tor control port (required for `stem`):
```bash
sudo bash -c 'echo "ControlPort 9051" >> /etc/tor/torrc'
sudo bash -c 'echo "CookieAuthentication 1" >> /etc/tor/torrc'
sudo usermod -aG debian-tor hexstrike   # Ubuntu/Debian
# or:
sudo usermod -aG tor hexstrike          # Kali
sudo systemctl restart tor
```

#### 8c — Wrap `requests` calls in `hexstrike_server.py` with SOCKS5

At the top of `hexstrike_server.py`, after the existing imports, add:
```python
# Load SOCKS5 proxy from environment when USE_TOR=true
# os is already imported at the top of hexstrike_server.py
if os.environ.get("USE_TOR", "true").lower() == "true":
    _tor_proxy = f"socks5h://{os.environ.get('TOR_SOCKS_HOST','127.0.0.1')}:{os.environ.get('TOR_SOCKS_PORT','9050')}"
    _DEFAULT_PROXIES = {"http": _tor_proxy, "https": _tor_proxy}
else:
    _DEFAULT_PROXIES = {}
```

Then ensure any `requests.get` / `requests.post` calls pass `proxies=_DEFAULT_PROXIES` (or use a session with `session.proxies.update(_DEFAULT_PROXIES)`).

---

### Step 9 — Verify the Server Starts

```bash
source hexstrike_env/bin/activate
python3 hexstrike_server.py
```

Expected terminal output:
```
██╗  ██╗███████╗██╗  ██╗███████╗████████╗██████╗ ██╗██╗  ██╗███████╗
...
[INFO] Server starting on 127.0.0.1:8888
[INFO] 150+ integrated modules | Adaptive AI decision engine active
[INFO] Blood-red theme engaged – unified offensive operations UI

 * Running on http://127.0.0.1:8888
 * Debug mode: off
```

Health check from another terminal:
```bash
curl -s http://127.0.0.1:8888/health | jq .
```
Expected:
```json
{"status":"healthy","version":"6.0","tools_count":150}
```

---

### Step 10 — Run Health Check via Telegram

1. Start the bot in a second terminal:
   ```bash
   source hexstrike_env/bin/activate
   python3 telegram_bot.py
   ```
2. Open Telegram and send `/status` to your bot

Expected bot reply:
```
📊 Status
MCP Server: healthy
Version: 6.0
Tor: ✅ Active
Exit IP: 185.220.xxx.xxx
Model: dolphin-2.9-llama3-70b
```

---

## 6. Telegram Bot — Command Reference

> **Authorization:** The bot checks `update.effective_chat.id` against `TELEGRAM_AUTHORIZED_CHAT_ID` on every incoming message. Any other chat ID receives no response and logs a warning. There is no fallback, no error message, and no prompt for credentials — silence is the only response to unauthorised requestors.

### Command Table

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Initialise session; confirm Venice AI model, Tor exit IP, and server health | `/start` |
| `/status` | Show server health, Tor routing status, current exit IP, active model | `/status` |
| `/scan <target>` | Run nmap + masscan against target; returns structured port/service list | `/scan 10.10.10.1` |
| `/recon <domain>` | Full recon chain: amass → subfinder → httpx subdomain enumeration | `/recon example.com` |
| `/web <url>` | Web app scan: nuclei templates + nikto + sqlmap parameter fuzzing | `/web https://target.com` |
| `/exploit <module> <target>` | Trigger a specific exploit module on the MCP server | `/exploit smb_ms17 10.10.10.1` |
| `/ask <prompt>` | Send free-form prompt directly to the Venice AI abliterated model | `/ask enumerate attack surface for 10.10.10.1` |
| `/tor renew` | Request a new Tor exit node via `NEWNYM` signal | `/tor renew` |
| `/torcheck` | Confirm current exit IP via check.torproject.org | `/torcheck` |
| `/logs [n]` | Retrieve last `n` lines from the server log file (default: 50) | `/logs 100` |
| `/stop` | Send graceful shutdown signal to the MCP server | `/stop` |

### Example Interactions

**`/start`**
```
User:  /start
Bot:   🔴 HexStrike AI DN — Online
       Venice AI model: dolphin-2.9-llama3-70b
       Tor exit IP: 185.220.101.47
       Server status: healthy
       Tools loaded: 150+
```

**`/scan 10.10.10.1`**
```
User:  /scan 10.10.10.1
Bot:   🔍 Scanning 10.10.10.1 via nmap + masscan...
       [2 minutes later]
Bot:   PORT     STATE SERVICE  VERSION
       22/tcp   open  ssh      OpenSSH 8.4
       80/tcp   open  http     Apache httpd 2.4.51
       443/tcp  open  ssl/http Apache httpd 2.4.51
       ...
       [Full results attached as scan_10_10_10_1.txt if > 4000 chars]
```

**`/ask enumerate attack surface for 10.10.10.1`**
```
User:  /ask enumerate attack surface for 10.10.10.1
Bot:   Based on the target IP, I recommend the following attack surface
       enumeration steps:
       1. Port scan (nmap -sV -p- -T4 10.10.10.1)
       2. Service fingerprinting and CVE lookup
       3. Web enumeration on ports 80/443 (gobuster, nuclei)
       4. SMB enumeration (netexec, enum4linux-ng)
       ...
```

**`/torcheck`**
```
User:  /torcheck
Bot:   ✅ Routing through Tor
       Exit IP: 185.220.101.47
```

**`/logs 20`**
```
User:  /logs 20
Bot:   2024-11-01 14:23:01 INFO Tool nmap_scan started — target 10.10.10.1
       2024-11-01 14:23:45 INFO nmap_scan completed — 3 open ports found
       ...
```

---

## 7. Tor Integration

### 7.1 Routing Tool Traffic Through Tor

All outbound tool execution is wrapped with `torsocks`:

```bash
# Run nmap through Tor
torsocks nmap -sV 10.10.10.1

# Run the entire MCP server through Tor
torsocks python3 hexstrike_server.py

# Run a single Python script through Tor
torsocks python3 venice_client.py
```

> **Note:** `torsocks` intercepts all TCP connections made by the wrapped process and routes them through the SOCKS5 proxy on port 9050. It does not affect UDP — see Section 7.4 for tools that cannot use Tor.

### 7.2 SOCKS5 Proxy in Python (`requests` and `aiohttp`)

**`requests`:**
```python
proxies = {
    "http":  "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}
response = requests.get("https://target.com", proxies=proxies, timeout=30)
```

> Use `socks5h://` (not `socks5://`) — the `h` suffix routes DNS resolution through Tor as well, preventing DNS leaks.

**`aiohttp`:**
```python
import aiohttp
from aiohttp_socks import ProxyConnector

async def fetch(url: str) -> str:
    connector = ProxyConnector.from_url("socks5://127.0.0.1:9050")
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as resp:
            return await resp.text()
```

Install `aiohttp-socks`:
```bash
pip install aiohttp-socks
```

### 7.3 Renewing the Tor Circuit Programmatically

Using the `stem` library:
```python
from stem import Signal
from stem.control import Controller

def renew_tor_circuit():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()           # Uses cookie auth by default
        controller.signal(Signal.NEWNYM)    # Request new exit node
        print("[Tor] New circuit requested.")
```

Or via command line:
```bash
echo -e 'AUTHENTICATE\r\nSIGNAL NEWNYM\r\nQUIT' | nc 127.0.0.1 9051
```

### 7.4 DNS Leak Prevention

Add to `/etc/tor/torrc`:
```ini
DNSPort 53
AutomapHostsOnResolve 1
VirtualAddrNetworkIPv4 10.192.0.0/10
```

Point system DNS to Tor's DNS resolver:
```bash
# Backup and replace resolv.conf
sudo cp /etc/resolv.conf /etc/resolv.conf.backup
echo "nameserver 127.0.0.1" | sudo tee /etc/resolv.conf
# Prevent NetworkManager from overwriting it:
sudo chattr +i /etc/resolv.conf
```

Verify no DNS leaks:
```bash
torsocks nslookup check.torproject.org
# Response should show a Tor exit DNS answer, not your ISP's resolver
```

### 7.5 Tools That Cannot Route Through Tor

The following tools use raw sockets or kernel-level packet injection and **cannot** be proxied through Tor:

| Tool | Reason | Alternative |
|------|--------|-------------|
| `masscan` | Raw sockets (kernel bypass) | Use nmap for Tor-routed scanning |
| `hping3` | Raw ICMP/TCP packet injection | Use nmap with `-sn` for host discovery |
| `nping` | Raw packet crafting | Acceptable — run without Tor on lab networks |
| `scapy` | Direct socket access | Wrap output parsing only; craft via Tor-accessible services |

For these tools, either accept the non-anonymised traffic (lab/internal use only), use a VPN as an additional layer before Tor, or run them against local/lab targets where anonymisation is not required.

---

## 8. Build & Deployment

### 8.1 Development — tmux Sessions on VPS

```bash
# Start a new tmux session
tmux new-session -s hexstrike

# Pane 1 — MCP Server (Ctrl+B, then %)
source hexstrike_env/bin/activate
torsocks python3 hexstrike_server.py

# Split pane — Ctrl+B then "
# Pane 2 — Telegram Bot
source hexstrike_env/bin/activate
python3 telegram_bot.py

# Detach and leave running: Ctrl+B, then D
# Reattach later: tmux attach -t hexstrike
```

---

### 8.2 Production — systemd Services

Create the two service unit files:

**`systemd/hexstrike-server.service`:**
```ini
[Unit]
Description=HexStrike AI DN — MCP Server
After=network.target tor.service
Wants=tor.service

[Service]
Type=simple
User=hexstrike
WorkingDirectory=/home/hexstrike/hexstrike-ai-dn
EnvironmentFile=/home/hexstrike/hexstrike-ai-dn/.env
ExecStart=/usr/bin/torsocks /home/hexstrike/hexstrike-ai-dn/hexstrike_env/bin/python3 hexstrike_server.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hexstrike-server

[Install]
WantedBy=multi-user.target
```

**`systemd/hexstrike-bot.service`:**
```ini
[Unit]
Description=HexStrike AI DN — Telegram C2 Bot
After=network.target hexstrike-server.service
Wants=hexstrike-server.service

[Service]
Type=simple
User=hexstrike
WorkingDirectory=/home/hexstrike/hexstrike-ai-dn
EnvironmentFile=/home/hexstrike/hexstrike-ai-dn/.env
ExecStart=/home/hexstrike/hexstrike-ai-dn/hexstrike_env/bin/python3 telegram_bot.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hexstrike-bot

[Install]
WantedBy=multi-user.target
```

Install and enable:
```bash
sudo cp systemd/hexstrike-server.service /etc/systemd/system/
sudo cp systemd/hexstrike-bot.service    /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hexstrike-server hexstrike-bot
sudo systemctl start  hexstrike-server hexstrike-bot
sudo systemctl status hexstrike-server hexstrike-bot
```

View live logs:
```bash
journalctl -u hexstrike-server -f
journalctl -u hexstrike-bot    -f
```

---

### 8.3 CI/CD — Automated Deployment via GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to VPS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to VPS via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host:     ${{ secrets.VPS_HOST }}
          username: hexstrike
          key:      ${{ secrets.VPS_SSH_KEY }}
          port:     22
          script: |
            set -e
            cd ~/hexstrike-ai-dn
            git pull origin main
            source hexstrike_env/bin/activate
            pip install -r requirements.txt --quiet
            sudo systemctl restart hexstrike-server
            sudo systemctl restart hexstrike-bot
            sleep 5

      - name: Health Check via Telegram Bot API
        run: |
          curl -s "https://api.telegram.org/bot${{ secrets.TELEGRAM_BOT_TOKEN }}/sendMessage" \
            -d chat_id="${{ secrets.TELEGRAM_AUTHORIZED_CHAT_ID }}" \
            -d text="✅ HexStrike deployed — commit: ${{ github.sha }}" \
            -d parse_mode="Markdown"
```

Add these repository secrets in GitHub → Settings → Secrets and variables → Actions:
- `VPS_HOST` — your VPS IP or hostname
- `VPS_SSH_KEY` — private SSH key (PEM format) for the `hexstrike` user
- `TELEGRAM_BOT_TOKEN` — from `.env`
- `TELEGRAM_AUTHORIZED_CHAT_ID` — from `.env`

---

## 9. Running Tests

### Unit Tests

```bash
source hexstrike_env/bin/activate
python3 -m pytest tests/ -v
```

Expected output:
```
tests/test_server.py::test_health_endpoint PASSED
tests/test_tor.py::test_tor_routing PASSED
tests/test_venice.py::test_venice_connection PASSED
...
25 passed in 4.31s
```

### Test Venice AI Connectivity

```bash
source hexstrike_env/bin/activate
python3 - <<'EOF'
from venice_client import chat
response = chat("Say: HexStrike online")
print(response)
EOF
```

Expected output:
```
HexStrike online
```

### Test Tor Routing

```bash
# Without Tor (baseline)
curl -s https://check.torproject.org/api/ip | jq .IsTor
# Expected: false

# With Tor
torsocks curl -s https://check.torproject.org/api/ip | jq .IsTor
# Expected: true
```

### Test Telegram Bot Token

```bash
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | jq '.result | {id, username, first_name}'
```

Expected:
```json
{
  "id": 123456789,
  "username": "hexstrike_op_bot",
  "first_name": "HexStrike Operator"
}
```

### Full Integration Test

1. Ensure `hexstrike_server.py` and `telegram_bot.py` are running
2. Send `/scan 127.0.0.1` to the bot
3. Verify the bot replies with nmap output for localhost within 60 seconds
4. Check server logs:
   ```bash
   journalctl -u hexstrike-server --since "1 minute ago"
   ```
   Expected log line: `INFO Tool nmap_scan started — target 127.0.0.1`

---

## 10. Common Issues & Troubleshooting

| Error / Symptom | Cause | Fix |
|-----------------|-------|-----|
| Venice AI returns `401 Unauthorized` | Invalid or missing `VENICE_API_KEY` | Verify `VENICE_API_KEY` in `.env`; regenerate the key at https://venice.ai |
| Venice AI returns `model not found` | Abliterated model ID changed or deprecated | Run `curl https://api.venice.ai/api/v1/models -H "Authorization: Bearer $VENICE_API_KEY" \| jq '.data[].id'`; update `VENICE_MODEL` |
| Bot not responding to any commands | Wrong `TELEGRAM_AUTHORIZED_CHAT_ID` or bot process not running | Verify chat ID with `getUpdates`; check `systemctl status hexstrike-bot` |
| `ConnectionRefusedError` on port 9050 | Tor service not running | `sudo systemctl start tor && sudo systemctl enable tor` |
| `torsocks: DNS leak detected` warning | `/etc/resolv.conf` points to non-Tor DNS | `echo "nameserver 127.0.0.1" | sudo tee /etc/resolv.conf && sudo chattr +i /etc/resolv.conf` |
| `ImportError: No module named 'mcp'` | `fastmcp` not installed inside the venv | `source hexstrike_env/bin/activate && pip install fastmcp` |
| `ChromeDriver version mismatch` | Chromium and chromedriver versions differ | `sudo apt install --reinstall chromium-browser chromium-chromedriver` |
| `OSError: [Errno 98] Address already in use` (port 8888) | Previous server instance still running | `fuser -k 8888/tcp` |
| `ImportError: pwntools / bcrypt conflict` | `bcrypt` installed at wrong version | `pip install bcrypt==4.0.1 --force-reinstall` |
| `nuclei: command not found` | Tool not installed or not in `$PATH` | Follow Section 2.6 Go tool install block; add `$HOME/go/bin` to `PATH` |
| `stem.SocketError: Unable to connect to port 9051` | Tor control port not enabled | Add `ControlPort 9051` and `CookieAuthentication 1` to `/etc/tor/torrc`; `sudo systemctl restart tor` |
| `Telegram getUpdates returns empty` | Bot never received a message | Send any message to the bot first, then retry `getUpdates` |
| `aiohttp.ClientProxyConnectionError` | `aiohttp-socks` not installed | `pip install aiohttp-socks` |

---

## 11. Project Structure

```
hexstrike-ai-dn/
├── hexstrike_server.py          # Core MCP server — 150+ tool handlers, Flask REST API
├── hexstrike_mcp.py             # MCP client bridge — FastMCP tool definitions for LLM agents
├── hexstrike-ai-mcp.json        # MCP server config (host, port, command, timeout)
├── requirements.txt             # Python dependencies (pinned versions)
├── telegram_bot.py              # Telegram C2 bot — command dispatcher, output relay
├── venice_client.py             # Venice AI API wrapper — abliterated model calls, SOCKS5 proxy
├── tor_manager.py               # Tor circuit control via stem — NEWNYM, IP check, DNS config
├── .env                         # Runtime secrets — NEVER commit this file
├── .env.example                 # Template for environment variables
├── assets/
│   └── hexstrike-logo.png       # Project logo
├── tests/
│   ├── test_server.py           # Unit tests for Flask API endpoints
│   ├── test_tor.py              # Tor routing and circuit renewal tests
│   └── test_venice.py           # Venice AI connectivity and response tests
├── systemd/
│   ├── hexstrike-server.service # systemd unit file for MCP server
│   └── hexstrike-bot.service    # systemd unit file for Telegram bot
└── scripts/
    ├── install_tools.sh         # Installs all 150+ external security tools
    ├── tool_check.sh            # Verifies all tools are present and executable
    └── deploy.sh                # VPS deployment: git pull, pip install, service restart
```

---

## 12. Scripts Reference

| Script / Command | Description |
|------------------|-------------|
| `python3 hexstrike_server.py` | Start the MCP server (plain, no Tor) |
| `torsocks python3 hexstrike_server.py` | Start MCP server with all traffic routed through Tor |
| `python3 telegram_bot.py` | Start the Telegram C2 bot |
| `bash scripts/install_tools.sh` | Install all 150+ external security tools (run once on fresh VPS) |
| `bash scripts/tool_check.sh` | Verify all tools are installed and accessible in `$PATH` |
| `bash scripts/deploy.sh` | Pull latest code, reinstall Python dependencies, restart systemd services |
| `systemctl start hexstrike-server` | Start MCP server as a persistent system service |
| `systemctl start hexstrike-bot` | Start Telegram bot as a persistent system service |
| `systemctl stop hexstrike-server` | Stop the MCP server service |
| `systemctl stop hexstrike-bot` | Stop the Telegram bot service |
| `systemctl restart hexstrike-server` | Restart the MCP server (after config changes) |
| `systemctl restart hexstrike-bot` | Restart the Telegram bot (after config changes) |
| `journalctl -u hexstrike-server -f` | Tail live MCP server logs |
| `journalctl -u hexstrike-bot -f` | Tail live Telegram bot logs |
| `torsocks curl -s https://check.torproject.org/api/ip` | Confirm Tor is routing traffic |
| `curl -s http://127.0.0.1:8888/health \| jq .` | Check MCP server health endpoint directly |

---

## 13. Contributing

1. Fork the repository and clone your fork:
   ```bash
   git clone https://github.com/<your-username>/hexstrike-ai-dn.git
   cd hexstrike-ai-dn
   ```
2. Create a branch using the appropriate prefix:
   - `feature/` — new capabilities or tools
   - `fix/` — bug fixes
   - `sec/` — security improvements or vulnerability patches
   ```bash
   git checkout -b feature/add-xxe-scanner
   ```
3. Make your changes inside an activated virtual environment
4. Format and lint before committing:
   ```bash
   pip install black flake8
   black .
   flake8 . --max-line-length=120
   ```
5. Confirm your changes pass the test suite:
   ```bash
   python3 -m pytest tests/ -v
   ```
6. Open a pull request against `main` with the following checklist completed:
   - [ ] Tor routing tested — no DNS leaks, `IsTor: true` confirmed
   - [ ] Venice AI model response tested — abliterated model responds correctly
   - [ ] Telegram bot commands tested — affected commands produce expected output
   - [ ] No secrets, API keys, or credentials in any committed file
   - [ ] `black` and `flake8` pass with zero errors

---

## 14. License

```
MIT License

Copyright (c) 2024 HexStrike / bitbybit91

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

**HexStrike AI DN** · VPS Edition · Built for headless, Tor-anonymised, autonomous offensive operations

*For authorised security testing only.*

</div>
