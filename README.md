<div align="center">

# TENEBRINET
### ⫷ Intelligent Honeypot Infrastructure ⫸
<img width="3168" height="1344" alt="tenebrinet" src="https://github.com/user-attachments/assets/e132aa31-4281-4ef9-8333-195101906b18" />

*Ubi codex in tenebris susurrat*
*(Where code whispers in the shadows)*

<br>

[![Build Status](https://img.shields.io/github/actions/workflow/status/ind4skylivey/tenebrinet/ci.yml?branch=main&style=for-the-badge&color=0d1117&labelColor=7b2cbf)](https://github.com/ind4skylivey/tenebrinet/actions)
[![Security](https://img.shields.io/badge/security-HARDENED-00ff9f?style=for-the-badge&labelColor=0d1117&color=b00020)]()
[![Python](https://img.shields.io/badge/python-3.10+-7b2cbf?style=for-the-badge&logo=python&labelColor=0d1117&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-1a0033?style=for-the-badge&labelColor=0d1117&color=525252)](LICENSE)

[📡 INTEL](https://github.com/ind4skylivey/tenebrinet/wiki) • 
[⚡ DEPLOY](#-deployment-protocols) • 
[💀 ARCHITECTURE](#-system-architecture) • 
[👁️ RECON](#-operative-modules)

</div>

---

## 📟 // SYSTEM_OVERVIEW

> **INITIALIZING TENEBRINET...**
> Target Identification: Cyber Threats
> Mode: Active Interception & Analysis

**TenebriNET** is not just a honeypot; it is an **ML-powered threat intelligence infrastructure**. Engineered for security researchers and Red Teamers who need to dissect how adversaries operate in the wild. It captures, analyzes, and visualizes attack vectors in real-time, turning darkness into actionable data.

---

## 👁️ // OPERATIVE_MODULES

| Module | Functionality | Status |
| :--- | :--- | :---: |
| **🕸️ Digital Simulacra** | High-fidelity emulation of **SSH, HTTP, FTP** services with realistic interactions. | `ACTIVE` |
| **🧠 Neural Heuristics** | ML Engine that automatically classifies attacks (Recon, Brute Force, Exploits, Botnets). | `ONLINE` |
| **🗺️ Panopticon View** | Interactive dashboard with global real-time attack map. | `ONLINE` |
| **📡 Threat Feed** | Intelligence integration with **AbuseIPDB, VirusTotal, Shodan**. | `LINKED` |
| **📼 Forensic Replay** | Full recording of attack sessions for post-incident forensic analysis. | `READY` |
| **🐳 Dockerized** | One-command deployment for total environment isolation. | `READY` |

---

## ⚡ // DEPLOYMENT_PROTOCOLS

### System Requirements
* Python 3.10+
* Docker & Docker Compose (Recommended)
* PostgreSQL 14+ & Redis 6+

### Initialization Sequence

```bash
# ------------------------------------------------------------------
# [1] INITIATING REPOSITORY CLONE
# ------------------------------------------------------------------
git clone [https://github.com/ind4skylivey/tenebrinet.git](https://github.com/ind4skylivey/tenebrinet.git)
cd tenebrinet

# ------------------------------------------------------------------
# [2] DEPLOYMENT VECTORS
# ------------------------------------------------------------------

# >> OPTION A: Engage Docker Swarm (Recommended)
docker-compose up -d

# >> OPTION B: Manual Injection
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m tenebrinet.core.honeypot --config config/honeypot.yml

# ------------------------------------------------------------------
# [3] SYSTEM BOOT SEQUENCE
# ------------------------------------------------------------------

# [!] Initialize database schema
python scripts/init_db.py

# [!] Execute Core System
python -m tenebrinet.core.honeypot

# [+] SYSTEM ONLINE. LISTENING ON:
# > http://localhost:8080


💀 // SYSTEM_ARCHITECTURE
Code snippet

graph TD
    A[☠️ ATTACK SOURCES] -->|SSH / HTTP / Bots| B(🛡️ Honeypot Services)
    B -->|Raw Data| C{📝 Logging Layer}
    C -->|PostgreSQL + Redis| D[🧠 ML Engine]
    D -->|Threat Classification| E[🚀 FastAPI + WS]
    E -->|Real-time Feed| F[💻 Vue.js Dashboard]
    
    style A fill:#b00020,stroke:#333,stroke-width:2px,color:#fff
    style B fill:#1a0033,stroke:#7b2cbf,stroke-width:2px,color:#fff
    style D fill:#7b2cbf,stroke:#fff,stroke-width:2px,color:#fff
    style F fill:#0d1117,stroke:#00ff9f,stroke-width:2px,color:#fff

Threat Classification Matrix

TenebriNET's neural engine identifies 5 main categories of hostility:

    🔍 Reconnaissance: Port scans, service enumeration.

    🔐 Brute Force: Credential stuffing, password spraying.

    💥 Exploitation: CVE attempts, command injection, shellcode.

    🦠 Malware Deployment: Binary uploads, script execution, chmod +x.

    🤖 Botnet Activity: C2 callbacks, DDoS participation.

⚙️ // CONFIGURATION_VECTORS
YAML

# config/honeypot.yml
services:
  ssh:
    enabled: true
    port: 2222
    banner: "OpenSSH_8.2p1 Ubuntu-4ubuntu0.5" # Deception Banner
  
ml:
  model: "random_forest"
  retrain_interval: "24h"
  
threat_intel:
  abuseipdb_key: "${ABUSEIPDB_API_KEY}" # Redacted

🤝 // ALLIANCE

Contributions are welcome. Check the CONTRIBUTING.md to join the network.

Research Citation:
Code snippet

@software{tenebrinet2025,
  title={TenebriNET: Intelligent Honeypot Infrastructure},
  author={Fleming, Livey},
  year={2025},
  url={[https://github.com/ind4skylivey/tenebrinet](https://github.com/ind4skylivey/tenebrinet)}
}

<div align="center">

🌑 Where darkness meets defense

<sub>Made with 💜 & ☕ by <a href="https://github.com/ind4skylivey">ind4skylivey</a></sub>

</div>
