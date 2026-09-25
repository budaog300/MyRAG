import asyncio
import statistics
import time

import httpx


collection_id = "218508ae-638f-4b38-a58c-01a084a8518a"
URL = f"http://localhost:8000/api/v1/collections/{collection_id}/search"

REQUEST_BODY = {
    "query": "Как включить потоковую генерацию токенов?",
    "only_context": False
}

# Сколько параллельных запросов делать в каждом батче
BATCH_SIZES = [1, 2, 4, 8, 16, 32] # [1, 2, 4, 8, 16]

# Таймаут одного запроса
TIMEOUT = 300.0


async def make_request(
    client: httpx.AsyncClient,
    request_number: int,
) -> dict:
    start = time.perf_counter()

    try:
        response = await client.post(
            URL,
            json=REQUEST_BODY,
        )

        elapsed = time.perf_counter() - start

        return {
            "number": request_number,
            "time": elapsed,
            "status": response.status_code,
            "success": response.is_success,
            "error": None,
        }

    except Exception as e:
        elapsed = time.perf_counter() - start

        return {
            "number": request_number,
            "time": elapsed,
            "status": None,
            "success": False,
            "error": f"{type(e).__name__}: {e}",
        }


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0

    values = sorted(values)

    index = (len(values) - 1) * p
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    if lower == upper:
        return values[lower]

    weight = index - lower

    return values[lower] + (values[upper] - values[lower]) * weight


async def run_batch(
    client: httpx.AsyncClient,
    batch_size: int,
) -> None:
    print()
    print("=" * 70)
    print(f"БАТЧ: {batch_size} параллельных запросов")
    print("=" * 70)

    batch_start = time.perf_counter()

    tasks = [
        make_request(client, i + 1)
        for i in range(batch_size)
    ]

    results = await asyncio.gather(*tasks)

    batch_time = time.perf_counter() - batch_start

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    times = [r["time"] for r in results]
    successful_times = [r["time"] for r in successful]

    print("\nЗапросы:")

    for result in results:
        status = result["status"]

        if result["success"]:
            print(
                f"  #{result['number']:02d} "
                f"{result['time']:.3f} сек "
                f"HTTP {status}"
            )
        else:
            print(
                f"  #{result['number']:02d} "
                f"{result['time']:.3f} сек "
                f"ERROR: {result['error']}"
            )

    print("\nМетрики:")

    print(f"  Всего запросов:        {len(results)}")
    print(f"  Успешных:              {len(successful)}")
    print(f"  Ошибок:                {len(failed)}")

    print(f"  Время батча:           {batch_time:.3f} сек")

    if times:
        print(f"  Минимальное время:     {min(times):.3f} сек")
        print(f"  Максимальное время:    {max(times):.3f} сек")
        print(f"  Среднее время:         {statistics.mean(times):.3f} сек")
        print(f"  Медиана:               {statistics.median(times):.3f} сек")
        print(f"  P95:                   {percentile(times, 0.95):.3f} сек")

    if successful_times:
        print(
            f"  Среднее успешных:      "
            f"{statistics.mean(successful_times):.3f} сек"
        )

    if batch_time > 0:
        print(f"  RPS:                   {len(results) / batch_time:.2f}")

    print()


async def main() -> None:
    limits = httpx.Limits(
        max_connections=100,
        max_keepalive_connections=100,
    )

    timeout = httpx.Timeout(TIMEOUT)

    async with httpx.AsyncClient(
        limits=limits,
        timeout=timeout,
    ) as client:

        print("RAG load test")
        print(f"URL: {URL}")
        print(f"Batch sizes: {BATCH_SIZES}")

        for batch_size in BATCH_SIZES:
            await run_batch(
                client,
                batch_size,
            )

            # Небольшая пауза между батчами
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())