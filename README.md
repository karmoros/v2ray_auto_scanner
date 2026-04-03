# V2Ray Auto Scanner

[![Release](https://img.shields.io/github/v/release/karmoros/v2ray_auto_scanner?include_prereleases&style=flat&label=Release)](https://github.com/karmoros/v2ray_auto_scanner/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Автоматический сканер VLESS/V2Ray конфигов с измерением задержки.


---

## 📥 Ready-to-use Downloads

**Latest Release:** [v1.0.3](https://github.com/karmoros/v2ray_auto_scanner/releases/latest)

| File | Description |
|------|-------------|
| `v2ray_auto_scanner.exe` | Готовый к запуску exe (- `output/fast_nodes.txt` — текстовый список для импорта в V2Ray создастся автоматически) |

---

## 🚀 Быстрый старт

| OS | Command |
|----|---------|
| **Windows** | 1. Скачай `.exe` из Releases<br>2.  Запусти |
| **macOS** | `pip install -r requirements.txt && python src/main.py` |
| **Linux** | `pip install -r requirements.txt && python src/main.py` |
| **Docker** | `docker run -v $(pwd)/output:/app/output karmoros/v2ray_auto_scanner` |

```bash
# Из исходников (любой OS):
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

## ⚙️ Настройки

Отредактируй `settings.json`:

```json
{
  "subscriptions": [
    "https://your-sub.com/sub.txt"
  ],
  "timeout_seconds": 5,
  "max_concurrent_scans": 50
}
```

> ⚠️ **RKN банит публичные подписки!** меняйте ссылки на актуальные.

---

## Возможности

- Скачивает конфиги из публичных подписок
- Автоматически парсит VLESS, VMESS, ShadowSocks ссылки
- Измеряет задержку узлов через TCP/TLS handshake
- Сортирует по скорости и сохраняет лучшие узлы
- Поддержка кастомных подписок через CLI

## CLI Аргументы

- `--subs` — кастомные подписки через запятую
- `--limit` — количество узлов для сохранения

```bash
python src/main.py --subs "https://example.com/sub.txt" --limit 50
```

## Результат

После сканирования:
- `output/fast_nodes.txt` — текстовый список для импорта в V2Ray
- `output/fast_nodes.json` — JSON для машинной обработки

## Сборка .exe

```bash
pyinstaller --onefile --name v2ray_auto_scanner src/main.py
```

или запустите `build.bat` на Windows.

## Опционально: Telegram Bot

См. `src/bot/README-bot.md` для настройки.

## Лицензия

MIT License — см. файл LICENSE.
