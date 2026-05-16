<!-- HexStrike AI DN — Ubuntu 20.04 VPS Edition -->
<div align="center">

<img src="assets/hexstrike-logo.png" alt="HexStrike AI Logo" width="220" style="margin-bottom: 20px;"/>

# HexStrike AI DN
### Autonomous Pentesting via Telegram · Venice AI · Tor · Ubuntu 20.04 VPS

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Penetration%20Testing-red.svg)](https://github.com/bitbybit91/hexstrike-ai-dn)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-purple.svg)](https://github.com/bitbybit91/hexstrike-ai-dn)
[![Version](https://img.shields.io/badge/Version-6.0.0-orange.svg)](https://github.com/bitbybit91/hexstrike-ai-dn)
[![Tools](https://img.shields.io/badge/Security%20Tools-150%2B-brightgreen.svg)](https://github.com/bitbybit91/hexstrike-ai-dn)
[![Tor](https://img.shields.io/badge/Network-Tor%20Anonymized-7D4698.svg)](https://www.torproject.org/)

**Ubuntu 20.04 LTS VPS · Headless / SSH-only · No GUI · Telegram C2 interface**

[�� Overview](#1-project-overview) • [⚙️ Prerequisites](#2-prerequisites) • [🖥️ VPS Setup](#3-vps-environment-setup-headless-no-physical-device) • [🤖 Telegram](#4-telegram-bot-setup) • [🧠 Venice AI](#5-venice-ai-configuration) • [🔧 Config](#6-configuration) • [🚀 Install](#7-installation) • [▶️ Run](#8-build--running) • [📟 Commands](#9-telegram-commands-reference) • [🧪 Tests](#10-running-tests) • [🛠️ Troubleshoot](#11-common-issues--troubleshooting) • [📁 Structure](#12-project-structure)

</div>

---

> **⚠️ Legal Notice:** HexStrike AI DN is designed exclusively for authorised penetration testing, CTF competitions, red team engagements, and security research on systems you own or have explicit written permission to test. Unauthorised use against systems you do not own is illegal. The authors accept no liability for misuse.

---

## 1. Project Overview

HexStrike AI DN is an **MCP-based offensive security automation platform** that exposes 150+ security tool wrappers through a FastMCP server (`hexstrike_server.py`) and MCP client bridge (`hexstrike_mcp.py`). A **Venice AI abliterated model** acts as the autonomous reasoning engine — selecting tools, interpreting results, and chaining attack phases — while a **Telegram bot** serves as the sole command-and-control interface, allowing the operator to issue commands, receive output, and manage scans entirely through a private Telegram chat from any device.

All outbound network traffic — tool executions, API calls to Venice AI, and HTTP requests — is routed through **Tor** via `torsocks` and a SOCKS5 proxy, providing full operational anonymity without any desktop GUI or physical device.

### Key Features

| Feature | Detail |
|---------|--------|
| **Telegram C2 interface** | Issue scan commands and receive structured output through a private Telegram chat |
| **Venice AI abliterated models** | Uncensored LLM reasoning for offensive security tasks — no content-policy refusals |
| **Tor-anonymised execution** | All tool traffic and API calls routed through `127.0.0.1:9050` via `torsocks` / SOCKS5 |
| **150+ security tool wrappers** | Network scanning, web app testing, exploitation, OSINT, binary analysis, password cracking |
| **MCP server/client architecture** | `hexstrike_server.py` (Flask REST API) + `hexstrike_mcp.py` (FastMCP bridge for LLM agents) |
| **Headless VPS-native** | No display server needed; persistent via `systemd` or `tmux` on Ubuntu 20.04 |
| **Autonomous tool chaining** | Venice AI selects and sequences tools based on target analysis without manual intervention |

### Full Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| API server | Flask 3.x |
| MCP bridge | FastMCP 0.2+ |
| AI backend | Venice AI API — abliterated models |
| C2 interface | python-telegram-bot v20+ |
| Anonymisation | Tor + torsocks + SOCKS5 (port 9050) |
| Browser automation | Chromium (headless) + Selenium 4 + ChromeDriver |
| HTTP proxy | mitmproxy 9+ |
| Binary analysis | pwntools 4.10+, angr 9.2+ |
| Async networking | aiohttp 3.8+ |
| HTML parsing | BeautifulSoup4 |

### Supported Environment

| Property | Value |
|----------|-------|
| OS | Ubuntu 20.04 LTS |
| Access | SSH only — no GUI, no physical device required |
| Python | 3.10+ (installed via `deadsnakes` PPA) |
| Network | All outbound traffic via Tor (optional bypass for lab use) |

---

## 2. Prerequisites

Install everything in the order listed. All commands are for **Ubuntu 20.04 LTS over SSH**.

### 2.1 System Updates

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git build-essential software-properties-common
```

---

### 2.2 Python 3.10 (via deadsnakes PPA)

Ubuntu 20.04 ships with Python 3.8. Python 3.10 is required for full pwntools compatibility and all dependencies.

```bash
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev
python3.10 --version
# Expected: Python 3.10.x
```

Install pip for Python 3.10:
```bash
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
python3.10 -m pip --version
# Expected: pip 24.x.x from ...python3.10/...
```

---

### 2.3 Tor

```bash
sudo apt install -y tor
sudo systemctl enable tor
sudo systemctl start tor
sudo systemctl status tor
# Expected: active (running)
tor --version
# Expected: Tor version 0.4.x.x.
```

---

### 2.4 torsocks

```bash
sudo apt install -y torsocks
torsocks --version
# Expected: torsocks version 2.x.x
```

---

### 2.5 tmux (persistent VPS sessions)

```bash
sudo apt install -y tmux
tmux -V
# Expected: tmux 3.x
```

---

### 2.6 Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send the message `/newbot`
3. Enter a display name when prompted, e.g., `HexStrike Operator`
4. Enter a username ending in `bot`, e.g., `hexstrike_op_bot`
5. BotFather replies with your token in the format `123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ`
6. Copy the token — store it as `TELEGRAM_BOT_TOKEN` in your `.env`

Verify the token works:
```bash
curl -s "https://api.telegram.org/bot<YOUR_TOKEN>/getMe" | python3 -m json.tool
# Expected: {"ok": true, "result": {"username": "hexstrike_op_bot", ...}}
```

---

### 2.7 Telegram Chat ID

Your Chat ID is the numeric identifier of your personal Telegram account. The bot will only respond to this ID.

1. Send any message to your bot from your personal Telegram account
2. Run:
```bash
curl -s "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result'][0]['message']['chat']['id'])"
```
3. The returned integer is your `TELEGRAM_ALLOWED_CHAT_ID`

Alternatively, search for **@userinfobot** in Telegram and send it `/start` to see your numeric ID.

---

### 2.8 Venice AI API Key

1. Open a browser and navigate to **https://venice.ai**
2. Create an account or sign in
3. Click your profile avatar → **Settings** → **API Keys** → **Create API Key**
4. Copy the key — it is displayed only once
5. Store it as `VENICE_API_KEY` in your `.env`

Verify the key (run from the VPS through Tor once Tor is configured):
```bash
torsocks curl -s "https://api.venice.ai/api/v1/models" \
  -H "Authorization: Bearer $VENICE_API_KEY" | python3 -m json.tool | grep '"id"'
```

---

### 2.9 External Security Tools (150+)

Run the provided installer script after cloning the repo:
```bash
bash scripts/install_tools.sh
```

Or install manually by category:

**Network & Reconnaissance:**
```bash
sudo apt install -y nmap masscan whois dnsutils traceroute netcat-openbsd
```

**Go-based tools** (requires Go — installed by the script):
```bash
sudo apt install -y golang-go
export GOPATH="$HOME/go"
export PATH="$PATH:$GOPATH/bin"
echo 'export GOPATH="$HOME/go"' >> ~/.bashrc
echo 'export PATH="$PATH:$GOPATH/bin"' >> ~/.bashrc

go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/owasp-amass/amass/v4/...@master
go install github.com/ffuf/ffuf/v2@latest
go install github.com/OJ/gobuster/v3@latest
go install github.com/hakluke/hakrawler@latest
go install github.com/lc/gau/v2/cmd/gau@latest
nuclei -update-templates
```

**Web Application Testing:**
```bash
sudo apt install -y sqlmap nikto whatweb dirb
pip3 install dirsearch wafw00f
```

**Password & Hash Tools:**
```bash
sudo apt install -y hydra john hashcat medusa
```

**Binary Analysis:**
```bash
sudo apt install -y binwalk gdb radare2 exiftool
```

**Forensics & OSINT:**
```bash
sudo apt install -y steghide foremost testdisk
pip3 install shodan
```

**Container/Cloud:**
```bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh
```

**Chromium (headless — for Selenium tools):**
```bash
sudo apt install -y chromium-browser chromium-chromedriver
chromium-browser --headless --no-sandbox --version
```

Verify all tools after install:
```bash
bash scripts/tool_check.sh
```

---

## 3. VPS Environment Setup (Headless, No Physical Device)

### 3.1 Provision a VPS

Log in to your preferred provider and create an **Ubuntu 20.04 LTS** instance. Minimum recommended specs: 2 vCPU, 4 GB RAM, 40 GB SSD.

**DigitalOcean (using `doctl`):**
```bash
doctl compute droplet create hexstrike-vps \
  --image ubuntu-20-04-x64 \
  --size s-2vcpu-4gb \
  --region nyc3 \
  --ssh-keys $(doctl compute ssh-key list --format ID --no-header | head -1) \
  --wait
```

**Hetzner Cloud (using `hcloud`):**
```bash
hcloud server create \
  --name hexstrike-vps \
  --type cx21 \
  --image ubuntu-20.04 \
  --ssh-key ~/.ssh/id_rsa.pub
```

**Vultr / Linode:** Use the web console to create an Ubuntu 20.04 instance with your SSH public key.

SSH into the new server:
```bash
ssh root@<VPS_IP>
```

---

### 3.2 Initial System Hardening

Run these commands as root immediately after first login:

```bash
# 1. Apply all security updates
apt update && apt upgrade -y && apt autoremove -y

# 2. Create a non-root operator user
adduser hexstrike
usermod -aG sudo hexstrike

# 3. Copy your SSH public key to the new user
rsync --archive --chown=hexstrike:hexstrike ~/.ssh /home/hexstrike

# 4. Disable password authentication and direct root login via SSH
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PermitRootLogin/PermitRootLogin/' /etc/ssh/sshd_config
systemctl reload sshd

# 5. Configure UFW — allow only SSH inbound; Tor SOCKS stays on loopback
ufw allow OpenSSH
ufw --force enable
ufw status verbose
# Expected: Status: active — 22/tcp ALLOW Anywhere
```

From a **new terminal**, verify you can still SSH as the `hexstrike` user before closing the root session:
```bash
ssh hexstrike@<VPS_IP>
```

All remaining commands are run as `hexstrike` unless `sudo` is shown explicitly.

---

### 3.3 Install and Configure Tor

```bash
sudo apt install -y tor torsocks
```

Edit `/etc/tor/torrc` to ensure SOCKS5 is enabled on loopback:
```bash
sudo cp /etc/tor/torrc /etc/tor/torrc.backup
sudo tee -a /etc/tor/torrc <<'EOF'
# HexStrike Tor configuration
SocksPort 127.0.0.1:9050
DNSPort 127.0.0.1:53
AutomapHostsOnResolve 1
VirtualAddrNetworkIPv4 10.192.0.0/10
Log notice file /var/log/tor/notices.log
EOF
sudo systemctl restart tor
sudo systemctl enable tor
```

Verify Tor is routing traffic:
```bash
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
```

Expected output:
```json
{"IsTor":true,"IP":"185.220.xxx.xxx"}
```

Verify with `torsocks`:
```bash
torsocks curl https://check.torproject.org/api/ip
# Expected: {"IsTor":true, ...}
```

---

### 3.4 Prevent DNS Leaks

```bash
# Point system DNS to Tor's DNS resolver
echo "nameserver 127.0.0.1" | sudo tee /etc/resolv.conf
# Prevent NetworkManager / systemd-resolved from overwriting it
sudo chattr +i /etc/resolv.conf
```

Verify:
```bash
torsocks nslookup check.torproject.org
# Should resolve via 127.0.0.1, not your ISP's DNS
```

---

### 3.5 Troubleshooting Tor

| Problem | Cause | Fix |
|---------|-------|-----|
| Tor not connecting | Firewall blocking outbound 9001/9030 | Allow outbound TCP on all ports or at minimum 9001, 9030 |
| Port 9050 already in use | Another SOCKS proxy is running | `sudo lsof -i :9050` to identify the process; stop it |
| `torsocks: Can't connect to Tor` | torsocks config points to wrong port | Check `/etc/tor/torsocks.conf` — `TorAddress 127.0.0.1`, `TorPort 9050` |
| DNS leaks detected | `resolv.conf` was overwritten | Re-run: `echo "nameserver 127.0.0.1" \| sudo tee /etc/resolv.conf && sudo chattr +i /etc/resolv.conf` |

---

## 4. Telegram Bot Setup

### 4.1 Create the Bot

1. Open Telegram on any device and search for **@BotFather**
2. Send `/newbot`
3. When prompted for a name, enter: `HexStrike Operator`
4. When prompted for a username, enter something unique ending in `bot`, e.g., `hexstrike_op_bot`
5. BotFather replies with a message containing your token:
   ```
   Use this token to access the HTTP API:
   7123456789:AAE-AbCdEfGhIjKlMnOpQrStUvWxYz12345
   ```
6. Copy this token and store it as `TELEGRAM_BOT_TOKEN` in your `.env`

Disable the bot from being added to groups (recommended for C2 use):
1. Send `/setjoingroups` to BotFather
2. Select your bot
3. Select **Disable**

---

### 4.2 Find Your Chat ID

1. Send the message `/start` to your new bot from your personal Telegram account
2. Run on the VPS:
```bash
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
updates = data.get('result', [])
if updates:
    chat = updates[-1]['message']['chat']
    print(f'Chat ID: {chat[\"id\"]}')
    print(f'Username: {chat.get(\"username\", \"(none)\")}')
else:
    print('No updates found — send a message to the bot first')
"
```
3. The numeric `Chat ID` value is your `TELEGRAM_ALLOWED_CHAT_ID`

---

### 4.3 Bot Authorization Model

The Telegram bot rejects all messages from any Chat ID that does not match `TELEGRAM_ALLOWED_CHAT_ID`. Unauthorised requestors receive no response and no error — only silence. The rejection is logged server-side.

---

### 4.4 Bot Dispatcher Setup

Create `telegram_bot.py` in the project root:

```python
#!/usr/bin/env python3
"""
HexStrike AI DN — Telegram C2 Bot
Routes commands to hexstrike_server.py and relays output to the operator.
"""
import os
import re
import logging
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

load_dotenv()

BOT_TOKEN       = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_CHAT_ID = int(os.environ["TELEGRAM_ALLOWED_CHAT_ID"])
SERVER_URL      = (
    f"http://{os.environ.get('HEXSTRIKE_SERVER_HOST','127.0.0.1')}"
    f":{os.environ.get('HEXSTRIKE_SERVER_PORT','8888')}"
)
USE_TOR         = os.environ.get("USE_TOR", "true").lower() == "true"
TOR_PROXY       = (
    f"socks5h://{os.environ.get('TOR_SOCKS_HOST','127.0.0.1')}"
    f":{os.environ.get('TOR_SOCKS_PORT','9050')}"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def tor_proxies() -> dict:
    return {"http": TOR_PROXY, "https": TOR_PROXY} if USE_TOR else {}


def server_post(endpoint: str, data: dict) -> str:
    try:
        r = requests.post(
            f"{SERVER_URL}/{endpoint}", json=data,
            proxies=tor_proxies(), timeout=300
        )
        r.raise_for_status()
        return str(r.json())
    except Exception as exc:
        return f"[ERROR] {exc}"


def server_get(endpoint: str) -> dict:
    try:
        r = requests.get(f"{SERVER_URL}/{endpoint}", timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        return {"error": str(exc)}


def authorised(update: Update) -> bool:
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        logger.warning("Rejected chat ID: %s", update.effective_chat.id)
        return False
    return True


async def safe_reply(update: Update, text: str) -> None:
    """Send reply; split into multiple messages if over Telegram's 4096-char limit."""
    for i in range(0, len(text), 4096):
        await update.message.reply_text(text[i:i+4096])


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return
    health = server_get("health")
    tor_data = requests.get(
        "https://check.torproject.org/api/ip",
        proxies=tor_proxies(), timeout=20
    ).json()
    reply = (
        "🔴 *HexStrike AI DN — Online*\n"
        f"Server status: `{health.get('status','unknown')}`\n"
        f"Tools loaded: `{health.get('tools_count','150+')}`\n"
        f"Venice model: `{os.environ.get('VENICE_MODEL','(not set)')}`\n"
        f"Tor active: `{'✅' if tor_data.get('IsTor') else '❌'}`\n"
        f"Exit IP: `{tor_data.get('IP','unknown')}`"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return
    health = server_get("health")
    tor_data = requests.get(
        "https://check.torproject.org/api/ip",
        proxies=tor_proxies(), timeout=20
    ).json()
    reply = (
        "📊 *Status*\n"
        f"Server: `{health.get('status','unknown')}`\n"
        f"Version: `{health.get('version','6.0')}`\n"
        f"Tor: `{'✅ Active' if tor_data.get('IsTor') else '❌ Not routing'}`\n"
        f"Exit IP: `{tor_data.get('IP','unknown')}`\n"
        f"Model: `{os.environ.get('VENICE_MODEL','(not set)')}`"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")


async def cmd_scan(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return
    if not ctx.args:
        await update.message.reply_text("Usage: /scan <target>")
        return
    target = ctx.args[0]
    await update.message.reply_text(
        f"🔍 Scanning `{target}` ...", parse_mode="Markdown"
    )
    result = server_post("api/tools/nmap_scan", {"target": target, "scan_type": "-sV"})
    await safe_reply(update, f"```\n{result}\n```")


async def cmd_nuclei(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return
    if not ctx.args:
        await update.message.reply_text("Usage: /nuclei <target>")
        return
    target = ctx.args[0]
    await update.message.reply_text(f"🎯 Running Nuclei on `{target}` ...", parse_mode="Markdown")
    result = server_post("api/tools/nuclei_scan", {"target": target})
    await safe_reply(update, f"```\n{result}\n```")


async def cmd_sqlmap(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return
    if not ctx.args:
        await update.message.reply_text("Usage: /sqlmap <url>")
        return
    url = ctx.args[0]
    await update.message.reply_text(f"💉 Running SQLMap on `{url}` ...", parse_mode="Markdown")
    result = server_post("api/tools/sqlmap_scan", {"url": url})
    await safe_reply(update, f"```\n{result}\n```")


async def cmd_ffuf(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return
    if not ctx.args:
        await update.message.reply_text("Usage: /ffuf <url>  (put FUZZ in the URL)")
        return
    url = ctx.args[0]
    await update.message.reply_text(f"📂 Running ffuf on `{url}` ...", parse_mode="Markdown")
    result = server_post("api/tools/ffuf_scan", {"url": url})
    await safe_reply(update, f"```\n{result}\n```")


async def cmd_ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return
    if not ctx.args:
        await update.message.reply_text("Usage: /ask <your question or prompt>")
        return
    prompt = " ".join(ctx.args)
    venice_base = os.environ.get("VENICE_BASE_URL", "https://api.venice.ai/api/v1")
    venice_key  = os.environ["VENICE_API_KEY"]
    venice_model = os.environ.get("VENICE_MODEL", "nous-hermes-2-mixtral-8x7b")
    resp = requests.post(
        f"{venice_base}/chat/completions",
        headers={"Authorization": f"Bearer {venice_key}"},
        json={
            "model": venice_model,
            "messages": [
                {"role": "system", "content": "You are an expert offensive security engineer."},
                {"role": "user",   "content": prompt},
            ],
            "temperature": 0.7,
        },
        proxies=tor_proxies(),
        timeout=120,
    )
    resp.raise_for_status()
    answer = resp.json()["choices"][0]["message"]["content"]
    await safe_reply(update, answer)


async def cmd_stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return
    result = server_post("api/shutdown", {})
    await update.message.reply_text(f"🛑 Shutdown signal sent: {result}")


async def cmd_results(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return
    data = server_get("api/results/last")
    await safe_reply(update, str(data))


async def cmd_tor_check(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return
    data = requests.get(
        "https://check.torproject.org/api/ip",
        proxies=tor_proxies(), timeout=20
    ).json()
    status = "✅ Routing through Tor" if data.get("IsTor") else "❌ NOT through Tor"
    await update.message.reply_text(
        f"{status}\nExit IP: `{data.get('IP','unknown')}`", parse_mode="Markdown"
    )


async def cmd_newcircuit(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return
    try:
        from stem import Signal
        from stem.control import Controller
        with Controller.from_port(port=9051) as ctrl:
            ctrl.authenticate()
            ctrl.signal(Signal.NEWNYM)
        await update.message.reply_text("🔄 New Tor circuit requested.")
    except Exception as exc:
        await update.message.reply_text(f"[ERROR] {exc}")


def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",      cmd_start))
    app.add_handler(CommandHandler("status",     cmd_status))
    app.add_handler(CommandHandler("scan",       cmd_scan))
    app.add_handler(CommandHandler("nuclei",     cmd_nuclei))
    app.add_handler(CommandHandler("sqlmap",     cmd_sqlmap))
    app.add_handler(CommandHandler("ffuf",       cmd_ffuf))
    app.add_handler(CommandHandler("ask",        cmd_ask))
    app.add_handler(CommandHandler("stop",       cmd_stop))
    app.add_handler(CommandHandler("results",    cmd_results))
    app.add_handler(CommandHandler("tor_check",  cmd_tor_check))
    app.add_handler(CommandHandler("newcircuit", cmd_newcircuit))
    logger.info("HexStrike Telegram bot polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
```

Install the additional bot dependencies:
```bash
pip install python-telegram-bot==20.7 python-dotenv stem requests[socks]
```

---

## 5. Venice AI Configuration

### 5.1 What Abliterated Models Are

Standard LLM models (GPT-4, Claude, etc.) include content-filtering layers — trained refusals that prevent them from discussing offensive security topics such as exploitation, payload generation, or vulnerability analysis. **Abliterated models** are open-source LLMs that have had this refusal training removed, allowing them to reason freely about offensive security tasks without interruption.

Venice AI hosts abliterated versions of leading open-source models and exposes them via an **OpenAI-compatible REST API** at `https://api.venice.ai/api/v1`. This means the same `requests.post` call structure used for OpenAI works identically with Venice AI — only the base URL and API key differ.

---

### 5.2 Obtain a Venice AI API Key

1. Open a browser and navigate to **https://venice.ai**
2. Create an account or sign in with an existing one
3. Click your profile avatar in the top-right corner → **Settings** → **API Keys**
4. Click **Create API Key**, enter a label (e.g., `hexstrike-vps`), and confirm
5. Copy the key — it is shown only once; store it as `VENICE_API_KEY` in `.env`

---

### 5.3 Recommended Abliterated Models

| Model ID | Parameters | Best Use Case |
|----------|-----------|---------------|
| `nous-hermes-2-mixtral-8x7b` | 8×7B MoE | **Default recommendation** — reasoning, attack planning, OSINT analysis |
| `dolphin-2.9-llama3-8b` | 8B | **Fast interactive queries** — Telegram responses, command generation, quick pivots |
| `dolphin-mixtral-8x22b` | 8×22B MoE | **Large context analysis** — interpreting long tool outputs, CVE research, report writing |
| `dolphin-2.9-llama3-70b` | 70B | **Deep reasoning** — complex multi-step exploit chains, zero-day research |

List all available models via the API:
```bash
curl -s "https://api.venice.ai/api/v1/models" \
  -H "Authorization: Bearer $VENICE_API_KEY" \
  | python3 -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin)['data']]"
```

---

### 5.4 Route Venice AI Calls Through Tor

All calls from `telegram_bot.py` and `hexstrike_server.py` to the Venice AI API are made through the Tor SOCKS5 proxy. Always use `socks5h://` (not `socks5://`) to route DNS resolution through Tor as well.

```python
import os
import requests

proxies = {
    "http":  "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}

response = requests.post(
    "https://api.venice.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['VENICE_API_KEY']}"},
    json={
        "model": os.environ.get("VENICE_MODEL", "nous-hermes-2-mixtral-8x7b"),
        "messages": [
            {
                "role": "system",
                "content": "You are an expert offensive security engineer.",
            },
            {
                "role": "user",
                "content": "Enumerate the attack surface for 10.10.10.1",
            },
        ],
        "temperature": 0.7,
    },
    proxies=proxies,
    timeout=120,
)
response.raise_for_status()
print(response.json()["choices"][0]["message"]["content"])
```

Equivalent `curl` test (through `torsocks`):
```bash
torsocks curl -s "https://api.venice.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $VENICE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nous-hermes-2-mixtral-8x7b",
    "messages": [
      {"role":"system","content":"You are an expert offensive security engineer."},
      {"role":"user","content":"List common web application attack vectors."}
    ],
    "temperature": 0.7
  }' | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])"
```

---

## 6. Configuration

### 6.1 Environment Variables

Copy the template and populate every value:
```bash
cp .env.example .env
nano .env
```

Full annotated `.env.example`:
```dotenv
# ============================================================
# Venice AI
# ============================================================
VENICE_API_KEY=your_venice_api_key_here
# Abliterated model — see Section 5.3 for full list
VENICE_MODEL=nous-hermes-2-mixtral-8x7b
# Venice AI OpenAI-compatible API base URL
VENICE_BASE_URL=https://api.venice.ai/api/v1

# ============================================================
# Telegram Bot
# ============================================================
TELEGRAM_BOT_TOKEN=123456789:ABCDEF_your_bot_token_here
# Your personal Telegram numeric chat ID — all other IDs are rejected
TELEGRAM_ALLOWED_CHAT_ID=987654321

# ============================================================
# HexStrike MCP Server
# ============================================================
# Bind to loopback only — do not set to 0.0.0.0 in production
HEXSTRIKE_SERVER_HOST=127.0.0.1
HEXSTRIKE_SERVER_PORT=8888

# ============================================================
# Tor
# ============================================================
TOR_SOCKS_HOST=127.0.0.1
TOR_SOCKS_PORT=9050
# Set to false only for local lab testing without Tor
USE_TOR=true

# ============================================================
# Logging
# ============================================================
# INFO for production; DEBUG for verbose development output
LOG_LEVEL=INFO
```

Generate a secret key for Flask if needed:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

### 6.2 `hexstrike-ai-mcp.json`

This file tells any MCP-compatible host (e.g., a Venice AI autonomous agent loop, or a local LLM orchestrator) how to launch `hexstrike_mcp.py` as a subprocess.

**Corrected production configuration:**

> **Important:** Update `args[0]` to the absolute path of `hexstrike_mcp.py` on your VPS. The path below assumes the repository was cloned to `/home/hexstrike/hexstrike-ai-dn`. Adjust if you used a different directory.

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
      "description": "HexStrike AI v6.0 — Offensive Security Automation Platform. Set alwaysAllow to [] for manual approval of each tool call.",
      "timeout": 300,
      "alwaysAllow": []
    }
  }
}
```

**Field reference:**

| Field | Description |
|-------|-------------|
| `command` | Python interpreter — use the full venv path for isolation: `/home/hexstrike/hexstrike-ai-dn/hexstrike_env/bin/python3` |
| `args[0]` | Absolute path to `hexstrike_mcp.py` on this VPS |
| `args[2]` | URL of the running `hexstrike_server.py` — must match `HEXSTRIKE_SERVER_HOST:HEXSTRIKE_SERVER_PORT` in `.env` |
| `timeout` | Maximum seconds to wait for a tool response (300 = 5 minutes) |
| `alwaysAllow` | List of tool names that run without operator confirmation. Use `[]` to require approval for every call |

---

### 6.3 Debug vs. Production Mode

| Setting | Production | Debug |
|---------|-----------|-------|
| `LOG_LEVEL` | `INFO` | `DEBUG` |
| Flask debug | Off (default) | Set `FLASK_DEBUG=1` |
| Tor routing | `USE_TOR=true` | `USE_TOR=false` (local lab only) |

Switch to debug mode temporarily:
```bash
LOG_LEVEL=DEBUG USE_TOR=false python3 hexstrike_server.py
```

---

## 7. Installation

Follow every step in order on a **clean Ubuntu 20.04 LTS VPS** accessed via SSH. Every command runs as the `hexstrike` user unless `sudo` is shown.

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
Resolving deltas: 100% (18/18), done.
```

Common error:
```
fatal: unable to access 'https://github.com/...': Could not resolve host: github.com
```
Fix: DNS is probably pointing to `127.0.0.1` before Tor is running. Temporarily restore DNS:
```bash
sudo chattr -i /etc/resolv.conf
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
# After cloning, re-enable Tor DNS:
echo "nameserver 127.0.0.1" | sudo tee /etc/resolv.conf && sudo chattr +i /etc/resolv.conf
```

---

### Step 2 — Navigate to the Project Directory

```bash
cd ~/hexstrike-ai-dn
pwd
# Expected: /home/hexstrike/hexstrike-ai-dn
```

---

### Step 3 — Create and Activate a Python 3.10 Virtual Environment

```bash
python3.10 -m venv hexstrike_env
source hexstrike_env/bin/activate
python3 --version
# Expected: Python 3.10.x
which pip
# Expected: /home/hexstrike/hexstrike-ai-dn/hexstrike_env/bin/pip
```

Common error:
```
python3.10: command not found
```
Fix:
```bash
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev
```

---

### Step 4 — Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Expected final lines:
```
Successfully installed aiohttp-3.9.5 beautifulsoup4-4.12.3 bcrypt-4.0.1
  fastmcp-0.2.3 flask-3.0.3 mitmproxy-10.2.4 psutil-5.9.8
  pwntools-4.12.0 requests-2.32.3 selenium-4.21.0 ...
Successfully installed 38 packages.
```

Common error — bcrypt conflict:
```
ERROR: pip's dependency resolver does not currently take into account all the packages...
```
Fix:
```bash
pip install bcrypt==4.0.1 --force-reinstall
```

Common error — pwntools fails on Python 3.11:
```
ERROR: Could not build wheels for pwntools
```
Fix: Ensure you activated the Python **3.10** venv (not system Python 3.11):
```bash
deactivate
python3.10 -m venv hexstrike_env
source hexstrike_env/bin/activate
```

---

### Step 5 — Copy `.env.example` to `.env` and Fill In All Values

```bash
cp .env.example .env
nano .env
```

Minimum required values:
```dotenv
VENICE_API_KEY=<your key>
VENICE_MODEL=nous-hermes-2-mixtral-8x7b
TELEGRAM_BOT_TOKEN=<your token>
TELEGRAM_ALLOWED_CHAT_ID=<your numeric chat ID>
```

---

### Step 6 — Verify Tor Is Running and Routing Correctly

```bash
sudo systemctl status tor
# Expected: active (running)

curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
# Expected: {"IsTor":true,"IP":"..."}
```

If Tor is not running:
```bash
sudo systemctl start tor && sudo systemctl enable tor
```

---

### Step 7 — Install All 150+ External Security Tools

```bash
bash scripts/install_tools.sh
```

This takes 10–20 minutes on a fresh VPS. When complete:
```
[✔] All 150 tools verified.
```

Verify with the check script:
```bash
bash scripts/tool_check.sh
```

---

### Step 8 — Run the HexStrike MCP Server

```bash
source hexstrike_env/bin/activate
python3 hexstrike_server.py
```

Expected output:
```
██╗  ██╗███████╗██╗  ██╗███████╗████████╗██████╗ ██╗██╗  ██╗███████╗
...
[INFO] Server starting on 127.0.0.1:8888
[INFO] 150+ integrated modules | Adaptive AI decision engine active
 * Running on http://127.0.0.1:8888
```

Health check from another terminal:
```bash
curl -s http://127.0.0.1:8888/health | python3 -m json.tool
# Expected: {"status": "healthy", "version": "6.0", "tools_count": 150}
```

---

### Step 9 — Run the Telegram Bot Controller

```bash
source hexstrike_env/bin/activate
python3 telegram_bot.py
```

Expected output:
```
INFO:__main__:HexStrike Telegram bot polling...
```

---

### Step 10 — Verify the Full Stack

Send `/status` to the bot from your Telegram account.

Expected bot reply:
```
📊 Status
Server: healthy
Version: 6.0
Tor: ✅ Active
Exit IP: 185.220.xxx.xxx
Model: nous-hermes-2-mixtral-8x7b
```

If the bot does not respond:
1. Confirm `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_CHAT_ID` are correct in `.env`
2. Check `python3 telegram_bot.py` is running: `tmux ls` or `ps aux | grep telegram`
3. Verify the server is healthy: `curl -s http://127.0.0.1:8888/health`

---

## 8. Build & Running

### 8.1 Development — tmux Sessions

```bash
# Start MCP server in background tmux session
tmux new-session -d -s hexstrike \
  "cd ~/hexstrike-ai-dn && source hexstrike_env/bin/activate && python3 hexstrike_server.py"

# Start Telegram bot in a separate tmux session
tmux new-session -d -s tgbot \
  "cd ~/hexstrike-ai-dn && source hexstrike_env/bin/activate && python3 telegram_bot.py"

# Attach to either session to see live output
tmux attach -t hexstrike
tmux attach -t tgbot

# Detach without stopping: Ctrl+B then D
```

Start both sessions through Tor:
```bash
tmux new-session -d -s hexstrike \
  "cd ~/hexstrike-ai-dn && source hexstrike_env/bin/activate && torsocks python3 hexstrike_server.py"
```

---

### 8.2 Route Tool Execution Through Tor

Prefix any tool command with `torsocks` to route it through Tor:
```bash
torsocks nmap -sV target.com
torsocks sqlmap -u "https://target.com/page?id=1" --dbs
torsocks nuclei -u https://target.com -t ~/nuclei-templates/
```

Verify Python SOCKS5 routing:
```python
import requests
proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}
r = requests.get("https://check.torproject.org/api/ip", proxies=proxies)
print(r.json())
# Expected: {'IsTor': True, 'IP': '185.220.xxx.xxx'}
```

---

### 8.3 Production — systemd Services

Create the service unit files:

**`/etc/systemd/system/hexstrike-server.service`:**
```ini
[Unit]
Description=HexStrike AI DN — MCP Server
After=network.target tor.service
Wants=tor.service

[Service]
Type=simple
User=hexstrike
Group=hexstrike
WorkingDirectory=/home/hexstrike/hexstrike-ai-dn
EnvironmentFile=/home/hexstrike/hexstrike-ai-dn/.env
ExecStart=/home/hexstrike/hexstrike-ai-dn/hexstrike_env/bin/python3 \
          /home/hexstrike/hexstrike-ai-dn/hexstrike_server.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hexstrike-server

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/hexstrike-tgbot.service`:**
```ini
[Unit]
Description=HexStrike AI DN — Telegram C2 Bot
After=network.target hexstrike-server.service
Wants=hexstrike-server.service

[Service]
Type=simple
User=hexstrike
Group=hexstrike
WorkingDirectory=/home/hexstrike/hexstrike-ai-dn
EnvironmentFile=/home/hexstrike/hexstrike-ai-dn/.env
ExecStart=/home/hexstrike/hexstrike-ai-dn/hexstrike_env/bin/python3 \
          /home/hexstrike/hexstrike-ai-dn/telegram_bot.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hexstrike-tgbot

[Install]
WantedBy=multi-user.target
```

Install and enable:
```bash
sudo cp systemd/hexstrike-server.service /etc/systemd/system/
sudo cp systemd/hexstrike-tgbot.service  /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hexstrike-server hexstrike-tgbot
sudo systemctl start  hexstrike-server hexstrike-tgbot
sudo systemctl status hexstrike-server hexstrike-tgbot
```

View live logs:
```bash
journalctl -u hexstrike-server -f
journalctl -u hexstrike-tgbot  -f
```

---

## 9. Telegram Commands Reference

> **Authorization:** Every incoming message is checked against `TELEGRAM_ALLOWED_CHAT_ID`. Messages from any other Chat ID are silently dropped and logged as a warning. There is no error reply to unauthorised senders.

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Initialise bot session; show server health, Tor status, and active model | `/start` |
| `/status` | Check server health, Tor circuit, and exit IP | `/status` |
| `/scan <target>` | Run nmap version scan against target | `/scan 10.10.10.1` |
| `/nuclei <target>` | Run Nuclei vulnerability scan with all default templates | `/nuclei example.com` |
| `/sqlmap <url>` | Run SQLMap injection test against a URL | `/sqlmap https://example.com/page?id=1` |
| `/ffuf <url>` | Run ffuf directory brute-force (place `FUZZ` in URL) | `/ffuf https://example.com/FUZZ` |
| `/ask <prompt>` | Send a free-form prompt to the Venice AI abliterated model | `/ask "analyse these HTTP headers for vulnerabilities"` |
| `/stop` | Send graceful shutdown signal to the MCP server | `/stop` |
| `/results` | Retrieve the last tool output stored by the server | `/results` |
| `/tor_check` | Confirm current exit IP via check.torproject.org | `/tor_check` |
| `/newcircuit` | Request a new Tor exit node via NEWNYM signal | `/newcircuit` |

### Example Interactions

**`/start`**
```
User: /start
Bot:  🔴 HexStrike AI DN — Online
      Server status: healthy
      Tools loaded: 150+
      Venice model: nous-hermes-2-mixtral-8x7b
      Tor active: ✅
      Exit IP: 185.220.101.47
```

**`/scan 10.10.10.1`**
```
User: /scan 10.10.10.1
Bot:  🔍 Scanning 10.10.10.1 ...
      [60 seconds later]
Bot:  PORT    STATE SERVICE VERSION
      22/tcp  open  ssh     OpenSSH 7.9
      80/tcp  open  http    Apache 2.4.38
      443/tcp open  https   Apache 2.4.38
```

**`/ask "list SMB attack vectors"`**
```
User: /ask "list SMB attack vectors"
Bot:  Common SMB attack vectors include:
      1. EternalBlue (MS17-010) — unauthenticated RCE via SMBv1
      2. Pass-the-Hash — relay captured NTLM hashes
      3. SMB Relay attacks via Responder + ntlmrelayx
      ...
```

**`/newcircuit`**
```
User: /newcircuit
Bot:  🔄 New Tor circuit requested.
```

---

## 10. Running Tests

### Test Venice AI Through Tor

```bash
source hexstrike_env/bin/activate
torsocks curl -s "https://api.venice.ai/api/v1/models" \
  -H "Authorization: Bearer $VENICE_API_KEY" \
  | python3 -c "import sys,json; print('OK —', len(json.load(sys.stdin)['data']), 'models available')"
# Expected: OK — N models available
```

### Test Telegram Bot Token

```bash
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('Bot:', d['result']['username'])"
# Expected: Bot: hexstrike_op_bot
```

### Test a Single Tool Wrapper via MCP Server

```bash
source hexstrike_env/bin/activate
curl -s -X POST http://127.0.0.1:8888/api/tools/nmap_scan \
  -H "Content-Type: application/json" \
  -d '{"target":"127.0.0.1","scan_type":"-sV","ports":"22,80"}' \
  | python3 -m json.tool
# Expected: JSON with scan results for localhost
```

### Send `/status` and Verify Full Stack

1. Start both services (or tmux sessions)
2. Send `/status` to the bot from Telegram
3. Confirm the reply shows `Server: healthy` and `Tor: ✅ Active`

### Run Unit Tests

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
N passed in X.XXs
```

---

## 11. Common Issues & Troubleshooting

| Error / Symptom | Cause | Fix |
|-----------------|-------|-----|
| `[Errno 111] Connection refused` on port 9050 | Tor service not running | `sudo systemctl start tor && sudo systemctl enable tor` |
| Venice AI returns `401 Unauthorized` | Invalid or missing `VENICE_API_KEY` | Verify `VENICE_API_KEY` in `.env`; regenerate the key at https://venice.ai |
| Venice AI returns `403` or content filtered | Using a non-abliterated model | Switch `VENICE_MODEL` to `nous-hermes-2-mixtral-8x7b` or `dolphin-2.9-llama3-8b` |
| Telegram bot not responding to any command | Wrong `BOT_TOKEN` or `ALLOWED_CHAT_ID` | Verify token: `curl "https://api.telegram.org/bot<TOKEN>/getMe"`; verify chat ID with `getUpdates` |
| `ModuleNotFoundError: No module named 'mcp'` | fastmcp not installed in active venv | `source hexstrike_env/bin/activate && pip install fastmcp>=0.2.0` |
| `torsocks: Can't connect to Tor` | torsocks misconfigured | Check `/etc/tor/torsocks.conf` — set `TorAddress 127.0.0.1` and `TorPort 9050` |
| `OSError: [Errno 98] Address already in use` (port 8888) | Previous server instance still running | `kill $(lsof -t -i:8888)` |
| pwntools install fails | Python version above 3.10 in the venv | Create a new venv with Python 3.10: `python3.10 -m venv hexstrike_env` |
| `nuclei: command not found` | Nuclei binary not in `$PATH` | Run `go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest`; ensure `$GOPATH/bin` is in `PATH` |
| Nuclei templates not found | Templates not downloaded | `nuclei -update-templates` |
| DNS leak through Tor | Using `socks5://` instead of `socks5h://` | Replace all proxy strings with `socks5h://127.0.0.1:9050` in code and `.env` |
| `stem.SocketError` on `/newcircuit` | Tor control port not enabled | Add `ControlPort 9051` and `CookieAuthentication 1` to `/etc/tor/torrc`; `sudo systemctl restart tor`; add user to `debian-tor` group: `sudo usermod -aG debian-tor hexstrike` |
| Git clone fails — DNS resolution error | Tor DNS is routing before Tor is started | Temporarily restore DNS: `sudo chattr -i /etc/resolv.conf && echo "nameserver 8.8.8.8" \| sudo tee /etc/resolv.conf` |

---

## 12. Project Structure

```
hexstrike-ai-dn/
├── hexstrike_server.py          # Main Flask+MCP server — 150+ security tool wrappers
├── hexstrike_mcp.py             # MCP client — bridges AI agents to the server API
├── hexstrike-ai-mcp.json        # MCP server config (host, port, command, timeout)
├── requirements.txt             # Python dependencies (pinned versions)
├── telegram_bot.py              # Telegram C2 bot — command dispatcher, output relay
├── .env.example                 # Environment variable template — copy to .env
├── .env                         # Runtime secrets — never commit this file
├── assets/
│   └── hexstrike-logo.png       # Project logo
├── tests/
│   ├── test_server.py           # Unit tests for Flask API endpoints
│   ├── test_tor.py              # Tor routing and circuit renewal tests
│   └── test_venice.py           # Venice AI connectivity tests
├── systemd/
│   ├── hexstrike-server.service # systemd unit file for MCP server
│   └── hexstrike-tgbot.service  # systemd unit file for Telegram bot
└── scripts/
    ├── install_tools.sh         # Installs all 150+ external security tools
    ├── tool_check.sh            # Verifies all tools are installed and in PATH
    └── deploy.sh                # VPS deployment helper (pull, pip install, restart services)
```

---

## 13. Scripts Reference

| Script / Command | Description |
|------------------|-------------|
| `python3 hexstrike_server.py` | Start the HexStrike MCP HTTP server on port 8888 |
| `python3 hexstrike_mcp.py --server http://127.0.0.1:8888` | Start MCP client connected to local server |
| `python3 telegram_bot.py` | Start the Telegram C2 bot |
| `torsocks python3 hexstrike_server.py` | Start MCP server with all traffic routed through Tor |
| `torsocks nmap -sV <target>` | Run nmap through Tor |
| `source hexstrike_env/bin/activate` | Activate Python 3.10 virtual environment |
| `sudo systemctl restart tor` | Restart the Tor daemon |
| `sudo systemctl restart hexstrike-server` | Restart MCP server systemd service |
| `sudo systemctl restart hexstrike-tgbot` | Restart Telegram bot systemd service |
| `journalctl -u hexstrike-server -f` | Tail live MCP server logs |
| `journalctl -u hexstrike-tgbot -f` | Tail live Telegram bot logs |
| `bash scripts/install_tools.sh` | Install all 150+ external security tools |
| `bash scripts/tool_check.sh` | Verify all tools are installed and accessible in PATH |
| `nuclei -update-templates` | Download/update Nuclei vulnerability templates |
| `kill $(lsof -t -i:8888)` | Kill any process occupying port 8888 |

---

## 14. Contributing

1. Fork the repository and clone your fork:
   ```bash
   git clone https://github.com/<your-username>/hexstrike-ai-dn.git
   cd hexstrike-ai-dn
   ```

2. Create a feature branch using the appropriate prefix:
   ```bash
   git checkout -b feat/your-feature-name
   # or: fix/bug-description  |  sec/vulnerability-patch
   ```

3. Make your changes inside an activated virtual environment (Python 3.10):
   ```bash
   python3.10 -m venv hexstrike_env
   source hexstrike_env/bin/activate
   pip install -r requirements.txt
   ```

4. Run linting before committing:
   ```bash
   pip install flake8
   flake8 . --max-line-length=120
   ```

5. Never commit `.env` or any file containing API keys, tokens, or credentials. Confirm:
   ```bash
   grep -r "VENICE_API_KEY\|BOT_TOKEN" --include="*.py" .
   # Must return no hardcoded values — only os.environ references
   ```

6. Open a pull request against `main` with the following checklist:
   - [ ] Tor routing preserved — `USE_TOR=true` tested, no DNS leaks
   - [ ] Venice AI model integration tested — abliterated model responds correctly
   - [ ] No hardcoded secrets in any committed file
   - [ ] Tested on Ubuntu 20.04 LTS over SSH

---

## 15. License

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

**HexStrike AI DN** · Ubuntu 20.04 VPS Edition · Autonomous offensive security via Telegram + Venice AI + Tor

*For authorised security testing only.*

</div>
