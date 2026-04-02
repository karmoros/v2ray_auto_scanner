import asyncio
import socket
import ssl
import time
from typing import Optional


async def _single_tcp_ping(host: str, port: int, timeout: float = 3.0) -> Optional[float]:
    """
    Один TCP-пинг: connect -> небольшой handshake -> close.
    Возвращает задержку в мс или None при неуспехе.
    """
    start = time.perf_counter()
    try:
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)

        try:
            # Мягкий handshake: отправляем 1 байт и ждём до 0.5с.
            # Это отсеет часть "полу-живых" узлов с RST после SYN/ACK.
            writer.write(b"\x00")
            await writer.drain()
            try:
                await asyncio.wait_for(reader.read(1), timeout=0.5)
            except (asyncio.TimeoutError, ConnectionResetError):
                # Если тут таймаут/ресет — считаем хост сомнительным
                pass
        finally:
            writer.close()
            if hasattr(writer, "wait_closed"):
                await writer.wait_closed()

        end = time.perf_counter()
        return (end - start) * 1000.0
    except (asyncio.TimeoutError, OSError, ConnectionError):
        return None
    except Exception:
        return None


async def _single_tls_handshake(host: str, port: int, sni: str, timeout: float = 5.0) -> Optional[float]:
    """
    TLS handshake тест для VLESS Reality.
    Возвращает задержку в мс или None при неуспехе.
    """
    def run_sync():
        start = time.perf_counter()
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with socket.create_connection((host, port), timeout=timeout) as sock:
                with ctx.wrap_socket(sock, server_hostname=sni) as ssock:
                    version = ssock.version()
                    if version:
                        return (time.perf_counter() - start) * 1000.0
        except Exception:
            pass
        return None
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, run_sync)


async def tls_handshake(host: str, port: int, sni: str, timeout: float = 5.0, attempts: int = 2) -> Optional[float]:
    """
    Делает несколько попыток TLS handshake и возвращает среднюю задержку.
    """
    latencies = []
    for _ in range(max(1, attempts)):
        latency = await _single_tls_handshake(host, port, sni, timeout=timeout)
        if latency is not None:
            latencies.append(latency)

    if not latencies:
        return None

    return sum(latencies) / len(latencies)


async def tcp_ping(host: str, port: int, timeout: float = 3.0, attempts: int = 2) -> Optional[float]:
    """
    Делает несколько попыток TCP-пинга и возвращает среднюю задержку
    по успешным, либо None, если все неудачные.
    """
    latencies = []
    for _ in range(max(1, attempts)):
        latency = await _single_tcp_ping(host, port, timeout=timeout)
        if latency is not None:
            latencies.append(latency)

    if not latencies:
        return None

    return sum(latencies) / len(latencies)
