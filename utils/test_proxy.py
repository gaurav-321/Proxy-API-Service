from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx
import socks
from tqdm import tqdm

from utils.functions import proxy_pattern, logger


# -------------------- Logger Setup -------------------- #


# -------------------- Regex Pattern -------------------- #


# -------------------- Proxy Checkers -------------------- #

def test_socks_proxy(ip, port, proto="socks5", timeout=5):
    try:
        sock_type = {
            "socks5": socks.SOCKS5,
            "socks4": socks.SOCKS4,
        }.get(proto)

        if sock_type is None:
            return False

        s = socks.socksocket()
        s.set_proxy(sock_type, ip, int(port))
        s.settimeout(timeout)
        s.connect(("1.1.1.1", 53))  # Lightweight test
        s.close()
        return True
    except Exception:
        return False


def test_http_proxy(ip, port, proto="http", timeout=5):
    try:
        url = "http://httpbin.org/ip"
        proxy_url = f"{proto}://{ip}:{port}"
        with httpx.Client(proxies=proxy_url, timeout=timeout) as client:
            response = client.get(url)
            return response.status_code == 200
    except Exception:
        return False


# -------------------- Unified Worker -------------------- #

def proxy_worker(match):
    proto, ip, port = match.groups()
    port = int(port)

    if proto:
        proto = proto.lower()
        if proto in ["socks4", "socks5"]:
            if test_socks_proxy(ip, port, proto):
                return f"{proto}://{ip}:{port}"
        elif proto in ["http", "https"]:
            if test_http_proxy(ip, port, proto):
                return f"{proto}://{ip}:{port}"
    else:
        # Try all protocols in order: socks5, socks4, http, https
        for p in ["socks5", "socks4", "http", "https"]:
            if p.startswith("socks") and test_socks_proxy(ip, port, p):
                return f"{p}://{ip}:{port}"
            elif p in ["http", "https"] and test_http_proxy(ip, port, p):
                return f"{p}://{ip}:{port}"

    return None


# -------------------- Main Function -------------------- #

def extract_and_test_proxies_concurrent(proxy_text, max_workers=50):
    matches = list(proxy_pattern.finditer(proxy_text))
    working = []

    logger.info(f"Testing {len(matches)} proxies using {max_workers} threads...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(proxy_worker, match) for match in matches]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Testing Proxies"):
            result = future.result()
            if result:
                logger.info(f"✅ Working proxy: {result}")
                working.append(result)

    return working


# -------------------- Entry Point -------------------- #

if __name__ == '__main__':
    with open("proxies_extracted.txt") as f:
        proxy_text = f.read()

    working_proxies = extract_and_test_proxies_concurrent(proxy_text, max_workers=1000)

    print("\n=== Working Proxies ===")
    for p in working_proxies:
        print(p)

    logger.info(f"✅ {len(working_proxies)} working proxies found.")
