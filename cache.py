"""缓存模块 - 内存缓存 + 文件缓存"""

import os
import json
import time
import logging
import hashlib
import threading
from typing import Any, Optional

logger = logging.getLogger(__name__)


class Cache:
    """带 TTL 的两级缓存（内存 + 文件）"""

    def __init__(self, ttl: int = 3600, cache_dir: str = None):
        """
        Args:
            ttl: 缓存有效期（秒），默认 3600（60分钟）
            cache_dir: 文件缓存目录，None 则仅用内存缓存
        """
        self.ttl = ttl
        self.cache_dir = cache_dir
        self._memory: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)

    def _file_path(self, key: str) -> str:
        h = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{h}.json") if self.cache_dir else ""

    def get(self, key: str) -> Optional[Any]:
        """获取缓存，未命中或过期返回 None"""
        # 内存缓存
        with self._lock:
            if key in self._memory:
                ts, val = self._memory[key]
                if time.time() - ts < self.ttl:
                    logger.debug(f"缓存命中(内存): {key}")
                    return val
                del self._memory[key]

        # 文件缓存
        if self.cache_dir:
            fp = self._file_path(key)
            if os.path.exists(fp):
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if time.time() - data.get("ts", 0) < self.ttl:
                        val = data["val"]
                        with self._lock:
                            self._memory[key] = (data["ts"], val)
                        logger.debug(f"缓存命中(文件): {key}")
                        return val
                    os.remove(fp)
                except Exception:
                    pass

        return None

    def set(self, key: str, value: Any) -> None:
        """写入缓存"""
        ts = time.time()
        with self._lock:
            self._memory[key] = (ts, value)

        if self.cache_dir:
            fp = self._file_path(key)
            try:
                with open(fp, "w", encoding="utf-8") as f:
                    json.dump({"ts": ts, "val": value}, f, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"文件缓存写入失败: {e}")

    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._memory.clear()
        if self.cache_dir:
            for f in os.listdir(self.cache_dir):
                if f.endswith(".json"):
                    try:
                        os.remove(os.path.join(self.cache_dir, f))
                    except OSError:
                        pass

    def cleanup_expired(self) -> int:
        """清理过期的文件缓存，返回清理数量"""
        count = 0
        if self.cache_dir:
            now = time.time()
            for f in os.listdir(self.cache_dir):
                if not f.endswith(".json"):
                    continue
                fp = os.path.join(self.cache_dir, f)
                try:
                    with open(fp, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    if now - data.get("ts", 0) >= self.ttl:
                        os.remove(fp)
                        count += 1
                except Exception:
                    try:
                        os.remove(fp)
                        count += 1
                    except OSError:
                        pass
        return count
