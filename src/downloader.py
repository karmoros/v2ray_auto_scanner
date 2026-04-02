import asyncio
import aiohttp
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"

async def fetch_text(session, url, timeout=10):
    try:
        async with session.get(url, timeout=timeout) as resp:
            resp.raise_for_status()
            return await resp.text()
    except Exception:
        return ""

async def download_urls(urls: List[str], max_nodes_per_source: int):
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_text(session, url) for url in urls]
        texts = await asyncio.gather(*tasks)

    for url, text in zip(urls, texts):
        if not text:
            continue
        lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
        if max_nodes_per_source > 0:
            lines = lines[:max_nodes_per_source]
        for line in lines:
            results.append((url, line))

    return results
