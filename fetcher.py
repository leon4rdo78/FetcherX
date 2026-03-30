import time
from datetime import datetime
from pathlib import Path

import requests

URLS = [
    "https://raw.githubusercontent.com/mohamadfg-dev/telegram-v2ray-configs-collector/refs/heads/main/category/Iran.txt",
    "https://raw.githubusercontent.com/miladtahanian/Config-Collector/refs/heads/main/mixed_iran.txt",
    "https://raw.githubusercontent.com/crackbest/V2ray-Config/refs/heads/main/config.txt",
    "https://raw.githubusercontent.com/miladtahanian/V2RayCFGDumper/refs/heads/main/sub.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/refs/heads/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/Surfboardv2ray/Proxy-sorter/refs/heads/main/output/IR.txt",
    "https://raw.githubusercontent.com/SoliSpirit/v2ray-configs/refs/heads/main/Countries/Iran.txt",
]

FETCH_TIMEOUT_SECONDS = 10
RETRY_COUNT = 10

ARCHIVE_DIR = Path("./archive")
LOG_DIR = Path("./logs")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}


def ensure_dirs() -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def timestamp_for_filename() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def fetch_with_retries(url: str, timeout: int, retry_count: int) -> tuple[bool, str]:
    last_error = ""

    for attempt in range(1, retry_count + 1):
        try:
            print(f"  Attempt {attempt}/{retry_count}")
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=timeout,
            )
            response.raise_for_status()

            text = response.text.strip()
            if text:
                return True, text

            last_error = "Empty response"

        except Exception as e:
            last_error = str(e)

        if attempt < retry_count:
            time.sleep(1)

    return False, last_error


def save_archive_file(all_results: list[tuple[str, str]]) -> Path:
    ts = timestamp_for_filename()
    output_file = ARCHIVE_DIR / f"{ts}_configs.txt"

    with output_file.open("w", encoding="utf-8", newline="\n") as f:
        for index, (url, content) in enumerate(all_results, start=1):
            f.write("=" * 100 + "\n")
            f.write(f"SOURCE {index}\n")
            f.write(f"URL: {url}\n")
            f.write("=" * 100 + "\n")
            f.write(content)
            f.write("\n\n")

    return output_file


def save_failed_log(failures: list[tuple[str, str]]) -> Path | None:
    if not failures:
        return None

    ts = timestamp_for_filename()
    log_file = LOG_DIR / f"{ts}_failed.txt"

    with log_file.open("w", encoding="utf-8", newline="\n") as f:
        for index, (url, error) in enumerate(failures, start=1):
            f.write(f"[{index}] {url}\n")
            f.write(f"ERROR: {error}\n")
            f.write("-" * 100 + "\n")

    return log_file


def run_once() -> None:
    ensure_dirs()

    successful_results: list[tuple[str, str]] = []
    failed_results: list[tuple[str, str]] = []

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting fetch cycle...")

    for url in URLS:
        print(f"Fetching: {url}")
        ok, result = fetch_with_retries(
            url=url,
            timeout=FETCH_TIMEOUT_SECONDS,
            retry_count=RETRY_COUNT,
        )

        if ok:
            successful_results.append((url, result))
            print("  Success")
        else:
            failed_results.append((url, result))
            print(f"  Failed: {result}")

    if successful_results:
        archive_file = save_archive_file(successful_results)
        print(f"Saved archive: {archive_file}")
    else:
        print("No successful results to save.")

    failed_log = save_failed_log(failed_results)
    if failed_log:
        print(f"Saved failure log: {failed_log}")

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetch cycle finished.")


def main() -> None:
    try:
        run_once()
    except Exception as e:
        ensure_dirs()
        ts = timestamp_for_filename()
        log_file = LOG_DIR / f"{ts}_failed.txt"

        with log_file.open("w", encoding="utf-8", newline="\n") as f:
            f.write(f"Fatal cycle error: {e}\n")

        print(f"Fatal cycle error logged to: {log_file}")
        raise


if __name__ == "__main__":
    main()
