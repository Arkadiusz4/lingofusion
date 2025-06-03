import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

from app.models.corrector import cached_correct_gec

executor = ThreadPoolExecutor(max_workers=1)


async def correct_lines(lines: List[str]) -> List[str]:
    """
    Korekta listy linii tekstu (jedna linia = jedno zdanie lub co tam jest),
    każde wywołanie w osobnym wątku (Executor).
    """
    loop = asyncio.get_event_loop()
    results: List[str] = []
    for line in lines:
        if not line.strip():
            results.append("")
        else:
            corrected = await loop.run_in_executor(executor, cached_correct_gec, line)
            results.append(corrected)
    return results
