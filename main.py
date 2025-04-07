import os
import time
from threading import Thread

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

from utils.functions import logger
from utils.github import generate_raw_proxies
from utils.test_proxy import extract_and_test_proxies_concurrent

load_dotenv()
SECRET_PASSWORD = os.getenv("ACCESS_PASSWORD", "changeme")

DATA_DIR = "output"
RAW_FILENAME = "raw.txt"
PROXIES_FILENAME = "proxies.txt"

app = FastAPI()


def run_proxy_collection_loop(interval_minutes=1):
    while True:
        logger.info("🔄 Starting new proxy collection cycle...")

        raw_proxies = generate_raw_proxies()
        proxy_text = "\n".join(raw_proxies)

        os.makedirs(DATA_DIR, exist_ok=True)
        raw_path = os.path.join(DATA_DIR, RAW_FILENAME)
        with open(raw_path, "w") as f:
            f.write(proxy_text)

        working_proxies = extract_and_test_proxies_concurrent(proxy_text, max_workers=500)
        all_path = os.path.join(DATA_DIR, PROXIES_FILENAME)
        with open(all_path, "w") as f:
            f.write("\n".join(working_proxies))

        logger.info(f"✅ Saved raw: {RAW_FILENAME}, working: {PROXIES_FILENAME}")
        logger.info(f"🔐 Access with /download?file=raw.txt or proxies.txt&password=<your_password>")

        time.sleep(interval_minutes * 2)


@app.get("/")
def root():
    return {
        "status": "running",
        "usage": "GET /download?file=raw.txt OR proxies.txt&password=your_password",
        "files": [RAW_FILENAME, PROXIES_FILENAME]
    }


@app.get("/download")
def download_file(
        file: str = Query(...),
        password: str = Query(...)
):
    if password != SECRET_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid password")

    file_path = os.path.join(DATA_DIR, file)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=file, media_type="text/plain")


def start_background_loop():
    thread = Thread(target=run_proxy_collection_loop, daemon=True)
    thread.start()


if __name__ == "__main__":
    start_background_loop()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
