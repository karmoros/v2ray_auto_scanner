# V2Ray Auto Scanner

Автоматический сканер VLESS/V2Ray конфигов с измерением задержки.

![v2ray_auto_scanner](v2ray_auto_scanner.ico)

## Возможности

- Скачивает конфиги из публичных подписок
- Автоматически парсит VLESS, VMESS, ShadowSocks ссылки
- Измеряет задержку узлов через TCP/TLS handshake
- Сортирует по скорости и сохраняет лучшие узлы
- Поддержка кастомных подписок через CLI

## Требования

- Python 3.10+ (рекомендуется 3.11 или 3.12)
- Доступ к GitHub для загрузки подписок

## Быстрый старт

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск

```bash
python src/main.py
```

или с кастомными подписками:

```bash
python src/main.py --subs "url1,url2"
```

## Конфигурация

Все настройки в `config/settings.json`:

```json
{
  "subscriptions": [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS_mobile.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
  ],
  "timeout_seconds": 5,
  "max_concurrent_scans": 50,
  "max_nodes_per_source": 400,
  "output_best_limit": 80,
  "max_latency_ms": 1200,
  "allowed_protocols": ["vless"]
}
```

## ⚠️ Важно

> **RKN блокирует публичные подписки!** В настройках указаны примеры подписок, которые могут не работать. Замените их на актуальные ссылки в `settings.json`.

## CLI Аргументы

- `--subs` — кастомные подписки через запятую (переопределяет settings.json)
- `--limit` — количество узлов для сохранения

Пример:
```bash
python src/main.py --subs "https://example.com/sub.txt" --limit 50
```

## Результат

После сканирования:
- `output/fast_nodes.txt` — текстовый список для импорта в V2Ray клиент
- `output/fast_nodes.json` — JSON для машинной обработки

## Сборка .exe

```bash
pyinstaller --onefile --icon=v2ray_auto_scanner.ico src/main.py
```

или запустите `build.bat` на Windows.

## Опционально: Telegram Bot

См. `src/bot/README-bot.md` для настройки.

## Лицензия

MIT License — см. файл LICENSE.
