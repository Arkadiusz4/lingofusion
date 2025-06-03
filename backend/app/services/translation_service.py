import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

from app.models.translator import (
    cached_translate_pl_en,
    cached_translate_en_pl,
)

executor = ThreadPoolExecutor(max_workers=1)


async def translate_lines_pl_en(lines: List[str]) -> List[str]:
    """
    Tłumaczy listę linii PL→EN, w osobnym wątku.
    """
    loop = asyncio.get_event_loop()
    results: List[str] = []
    for line in lines:
        if not line.strip():
            results.append("")  # pusta linia
        else:
            translated = await loop.run_in_executor(executor, cached_translate_pl_en, line)
            results.append(translated)
    return results


async def translate_lines_en_pl(lines: List[str]) -> List[str]:
    """
    Tłumaczy listę linii EN→PL, w osobnym wątku.
    """
    loop = asyncio.get_event_loop()
    results: List[str] = []
    for line in lines:
        if not line.strip():
            results.append("")
        else:
            translated = await loop.run_in_executor(executor, cached_translate_en_pl, line)
            results.append(translated)
    return results
