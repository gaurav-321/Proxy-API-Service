# Proxy API Service

A FastAPI service that collects, filters, and tests public HTTP/SOCKS proxies from GitHub repositories. Provides downloadable raw and verified proxy lists via a simple API.

---

## 🚀 Features

- Scrapes proxy list files from recently updated GitHub repositories
- Filters and extracts public IP:PORT proxies
- Concurrent proxy verification using HTTP/SOCKS support
- Password-protected API endpoints to download results
- Fully automated background collection and verification loop

---

## 🧰 Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) - Web API framework
- [httpx](https://www.python-httpx.org/) - Async-capable HTTP client
- [PySocks](https://pypi.org/project/PySocks/) - SOCKS proxy testing
- [dotenv](https://pypi.org/project/python-dotenv/) - Secrets management
- [tqdm](https://github.com/tqdm/tqdm) - Progress visualization
- [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html) - For concurrent proxy validation

---

## 📁 Directory Structure

```
project/
├── main.py                # FastAPI server and loop
├── output/                # Stores raw.txt and proxies.txt
├── utils/
│   ├── functions.py       # Common utilities (regex, logging)
│   ├── github.py          # GitHub scraping logic
│   └── test_proxy.py      # Proxy testing with concurrency
├── .env                   # Contains ACCESS_PASSWORD, GITHUB_TOKEN
└── requirements.txt       # Python dependencies
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory with the following content:

```env
ACCESS_PASSWORD=your_secure_password
GITHUB_TOKEN=your_github_token_optional
```

- `ACCESS_PASSWORD`: Required to download files from the API.
- `GITHUB_TOKEN`: Optional, increases GitHub API rate limit.

---

## 🛠 Setup & Usage

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the server

```bash
python main.py
```

By default, runs at: `http://127.0.0.1:8000`

---

## 📥 API Endpoints

### Health Check
`GET /`

Returns status and usage instructions.

### Download File
`GET /download?file=raw.txt&password=your_password`

- `file`: `raw.txt` or `proxies.txt`
- `password`: must match your `.env` `ACCESS_PASSWORD`

---

## 🔄 How It Works

### 1. GitHub Scraping (utils/github.py)
- Searches GitHub for repositories with terms like "proxies list"
- Filters files with proxy-related extensions (.txt, .csv, .json)
- Downloads raw file content and extracts public proxy IPs using regex

### 2. Proxy Testing (utils/test_proxy.py)
- Uses regex to extract IP, port, and protocol
- Tests proxies concurrently across HTTP/SOCKS4/SOCKS5
- Uses DNS ping and `httpbin.org` to validate working proxies

### 3. Automation Loop (main.py)
- Runs every 30 minutes by default
- Saves results to `output/raw.txt` (all scraped) and `output/proxies.txt` (working only)

---

## ⚙️ Customization

- Change scraping keywords in `generate_raw_proxies()`
- Modify GitHub file filters in `blacklist_keyword` or `valid_ext`
- Adjust thread pool size via `MAX_WORKERS`
- Tune interval in `run_proxy_collection_loop(interval_minutes=30)`

---

## 🧪 Sample Output

```
# raw.txt
123.45.67.89:8080
socks5://98.76.54.32:1080
...

# proxies.txt
http://123.45.67.89:8080
socks5://98.76.54.32:1080
...
```

---

## ⚠️ Disclaimer

This tool is provided for educational and research purposes only. Use responsibly and ensure compliance with applicable laws and service agreements.

---

## 📄 License

MIT License

