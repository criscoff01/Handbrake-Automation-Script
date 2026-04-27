import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# === CONFIG ===
SOURCE_DIR = Path(r"C:\Handbrakes\Uncompressed")
DEST_DIR = Path(r"C:\Handbrakes\Compressed")
HANDBRAKE_CLI = r"C:\Program Files\HandBrake\HandBrakeCLI.exe"
PRESET = "Very Fast 480p30"  # Better compression, slower

MAX_CONCURRENT_JOBS = 1   # Adjust based on CPU (2–4 is safe)
DELAY_BETWEEN_JOBS = 10    # Seconds between job starts (reduces CPU spikes)

VIDEO_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mov"]

# === SETUP LOGGING ===
logging.basicConfig(
    filename="compression.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Ensure destination exists
DEST_DIR.mkdir(parents=True, exist_ok=True)

def is_video(file):
    return file.suffix.lower() in VIDEO_EXTENSIONS

def compress_video(file):
    output_file = DEST_DIR / f"{file.stem}.mkv"

    # Skip if already exists
    if output_file.exists():
        logging.info(f"SKIPPED (already exists): {file.name}")
        return f"Skipped: {file.name}"

    command = [
        HANDBRAKE_CLI,
        "-i", str(file),
        "-o", str(output_file),
        "--preset", PRESET
    ]

    logging.info(f"START: {file.name}")
    print(f"Compressing: {file.name}")

    try:
        result = subprocess.run(command)

        # Validate output
        if result.returncode == 0 and output_file.exists() and output_file.stat().st_size > 0:
            logging.info(f"SUCCESS: {file.name}")

            # Delete original
            file.unlink()
            logging.info(f"DELETED ORIGINAL: {file.name}")

            return f"Success: {file.name}"

        else:
            logging.error(f"FAILED: {file.name}")
            return f"Failed: {file.name}"

    except Exception as e:
        logging.error(f"ERROR processing {file.name}: {e}")
        return f"Error: {file.name}"

def main():
    files = [f for f in SOURCE_DIR.iterdir() if f.is_file() and is_video(f)]

    if not files:
        print("No video files found.")
        return

    print(f"Found {len(files)} files. Starting compression...\n")

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_JOBS) as executor:
        futures = []

        for file in files:
            futures.append(executor.submit(compress_video, file))
            time.sleep(DELAY_BETWEEN_JOBS)  # throttle job start

        for future in as_completed(futures):
            print(future.result())

    print("\nAll jobs completed.")

if __name__ == "__main__":
    main()