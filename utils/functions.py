from datetime import datetime, timedelta
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

proxy_pattern = re.compile(
    r'(?:(https?|socks4|socks5)://)?((?:\d{1,3}\.){3}\d{1,3}):(\d{1,5})',
    re.IGNORECASE
)


def is_within_last_30_days(date_str):
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ") >= datetime.now() - timedelta(days=30)
