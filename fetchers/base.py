"""基础爬取器，提供公共请求方法"""

import os
import requests
import time
import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;"
              "q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

REQUEST_TIMEOUT = 15
RETRY_COUNT = 2

# 系统代理缓存（只检测一次）
_system_proxy: Optional[str] = None


def _detect_system_proxy() -> Optional[str]:
    """检测 macOS 系统代理设置，返回 http/https 代理地址"""
    global _system_proxy
    if _system_proxy is not None:
        return _system_proxy or None

    # 1) 优先用环境变量
    env_proxy = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") or \
                os.environ.get("http_proxy") or os.environ.get("HTTP_PROXY") or \
                os.environ.get("ALL_PROXY")
    if env_proxy:
        _system_proxy = env_proxy
        return env_proxy

    # 2) 检查 macOS 系统代理（PAC / HTTP / SOCKS）
    try:
        result = subprocess.run(
            ["scutil", "--proxy"],
            capture_output=True, text=True, timeout=3
        )
        output = result.stdout

        # 检查 HTTP 代理
        if "HTTPEnable : 1" in output:
            import re
            host_m = re.search(r"HTTPProxy\s*:\s*(\S+)", output)
            port_m = re.search(r"HTTPPort\s*:\s*(\d+)", output)
            if host_m and port_m:
                _system_proxy = f"http://{host_m.group(1)}:{port_m.group(1)}"
                return _system_proxy

        # 检查 HTTPS 代理
        if "HTTPSEnable : 1" in output:
            import re
            host_m = re.search(r"HTTPSProxy\s*:\s*(\S+)", output)
            port_m = re.search(r"HTTPSPort\s*:\s*(\d+)", output)
            if host_m and port_m:
                _system_proxy = f"http://{host_m.group(1)}:{port_m.group(1)}"
                return _system_proxy

        # 检查 SOCKS 代理
        if "SOCKSEnable : 1" in output:
            import re
            host_m = re.search(r"SOCKSProxy\s*:\s*(\S+)", output)
            port_m = re.search(r"SOCKSPort\s*:\s*(\d+)", output)
            if host_m and port_m:
                _system_proxy = f"socks5://{host_m.group(1)}:{port_m.group(1)}"
                return _system_proxy

        # 检查 PAC 自动代理
        if "ProxyAutoConfigEnable : 1" in output:
            import re
            pac_m = re.search(r"ProxyAutoConfigURLString\s*:\s*(\S+)", output)
            if pac_m:
                pac_url = pac_m.group(1)
                # 尝试下载 PAC 文件解析代理
                try:
                    import urllib.request
                    req = urllib.request.Request(pac_url)
                    with urllib.request.urlopen(req, timeout=3) as resp:
                        pac_content = resp.read().decode("utf-8", errors="ignore")
                    # 从 PAC 中提取代理地址
                    # PAC 格式多样: "PROXY host:port; SOCKS5 ..." 或 "PROXY host:port"
                    import re
                    proxy_m = re.search(
                        r'return\s+"(?:.*?)(?:PROXY|SOCKS5?)\s+([\w.\-]+:\d+)',
                        pac_content
                    )
                    if proxy_m:
                        proxy_addr = f"http://{proxy_m.group(1)}"
                        _system_proxy = proxy_addr
                        logger.info(f"🔍 从 PAC 检测到代理: {_system_proxy}")
                        return _system_proxy
                except Exception:
                    pass
    except Exception:
        pass

    _system_proxy = ""  # 标记已检测，无代理
    return None


class BaseFetcher:
    """所有爬取器的基类"""

    name: str = "base"
    display_name: str = "基础"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        # 自动配置系统代理
        proxy = _detect_system_proxy()
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
            logger.debug(f"[{self.name}] 使用代理: {proxy}")

    def _get(self, url: str, params: Optional[dict] = None,
             headers: Optional[dict] = None, as_json: bool = False):
        """带重试的 GET 请求"""
        for attempt in range(RETRY_COUNT):
            try:
                resp = self.session.get(
                    url, params=params, headers=headers,
                    timeout=REQUEST_TIMEOUT
                )
                resp.raise_for_status()
                if as_json:
                    return resp.json()
                return resp.text
            except Exception as e:
                logger.warning(f"[{self.name}] 请求失败 (尝试 {attempt+1}/{RETRY_COUNT}): {e}")
                if attempt < RETRY_COUNT - 1:
                    time.sleep(2)
        return None

    def fetch(self) -> list:
        """子类必须实现，返回标准化的热点列表"""
        raise NotImplementedError
