# 🔴 RedZone.py — Advanced Web Defacement Framework

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.0-red?style=for-the-badge&logo=python" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-green?style=for-the-badge&logo=linux" alt="Platform">
  <img src="https://img.shields.io/badge/License-Educational-yellow?style=for-the-badge" alt="License">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Author-Hackfut%20Security-red?style=for-the-badge" alt="Author">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" alt="Status">
</p>

<p align="center">
  <b>🔴 RedZone.py</b> — An advanced WebDAV vulnerability testing & file upload framework with a modern cyberpunk interface.
</p>

---

## 📸 Preview

<p align="center">
  <img src="https://i.postimg.cc/bvBRXc8S/Screenshot-2026-11-26-1.png" alt="RedZone Interface" width="90%">
  <br>
  <i>RedZone.py — Cyberpunk Interface</i>
</p>

<p align="center">
  <img src="https://i.postimg.cc/j2VmbJKc/Screenshot-2026-11-26-3.png" alt="RedZone Results" width="90%">
  <br>
  <i>Real-time Results & Reporting</i>
</p>

---

## ⚡ Features

<table>
<tr>
<td width="50%">

### 🎯 Core Capabilities
- ✅ **14 WebDAV Bypass Methods**
- ✅ PUT Method Testing
- ✅ Content-Type Bypass
- ✅ Path Traversal Attacks
- ✅ Null Byte Injection
- ✅ Double Extension Bypass
- ✅ Case Sensitivity Bypass
- ✅ Header Injection
- ✅ Filename Obfuscation
- ✅ Chunked Encoding
- ✅ Unicode Normalization
- ✅ Windows Shortname
- ✅ Apache MultiViews
- ✅ HTTP Methods Enumeration

</td>
<td width="50%">

### 🚀 Advanced Features
- 🖥️ **Cyberpunk PyQt5 Interface**
- 📊 **Real-time Dashboard**
- 📁 **Single & Multi-target Testing**
- 🔍 **Port Scanning & Tech Detection**
- 🎭 **Stealth Mode with Random Delays**
- 🌐 **Proxy Rotation Support**
- 🎲 **User-Agent Randomization**
- 📤 **CSV / JSON Export**
- 📜 **Session History**
- 🌙 **System Tray Integration**
- ⚡ **Multi-threaded Engine**

</td>
</tr>
</table>

---

## 🛠️ Installation

### Prerequisites

```bash
# Python 3.8 or higher required
python3 --version
```

### Step 1: Clone the Repository

```bash
git clone https://github.com/HackfutSecRoot/deface_tool.git
cd deface_tool
```

### Step 2: Install Dependencies

```bash
pip install PyQt5 requests
```

<details>
<summary><b>📦 Full Requirements (click to expand)</b></summary>

```txt
PyQt5>=5.15.0
requests>=2.28.0
```

Or install everything at once:

```bash
pip install PyQt5 requests
```

</details>

### Step 3: Launch RedZone

```bash
python3 RedZone.py
```

> 💡 **Tip:** On Linux, you may need `sudo apt install python3-pyqt5` if PyQt5 fails to install via pip.

---

## 🚀 Quick Start

### 1️⃣ Single Target Test

```text
1. Open the "Single Test" tab
2. Enter target URL (e.g., https://example.com)
3. Browse and select your HTML/TXT file to upload
4. Configure timeout / stealth mode / random delay
5. Click "Start Test"
```

### 2️⃣ Multi-Target Test

```text
1. Open the "File Test" tab
2. Select a .txt file containing URLs (one per line)
3. Select your HTML/TXT payload file
4. Set number of workers & timeout
5. Click "Start Multi Test"
```

### 3️⃣ URL File Format

```txt
https://target1.com
http://target2.com
https://target3.com/path
```

---

## 🎨 Interface Overview

| Tab | Description |
|-----|-------------|
| **Single Test** | Test one target at a time with advanced options |
| **File Test** | Bulk testing from URL list file |
| **Settings** | Manage User-Agents & Proxies |
| **Dashboard** | Statistics & detailed results table |
| **History** | Session history & reloading |

---

## 🔬 Vulnerability Tests Explained

| Method | Description |
|--------|-------------|
| `test_put_method` | Direct PUT upload with verification |
| `test_content_type_bypass` | Spoofs `Content-Type: image/jpeg` |
| `test_path_traversal` | `../../` path traversal upload |
| `test_null_byte` | `%00` null byte injection |
| `test_double_extension` | `.html.jpg` double extension |
| `test_case_sensitivity` | Uppercase extension bypass |
| `test_header_injection` | `X-Forwarded-For` / `X-Real-IP` bypass |
| `test_filename_bypass` | Trailing dots, spaces, `::DATA` |
| `test_http_methods` | PROPFIND, MKCOL, COPY, MOVE, LOCK |
| `test_chunked_encoding` | `Transfer-Encoding: chunked` |
| `test_unicode_normalization` | RTL marks, BOM, invalid UTF-8 |
| `test_windows_shortname` | `AAAAAA~1.HTM` short name access |
| `test_path_obfuscation` | `/./`, `/.../`, `/..;/` tricks |
| `test_apache_multiview` | Extension-less upload |

---

## ⚙️ Configuration

### User-Agents Management

```text
Settings Tab → User Agents
├── Add custom UA
├── Remove selected
├── Generate random UA
└── Enable Auto Rotation
```

### Proxy Support

```text
Settings Tab → Proxies
├── Type: HTTP / HTTPS / SOCKS4 / SOCKS5
├── Add proxy (host:port)
├── Test proxy connectivity
└── Enable Auto Rotation
```

### Stealth Options

| Option | Effect |
|--------|--------|
| **Stealth Mode** | Random delay 1–5 seconds between requests |
| **Random Delay** | Random delay 0.1–2 seconds |
| **Verbose** | Detailed logging in output panel |

---

## 📊 Export Formats

### CSV Export
```csv
URL,Status,Ports,Technology,Methods,Upload
https://target.com,VULNERABLE,"[80, 443]","{'server': 'Apache'}",test_put_method,YES
```

### JSON Export
```json
{
  "https://target.com": {
    "status": "VULNERABLE",
    "methods": ["test_put_method", "test_content_type_bypass"],
    "uploaded": true,
    "method_used": "test_put_method",
    "ports": [80, 443],
    "technology": {"server": "Apache/2.4.41"}
  }
}
```

---

## 🔗 Official Channels

<p align="center">

### 📢 Telegram Channels
[![Channel 1](https://img.shields.io/badge/📢_Channel_1-Join-blue?style=for-the-badge&logo=telegram)](https://t.me/+gsrpvshwGUc5MzI0)
[![Channel 2](https://img.shields.io/badge/📢_Channel_2-Join-red?style=for-the-badge&logo=telegram)](https://t.me/LinxProdXs404)

### 💬 Community & Support
[![ULP Cloud](https://img.shields.io/badge/☁️_ULP_CLOUD-@ulp__CLOUD1-cyan?style=for-the-badge&logo=telegram)](https://t.me/ulp_CLOUD1)
[![DM](https://img.shields.io/badge/💬_DM-@HackfutS3c-purple?style=for-the-badge&logo=telegram)](https://t.me/HackfutS3c)

### 📝 Posts
[![Post 1](https://img.shields.io/badge/📝_Post_1-View-orange?style=for-the-badge&logo=telegram)](https://t.me/LinxProdXs404/249)
[![Post 2](https://img.shields.io/badge/📝_Post_2-View-orange?style=for-the-badge&logo=telegram)](https://t.me/LinxProdXs404/541)

### 🌐 Source Code
[![GitHub](https://img.shields.io/badge/GitHub-deface__tool-black?style=for-the-badge&logo=github)](https://github.com/HackfutSecRoot/deface_tool)
[![Pastebin](https://img.shields.io/badge/Pastebin-Hackfut-blue?style=for-the-badge&logo=pastebin)](https://pastebin.com/u/hackfut)

</p>

---

## 🧩 Project Structure

```text
deface_tool/
│
├── RedZone.py           # Main application
├── hack_bg.jpg          # Background image (auto-downloaded)
├── README.md            # This file
│
└── (optional)
    ├── targets.txt      # URL list for bulk testing
    └── payload.html     # Your defacement page
```

---

## ⚠️ Legal Disclaimer

> **🚨 IMPORTANT — READ CAREFULLY 🚨**

```text
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ⚠️  THIS TOOL IS PROVIDED FOR EDUCATIONAL AND              ║
║       AUTHORIZED SECURITY TESTING PURPOSES ONLY.             ║
║                                                              ║
║   ❌ Unauthorized use against systems you do not own         ║
║      or have explicit written permission to test is          ║
║      ILLEGAL and may result in criminal prosecution.         ║
║                                                              ║
║   ✅ Use ONLY on:                                            ║
║      • Your own systems                                     ║
║      • Systems you have written authorization for           ║
║      • CTF / Lab environments                               ║
║                                                              ║
║   📜 Users are solely responsible for their actions.         ║
║      The author (Hackfut Security) assumes NO liability      ║
║      for any misuse or damage caused by this tool.           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**By using RedZone.py, you agree that:**
- ✅ You will only test systems you own or have permission to test
- ✅ You understand the legal consequences of unauthorized access
- ✅ You take full responsibility for your actions
- ✅ The author is not responsible for any misuse

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

```bash
1. Fork the repository
2. Create a feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request
```

---

## 📜 License

```text
Educational Use License

Copyright (c) 2026 Hackfut Security

Permission is granted to use this software for educational
and authorized security testing purposes only.
```

---

## 🙏 Credits

<table align="center">
<tr>
<td align="center">
<b>👨‍💻 Developer</b><br>
<a href="https://t.me/HackfutS3c">Hackfut Security</a>
</td>
<td align="center">
<b>🎨 UI Framework</b><br>
PyQt5
</td>
<td align="center">
<b>🌐 HTTP Library</b><br>
Python Requests
</td>
</tr>
</table>

---

<p align="center">
  <b>⭐ If you find this tool useful, please give it a star! ⭐</b>
</p>

<p align="center">
  <a href="https://github.com/HackfutSecRoot/deface_tool">
    <img src="https://img.shields.io/github/stars/HackfutSecRoot/deface_tool?style=social" alt="Stars">
  </a>
  <a href="https://github.com/HackfutSecRoot/deface_tool/fork">
    <img src="https://img.shields.io/github/forks/HackfutSecRoot/deface_tool?style=social" alt="Forks">
  </a>
</p>

<p align="center">
  <sub>Made with ❤️ and 🔴 by <a href="https://t.me/HackfutS3c">Hackfut Security</a></sub>
  <br>
  <sub>© 2026 RedZone.py — All Rights Reserved</sub>
</p>
