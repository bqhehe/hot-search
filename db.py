"""SQLite 数据持久化 - 热点数据存储与查询"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# 默认数据库路径
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "hot.db")


def _get_db_path(db_path: str = None) -> str:
    if db_path:
        return db_path
    return os.environ.get("HOT_DB_PATH", DEFAULT_DB_PATH)


@contextmanager
def _get_conn(db_path: str = None):
    """获取数据库连接（上下文管理器）"""
    path = _get_db_path(db_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str = None):
    """初始化数据库表结构"""
    with _get_conn(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS fetch_batches (
                id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                mode TEXT NOT NULL DEFAULT 'api',
                platform_count INTEGER DEFAULT 0,
                item_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS hot_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT,
                hot TEXT,
                label TEXT,
                rank INTEGER,
                source TEXT,
                content TEXT,
                fetched_at TEXT NOT NULL,
                title_hash TEXT,
                FOREIGN KEY (batch_id) REFERENCES fetch_batches(id)
            );

            CREATE INDEX IF NOT EXISTS idx_items_platform
                ON hot_items(platform);
            CREATE INDEX IF NOT EXISTS idx_items_fetched_at
                ON hot_items(fetched_at);
            CREATE INDEX IF NOT EXISTS idx_items_title_hash
                ON hot_items(title_hash);
            CREATE INDEX IF NOT EXISTS idx_items_batch_id
                ON hot_items(batch_id);
            CREATE INDEX IF NOT EXISTS idx_batches_started_at
                ON fetch_batches(started_at);
        """)
    logger.debug("数据库初始化完成")


def _title_hash(title: str) -> str:
    """生成标题哈希（用于去重判断）"""
    import hashlib
    # 去除空格和标点后取 hash
    clean = "".join(c for c in title if c.isalnum())
    return hashlib.md5(clean.encode("utf-8")).hexdigest()[:16]


def save_batch(
    all_data: dict,
    mode: str = "api",
    source_stats: dict = None,
    db_path: str = None,
) -> str:
    """保存一次抓取的所有数据

    Args:
        all_data: {平台名: [items]} 格式的抓取结果
        mode: 抓取模式 (api/off/only)
        source_stats: 数据源统计
        db_path: 数据库路径

    Returns:
        batch_id
    """
    init_db(db_path)
    batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    now = datetime.now().isoformat()
    total_items = sum(len(v) for v in all_data.values())
    success_count = sum(1 for v in all_data.values() if v)
    fail_count = sum(1 for v in all_data.values() if not v)

    with _get_conn(db_path) as conn:
        # 写入 batch
        conn.execute(
            """INSERT INTO fetch_batches
               (id, started_at, finished_at, mode, platform_count,
                item_count, success_count, fail_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (batch_id, now, now, mode, len(all_data),
             total_items, success_count, fail_count),
        )

        # 批量写入 items
        per_platform = source_stats.get("_per_platform", {}) if source_stats else {}
        rows = []
        for platform_name, items in all_data.items():
            src = per_platform.get(platform_name, "unknown")
            for item in items:
                title = str(item.get("title", ""))
                rows.append((
                    batch_id,
                    platform_name,
                    title,
                    str(item.get("url", "")),
                    str(item.get("hot", "")),
                    str(item.get("label", "")),
                    int(item.get("rank", 0)),
                    src,
                    str(item.get("content", "") or ""),
                    now,
                    _title_hash(title),
                ))

        if rows:
            conn.executemany(
                """INSERT INTO hot_items
                   (batch_id, platform, title, url, hot, label, rank,
                    source, content, fetched_at, title_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                rows,
            )

    logger.info(f"已保存批次 {batch_id}: {total_items} 条 / {len(all_data)} 个平台")
    return batch_id


def query_latest(
    platform: str = None,
    limit: int = 30,
    db_path: str = None,
) -> list[dict]:
    """查询最新一批数据

    Args:
        platform: 指定平台名，None 表示全部
        limit: 每个平台最多返回条数
    """
    init_db(db_path)
    with _get_conn(db_path) as conn:
        # 找最新 batch
        row = conn.execute(
            "SELECT id FROM fetch_batches ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        if not row:
            return []

        batch_id = row["id"]
        if platform:
            rows = conn.execute(
                """SELECT * FROM hot_items
                   WHERE batch_id = ? AND platform = ?
                   ORDER BY rank LIMIT ?""",
                (batch_id, platform, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM hot_items
                   WHERE batch_id = ?
                   ORDER BY platform, rank LIMIT ?""",
                (batch_id, limit),
            ).fetchall()

    return [dict(r) for r in rows]


def query_trending(
    hours: int = 24,
    min_platforms: int = 2,
    limit: int = 50,
    db_path: str = None,
) -> list[dict]:
    """查询跨平台趋势话题（同一话题出现在多个平台）

    Args:
        hours: 查询最近 N 小时
        min_platforms: 至少出现在几个平台
        limit: 返回条数

    Returns:
        [{title, platforms: [str], platform_count, first_seen}] 列表
    """
    init_db(db_path)
    since = (datetime.now() - timedelta(hours=hours)).isoformat()

    with _get_conn(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
                title,
                GROUP_CONCAT(DISTINCT platform) AS platforms,
                COUNT(DISTINCT platform) AS platform_count,
                MIN(fetched_at) AS first_seen,
                MAX(hot) AS max_hot
            FROM hot_items
            WHERE fetched_at > ?
            GROUP BY title_hash
            HAVING platform_count >= ?
            ORDER BY platform_count DESC, max_hot DESC
            LIMIT ?
            """,
            (since, min_platforms, limit),
        ).fetchall()

    return [dict(r) for r in rows]


def query_platform_history(
    platform: str,
    days: int = 7,
    db_path: str = None,
) -> list[dict]:
    """查询某个平台的历史数据（每天一条快照）

    Args:
        platform: 平台名
        days: 查询最近 N 天
    """
    init_db(db_path)
    since = (datetime.now() - timedelta(days=days)).isoformat()

    with _get_conn(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
                DATE(fetched_at) AS date,
                COUNT(*) AS item_count,
                GROUP_CONCAT(title, '||') AS titles
            FROM hot_items
            WHERE platform = ? AND fetched_at > ?
            GROUP BY DATE(fetched_at)
            ORDER BY date DESC
            """,
            (platform, since),
        ).fetchall()

    return [dict(r) for r in rows]


def query_stats(db_path: str = None) -> dict:
    """查询数据库统计信息"""
    init_db(db_path)
    with _get_conn(db_path) as conn:
        batches = conn.execute(
            "SELECT COUNT(*) AS cnt FROM fetch_batches"
        ).fetchone()["cnt"]

        items = conn.execute(
            "SELECT COUNT(*) AS cnt FROM hot_items"
        ).fetchone()["cnt"]

        platforms = conn.execute(
            "SELECT COUNT(DISTINCT platform) AS cnt FROM hot_items"
        ).fetchone()["cnt"]

        earliest = conn.execute(
            "SELECT MIN(started_at) AS val FROM fetch_batches"
        ).fetchone()["val"]

        latest = conn.execute(
            "SELECT MAX(started_at) AS val FROM fetch_batches"
        ).fetchone()["val"]

        # 各平台数据量
        platform_counts = conn.execute(
            """SELECT platform, COUNT(*) AS cnt
               FROM hot_items
               GROUP BY platform
               ORDER BY cnt DESC"""
        ).fetchall()

    return {
        "total_batches": batches,
        "total_items": items,
        "total_platforms": platforms,
        "earliest_batch": earliest,
        "latest_batch": latest,
        "platform_counts": [dict(r) for r in platform_counts],
    }


def cleanup_old(days: int = 30, db_path: str = None) -> int:
    """清理超过 N 天的旧数据

    Returns:
        删除的 item 数量
    """
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    with _get_conn(db_path) as conn:
        # 先删 items
        cur = conn.execute(
            "DELETE FROM hot_items WHERE fetched_at < ?", (cutoff,)
        )
        deleted = cur.rowcount

        # 再删空的 batches
        conn.execute(
            """DELETE FROM fetch_batches
               WHERE id NOT IN (SELECT DISTINCT batch_id FROM hot_items)"""
        )

        # 优化空间
        conn.execute("VACUUM")

    if deleted:
        logger.info(f"已清理 {deleted} 条超过 {days} 天的旧数据")
    return deleted
