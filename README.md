# V2Ray Auto Scanner

[![Release](https://img.shields.io/github/v/release/karmoros/v2ray_auto_scanner?include_prereleases&style=flat&label=Release)](https://github.com/karmoros/v2ray_auto_scanner/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Автоматический сканер VLESS/V2Ray конфигов с измерением задержки.

---

## 📥 Ready-to-use Downloads

**Latest Release:** [v1.0.6](https://github.com/karmoros/v2ray_auto_scanner/releases/latest)

| File | Description |
|------|-------------|
| `v2ray_auto_scanner.exe` | Готовый к запуску exe (папка `output/fast_nodes.txt` — текстовый список для импорта в V2Ray создастся автоматически) |

---

## 🚀 English Summary

v2ray_auto_scanner is an automated scanner for VLESS / VMESS / Shadowsocks proxy subscriptions. It downloads subscription links, parses proxy nodes, checks their availability and latency, and produces a sorted list of the fastest nodes.

### Main Features

- Supports VLESS, VMESS and Shadowsocks subscription links
- Measures latency (TCP/TLS handshake) and filters dead nodes
- Outputs results to plain text and JSON files
- CLI arguments for custom subscription URLs and node limits
- Docker image and standalone Windows .exe build
- This tool is designed for users who need to quickly find the fastest and most stable proxy nodes from public or private subscription sources.

---

## Supported Protocols

- **VLESS**
- **VMESS**
- **Shadowsocks**

---

## How It Works

1. Downloads one or more subscription URLs (HTTP/HTTPS).
2. Decodes and parses VLESS / VMESS / Shadowsocks links.
3. Normalizes all nodes to a common internal format.
4. Performs concurrent connectivity and latency checks.
5. Sorts nodes by latency and filters out dead or unstable ones.
6. Saves the final list to `output/fast_nodes.txt` and `output/fast_nodes.json`.

---

## 🚀 Quick Start

| OS | Command |
|----|---------|
| **Windows** | 1. Скачай `.exe` из Releases<br>2. Запусти |
| **macOS** / **Linux** | See below |
| **Docker** | `docker run -v $(pwd)/output:/app/output karmoros/v2ray_auto_scanner` |

```bash
pip install -r requirements.txt
python src/main.py
```

---

## 🐳 Docker

### Build
```bash
docker build -t karmoros/v2ray_auto_scanner .
```

### Run
```bash
docker run -v $(pwd)/output:/app/output karmoros/v2ray_auto_scanner
```

### Результат сохранится в папку `output/` на хосте.

---

## 📦 Python Dependencies

### Установка
```bash
pip install -r requirements.txt
```

### Требования к системе
- **Python 3.11+**
- **Linux/macOS:** Обычно дополнительные пакеты не нужны
- **Windows:** Python с python.org или из Microsoft Store

---

## ⚙️ Configuration

Edit `config/settings.json`:

```json
{
  "subscriptions": [
    "https://example.com/sub.txt"
  ],
  "timeout_seconds": 5,
  "max_concurrent_scans": 50,
  "max_nodes_per_source": 400,
  "output_best_limit": 80,
  "tcp_ping_port_fallback": 443,
  "ping_attempts": 2,
  "max_latency_ms": 1200,
  "allowed_protocols": ["vless"],
  "reality_filter": {
    "sni_whitelist": ["www.apple.com", "www.microsoft.com", "www.google.com", "www.cloudflare.com"],
    "fp_whitelist": ["chrome", "firefox", "random"],
    "require_sid": true,
    "ports": [443, 8443, 80],
    "exclude_ips": []
  }
}
```

Add more subscription URLs to exclude specific nodes (blacklist):

> ⚠️ Public proxy subscriptions may get blocked or throttled over time. Use only up-to-date and legally obtained subscription URLs.

---

## CLI Arguments

- `--subs` — кастомные подписки через запятую
- `--limit` — количество узлов для сохранения

```bash
python src/main.py --subs "https://example.com/sub.txt" --limit 50
```

---

## Результат

After scanning:
- `output/fast_nodes.txt` — текстовый список для импорта в V2Ray
- `output/fast_nodes.json` — JSON для машинной обработки

---

## Сборка .exe

```bash
pyinstaller --onefile --name v2ray_auto_scanner src/main.py
```

or run `build.bat` on Windows.

---

## Опционально: Telegram Bot

See `src/bot/README-bot.md` for setup instructions.

---

## Лицензия

MIT License — see LICENSE file.