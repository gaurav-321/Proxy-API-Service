import ipaddress
import os
import re
from concurrent.futures import ThreadPoolExecutor, wait

import httpx
import tqdm

from dotenv import load_dotenv
from utils.functions import logger, is_within_last_30_days, proxy_pattern

# --------------------------- Setup --------------------------- #
load_dotenv()

bar_repo = tqdm.tqdm(desc="Repo Lists")
bar_files = tqdm.tqdm(desc="Files Url")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
headers = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else None
}

MAX_WORKERS = 50
proxies = []
raw_files = []


blacklist_keyword = [
    "README.md", "README", "README.txt", "LICENSE", "LICENSE.txt", "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md", "SECURITY.md", "CHANGELOG.md", "CHANGES.md", "TODO.md", "INSTALL.md",
    "SETUP.md", "requirements.txt", "Pipfile", "Pipfile.lock", "environment.yml", ".gitignore",
    ".gitattributes", ".github/", ".github/workflows/", ".gitmodules", "Makefile", "Dockerfile",
    "docker-compose.yml", "package.json", "package-lock.json", "yarn.lock", "tsconfig.json",
    "babel.config.js", "webpack.config.js", "CMakeLists.txt", "build.gradle", "pom.xml", "Gemfile",
    "Gemfile.lock", "setup.py", "pyproject.toml", "MANIFEST.in"
]

valid_ext = [".txt", ".json", ".csv"]


# ------------------------ Utility Functions ------------------------ #
def extract_best_proxies(proxy_list_text):
    # Pattern to match IP:PORT with optional protocol prefix
    proxy_map = {}  # key = IP, value = longest version (full match)
    for match in proxy_pattern.finditer(proxy_list_text):
        full = match.group(0)  # full match (e.g., socks5://ip:port or ip:port)
        ip = match.group(2)
        if ip not in proxy_map or len(full) > len(proxy_map[ip]):
            proxy_map[ip] = full

    return list(proxy_map.values())


def filter_public_proxies(proxy_text):
    proxies = []
    for match in list(proxy_pattern.finditer(proxy_text)):
        try:
            proto, ip, port = match.groups()
            full = match.group(0)
            if ipaddress.ip_address(ip).is_global:
                proxies.append(full)
        except ValueError:
            continue
    return proxies


def get_file_content_and_extract(download_link):
    try:
        logger.info(download_link)
        with httpx.Client(timeout=10.0) as client:
            response = client.get(download_link)
        bar_files.update(1)
        if response.status_code == 200:
            proxies.extend(filter_public_proxies(response.text))
        else:
            logger.warning(f"Failed to fetch content from {download_link} - Status: {response.status_code}")
    except httpx.TimeoutException:
        logger.error(f"Timeout when fetching {download_link}")
    except httpx.RequestError as e:
        logger.error(f"Exception fetching {download_link}: {e}")


# ------------------------ Repo Processing ------------------------ #

def process_repo(username, repo):
    logger.info(f"Processing repo: {username}/{repo}")
    url = f"https://api.github.com/repos/{username}/{repo}/contents/"
    logger.info(f"Fetching {url}")

    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.get(url, headers=headers)
        if response.status_code == 200:
            items = response.json()
            if len(items) < 15:
                files = [
                    item for item in items
                    if item['type'] == 'file'
                       and item['size'] // 1024 > 1
                       and item['name'].lower().endswith(tuple(valid_ext))
                       and item['name'].lower() not in blacklist_keyword
                ]

                logger.info(f"Number of files for {username}/{repo}: {len(files)}")
                raw_files.extend(files)
            else:
                logger.info(f"Skipping {url}, max file exceeded")
        else:
            logger.warning(f"Failed to fetch {url} - Status: {response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Error listing files in {repo}: {e}")

    bar_repo.update(1)


# ------------------------ GitHub Repo Search ------------------------ #

def search_github_repos(query, sort='updated', order='desc', per_page=30):
    url = "https://api.github.com/search/repositories"
    params = {'q': query, 'sort': sort, 'order': order, 'per_page': per_page}

    logger.info(f"Searching GitHub for: '{query}'")

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params, headers=headers)
        if response.status_code != 200:
            logger.error(f"GitHub API error: {response.status_code}")
            return []

        repos = response.json().get('items', [])
        valid = [
            (r['owner']['login'], r['name']) for r in repos
            if is_within_last_30_days(r['updated_at'])
        ]

        logger.info(f"Found {len(valid)} recently updated repos")
        return valid

    except httpx.RequestError as e:
        logger.error(f"Search request failed: {e}")
        return []


# ------------------------ Main ------------------------ #


def generate_raw_proxies():
    search_term = "proxies list"
    repo_tuples = search_github_repos(search_term)
    bar_repo.total = len(repo_tuples)

    logger.info(f"Processing {len(repo_tuples)} repositories")

    # Run repo processing concurrently
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        repo_futures = [executor.submit(process_repo, username, repo) for username, repo in repo_tuples]
        wait(repo_futures)

    raw_files.sort(key=lambda x: x['size'], reverse=True)
    bar_files.total = len(raw_files)

    # Run file content extraction concurrently
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        file_futures = [executor.submit(get_file_content_and_extract, file['download_url']) for file in raw_files]
        done, not_done = wait(file_futures, timeout=60)

        logger.info(f"{len(done)} file downloads completed, {len(not_done)} did not finish.")
        for future in not_done:
            future.cancel()

    best_proxies = extract_best_proxies("\n".join(proxies))
    logger.info(f"Extracted {len(set(proxies))} unique proxies.")
    with open("output/raw.txt", "w") as f:
        f.write("\n".join(best_proxies))
    return sorted(set(best_proxies))


if __name__ == "__main__":
    generate_raw_proxies()
