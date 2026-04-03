import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict


def get_base_dir() -> Path:
    # если упаковано в exe (PyInstaller)
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    # запуск как .py
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
sys.path.insert(0, str(BASE_DIR / "src"))

try:
    from downloader import download_urls
    from parser import parse_config_line
    from pinger import tcp_ping, tls_handshake
except ImportError as e:
    print(f"[!] Ошибка импорта: {e}")
    print("Убедись, что все файлы в папке src созданы правильно.")
    sys.exit(1)


CONFIG_DIR = BASE_DIR / "config"
OUTPUT_DIR = BASE_DIR / "output"


def ensure_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    settings_path = CONFIG_DIR / "settings.json"
    if not settings_path.exists():
        default_settings = {
            "subscriptions": [
                "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS_mobile.txt",
                "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
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
                "require_sid": True,
                "ports": [443, 8443, 80],
                "exclude_ips": []
            }
        }
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(default_settings, f, ensure_ascii=False, indent=4)
        print(f"[*] Создан файл настроек: {settings_path}")
        print("[*] Запускаю сканирование...\n")


def load_settings() -> Dict:
    settings_path = CONFIG_DIR / "settings.json"
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[!] Не найден файл: {settings_path}")
        print("Создай config/settings.json с настройками!")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"[!] Ошибка в формате JSON: {settings_path}")
        sys.exit(1)


async def scan_all(custom_subscriptions: List[str] = []) -> None:
    print("[*] V2Ray Auto Scanner запущен!")
    ensure_config()

    settings = load_settings()
    subscriptions = custom_subscriptions or settings.get("subscriptions", [])
    
    if not subscriptions:
        print("[!] Не указаны подписки в settings.json!")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Настройки
    timeout = float(settings.get("timeout_seconds", 3))
    max_concurrent = int(settings.get("max_concurrent_scans", 100))
    max_nodes_per_source = int(settings.get("max_nodes_per_source", 500))
    output_best_limit = int(settings.get("output_best_limit", 100))
    fallback_port = int(settings.get("tcp_ping_port_fallback", 443))

    # Новые настройки (можешь добавить в settings.json):
    ping_attempts = int(settings.get("ping_attempts", 2))          # попыток пинга на узел
    max_latency_ms = float(settings.get("max_latency_ms", 1500))   # отбраковка слишком медленных
    allowed_protocols = settings.get("allowed_protocols", [])      # например ["vless", "vmess"]

    print("[*] Загрузка списков конфигов...")
    raw_nodes = await download_urls(subscriptions, max_nodes_per_source)
    print(f"[*] Получено строк конфигов: {len(raw_nodes):,}")

    if not raw_nodes:
        print(" Не удалось скачать ни одного конфига!")
        return

    print("[*] Парсинг конфигов...")
    parsed_nodes: List[Dict] = []
    for src_url, line in raw_nodes:
        parsed = parse_config_line(line, fallback_port=fallback_port)
        if not parsed or not parsed.get("host"):
            continue

        # Фильтр по протоколам, если задан
        proto = parsed.get("protocol", "").lower()
        if allowed_protocols and proto not in [p.lower() for p in allowed_protocols]:
            continue

        # Фильтр: VLESS + TLS или Reality (упрощенный)
        if proto == "vless":
            security = parsed.get("security", "")
            network = parsed.get("network", "tcp")
            port = parsed.get("port", 0)
            sni = parsed.get("sni", "")
            flow = parsed.get("flow", "")
            
            # Принимаем: TLS, Reality, или даже без security
            is_valid = (
                security in ("tls", "reality") or 
                security == "" or
                security == "none"
            )
            
            if not is_valid:
                continue
            
            # Пропускаем любой порт

        parsed["source_url"] = src_url
        parsed["raw"] = line
        parsed_nodes.append(parsed)

    print(f"[*] Удалось распарсить узлов: {len(parsed_nodes):,}")

    if not parsed_nodes:
        print(" Не удалось распарсить ни одного узла!")
        return

    print(f"[*] Тестирование задержек (максимум {max_concurrent} одновременно)...")
    sem = asyncio.Semaphore(max_concurrent)
    results: List[Dict] = []

    async def worker(node: Dict) -> None:
        host = node["host"]
        port = node["port"]
        async with sem:
            try:
                # Для TLS конфигов используем TLS handshake тест
                if node.get("security") == "tls" and node.get("sni"):
                    sni = node.get("sni", "")
                    latency = await tls_handshake(host, port, sni, timeout=timeout, attempts=ping_attempts)
                    # Fallback на TCP если TLS не прошёл
                    if latency is None:
                        latency = await tcp_ping(host, port, timeout=timeout, attempts=ping_attempts)
                else:
                    latency = await tcp_ping(host, port, timeout=timeout, attempts=ping_attempts)
                
                if latency is not None and latency <= max_latency_ms:
                    node_result = dict(node)
                    node_result["latency_ms"] = round(latency, 1)
                    results.append(node_result)
                    print(f" {host}:{port} - {latency:.1f} ms ({node_result.get('protocol', '?')})")
                else:
                    pass
            except Exception:
                pass

    # Лимит в 2000 узлов оставляем, чтобы не ушатать сеть
    tasks = [asyncio.create_task(worker(n)) for n in parsed_nodes[:2000]]
    await asyncio.gather(*tasks, return_exceptions=True)

    print(f"\n[*] Найдено рабочих узлов (по TCP-тесту): {len(results):,}")

    if not results:
        print(" Не найдено ни одного рабочего узла!")
        return

    # Сортировка по задержке
    results.sort(key=lambda x: x["latency_ms"])
    best = results[:output_best_limit]

    fast_txt_path = OUTPUT_DIR / "fast_nodes.txt"
    fast_json_path = OUTPUT_DIR / "fast_nodes.json"

    loop_time = asyncio.get_event_loop().time()

    with open(fast_txt_path, "w", encoding="utf-8") as f:
        f.write(f"# Лучшие V2Ray конфиги (топ-{len(best)})\n")
        f.write(f"# Сканирование: {loop_time}\n\n")
        for i, node in enumerate(best, 1):
            f.write(f"#{i}. {node['latency_ms']} ms | {node.get('protocol', '?')} | "
                    f"{node['host']}:{node['port']}\n")
            f.write(f"{node['raw']}\n\n")

    with open(fast_json_path, "w", encoding="utf-8") as f:
        json.dump(best, f, ensure_ascii=False, indent=2)

    print(f"\n ГОТОВО! Сохранено {len(best)} лучших узлов:")
    print(f" Текстовый список: {fast_txt_path}")
    print(f" JSON: {fast_json_path}")
    print("\n Импортируй fast_nodes.txt в свой V2Ray-клиент!")


def run(custom_subscriptions: List[str] = None) -> None:
    try:
        subscriptions = custom_subscriptions or []
        asyncio.run(scan_all(subscriptions))
    except KeyboardInterrupt:
        print("\n[*] Остановлено пользователем")
    except Exception as e:
        print(f"[!] Критическая ошибка: {e}")


if __name__ == "__main__":
    run()
