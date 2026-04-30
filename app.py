import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging


# === CONFIG ===
SOURCE_DIR = Path(r"C:\Handbrakes\Uncompressed") #The location of the file you want compressed 
DEST_DIR = Path(r"C:\Handbrakes\Compressed") #Where you want the compressed file to be saved to
HANDBRAKE_CLI = r"C:\Program Files\HandBrake\HandBrakeCLI.exe" #The location of the HandBrakeCLI.exe file on your system
PRESET = "Very Fast 480p30" #The preset you want to use you can find the list of presets by running `HandBrakeCLI --preset-list` in your command prompt.

MAX_CONCURRENT_JOBS = 1 #Set this number to the amount of concurrent jobs you want to run at once, be careful not to set this too high or you may run into performance issues. I recommend starting with 1 and increasing it if you have a powerful CPU and enough RAM.
DELAY_BETWEEN_JOBS = 10 #Set this number to the amount of seconds you want to wait between starting each job, this can help prevent performance issues when running multiple jobs at once. I recommend starting with 10 seconds and adjusting as needed.

VIDEO_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mov"] #file extensions to look for when scanning the source directory, you can add or remove extensions as needed


# === SETUP LOGGING ===
logging.basicConfig(
    filename="compression.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DEST_DIR.mkdir(parents=True, exist_ok=True)


def is_video(file):
    return file.suffix.lower() in VIDEO_EXTENSIONS


def compress_video(file):
    output_file = DEST_DIR / f"{file.stem}.mkv"

    if output_file.exists():
        logging.info(f"SKIPPED: {file.name}")
        return f"Skipped: {file.name}"

    command = [
        HANDBRAKE_CLI,
        "-i",
        str(file),
        "-o",
        str(output_file),
        "--preset",
        PRESET
    ]

    logging.info(f"START: {file.name}")
    print(f"Compressing: {file.name}")

    try:
        result = subprocess.run(command)

        success = (
            result.returncode == 0
            and output_file.exists()
            and output_file.stat().st_size > 0
        )

        if success:
            logging.info(f"SUCCESS: {file.name}")
            file.unlink()
            logging.info(f"DELETED: {file.name}")
            return f"Success: {file.name}"

        logging.error(f"FAILED: {file.name}")
        return f"Failed: {file.name}"

    except Exception as e:
        logging.error(f"ERROR: {file.name} - {e}")
        return f"Error: {file.name}"


def main():
    files = [
        f for f in SOURCE_DIR.iterdir()
        if f.is_file() and is_video(f)
    ]

    if not files:
        print("No video files found.")
        return

    print(
        f"Found {len(files)} files. "
        "Starting compression..."
    )

    with ThreadPoolExecutor(
        max_workers=MAX_CONCURRENT_JOBS
    ) as executor:

        futures = []

        for file in files:
            futures.append(
                executor.submit(compress_video, file)
            )
            time.sleep(DELAY_BETWEEN_JOBS)

        for future in as_completed(futures):
            print(future.result())

    print("All jobs completed.")


if __name__ == "__main__":
    main()
