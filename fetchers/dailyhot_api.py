"""热点 API 聚合接口 - 支持 orz.ai 公开 API + DailyHotApi 自部署"""

import logging
import os
import requests
from typing import Optional
from cache import Cache

logger = logging.getLogger(__name__)

# ===== API 配置 =====
# orz.ai 公开 API（默认，22 个平台，免费无需部署）
ORZ_API_BASE = "https://orz.ai/api/v1/dailynews"

# DailyHotApi 自部署（备用，40+ 平台，需 Docker 部署）
DAILYHOT_API_BASE = os.environ.get("DAILYHOT_API_URL", "http://localhost:6688")

# 默认使用 orz.ai
API_BASE = os.environ.get("HOT_API_BASE", "orz")

# 平台配置：key 为内部标识
# source: "orz" | "dailyhot" | "both"
PLATFORM_CONFIG: dict[str, dict] = {
    # ===== 社交媒体 =====
    "weibo": {
        "orz_name": "weibo",
        "dailyhot_name": "weibo",
        "display_name": "微博热搜",
        "icon": "🔥",
        "fallback": "weibo",
        "source": "both",
    },
    "zhihu": {
        "orz_name": "zhihu",
        "dailyhot_name": "zhihu",
        "display_name": "知乎热榜",
        "icon": "💡",
        "fallback": "zhihu",
        "source": "both",
    },
    "douban": {
        "orz_name": "douban",
        "dailyhot_name": "douban",
        "display_name": "豆瓣",
        "icon": "🎬",
        "fallback": None,
        "source": "both",
    },
    "tieba": {
        "orz_name": "tieba",
        "dailyhot_name": "tieba",
        "display_name": "百度贴吧",
        "icon": "💭",
        "fallback": None,
        "source": "both",
    },
    "hupu": {
        "orz_name": "hupu",
        "dailyhot_name": "hupu",
        "display_name": "虎扑",
        "icon": "🏀",
        "fallback": None,
        "source": "both",
    },

    # ===== 视频娱乐 =====
    "bilibili": {
        "orz_name": "bilibili",
        "dailyhot_name": "bilibili",
        "display_name": "B站热门",
        "icon": "📺",
        "fallback": "bilibili",
        "source": "both",
    },
    "douyin": {
        "orz_name": "douyin",
        "dailyhot_name": "douyin",
        "display_name": "抖音热点",
        "icon": "🎵",
        "fallback": "douyin",
        "source": "both",
    },

    # ===== 新闻资讯 =====
    "toutiao": {
        "orz_name": "jinritoutiao",
        "dailyhot_name": "toutiao",
        "display_name": "今日头条",
        "icon": "📰",
        "fallback": "toutiao",
        "source": "both",
    },
    "baidu": {
        "orz_name": "baidu",
        "dailyhot_name": "baidu",
        "display_name": "百度热搜",
        "icon": "🔍",
        "fallback": "baidu",
        "source": "both",
    },
    "tencent_news": {
        "orz_name": "tenxunwang",
        "dailyhot_name": "qqNews",
        "display_name": "腾讯新闻",
        "icon": "📡",
        "fallback": None,
        "source": "both",
    },

    # ===== 科技媒体 =====
    "36kr": {
        "orz_name": "36kr",
        "dailyhot_name": "36kr",
        "display_name": "36氪",
        "icon": "🚀",
        "fallback": "kr36",
        "source": "both",
    },
    "sspai": {
        "orz_name": "shaoshupai",
        "dailyhot_name": "sspai",
        "display_name": "少数派",
        "icon": "🎯",
        "fallback": "sspai",
        "source": "both",
    },
    "ithome": {
        "orz_name": None,
        "dailyhot_name": "ithome",
        "display_name": "IT之家",
        "icon": "💻",
        "fallback": "ithome",
        "source": "dailyhot",
    },
    "huxiu": {
        "orz_name": None,
        "dailyhot_name": "huxiu",
        "display_name": "虎嗅",
        "icon": "🐅",
        "fallback": "huxiu",
        "source": "dailyhot",
    },

    # ===== 技术社区 =====
    "juejin": {
        "orz_name": "juejin",
        "dailyhot_name": "juejin",
        "display_name": "掘金",
        "icon": "⛏️",
        "fallback": "juejin",
        "source": "both",
    },
    "github": {
        "orz_name": "github",
        "dailyhot_name": "github",
        "display_name": "GitHub日榜",
        "icon": "🐙",
        "description": "最近24小时最受关注的开源项目",
        "fallback": "github",
        "source": "both",
    },
    "github_weekly": {
        "orz_name": None,
        "dailyhot_name": None,
        "display_name": "GitHub周榜",
        "icon": "📅",
        "description": "最近7天最受关注的开源项目",
        "fallback": "github_weekly",
        "source": "crawl",
    },
    "github_monthly": {
        "orz_name": None,
        "dailyhot_name": None,
        "display_name": "GitHub月榜",
        "icon": "📆",
        "description": "最近30天最受关注的开源项目",
        "fallback": "github_monthly",
        "source": "crawl",
    },
    "v2ex": {
        "orz_name": "v2ex",
        "dailyhot_name": None,
        "display_name": "V2EX",
        "icon": "💬",
        "fallback": "v2ex",
        "source": "orz",
    },
    "stackoverflow": {
        "orz_name": "stackoverflow",
        "dailyhot_name": None,
        "display_name": "Stack Overflow",
        "icon": "🧑‍💻",
        "fallback": None,
        "source": "orz",
    },
    "hackernews": {
        "orz_name": "hackernews",
        "dailyhot_name": None,
        "display_name": "Hacker News",
        "icon": "🟠",
        "fallback": None,
        "source": "orz",
    },

    # ===== 财经 =====
    "sina_finance": {
        "orz_name": "sina_finance",
        "dailyhot_name": None,
        "display_name": "新浪财经",
        "icon": "💹",
        "fallback": None,
        "source": "orz",
    },
    "eastmoney": {
        "orz_name": "eastmoney",
        "dailyhot_name": None,
        "display_name": "东方财富",
        "icon": "💰",
        "fallback": None,
        "source": "orz",
    },
    "xueqiu": {
        "orz_name": "xueqiu",
        "dailyhot_name": None,
        "display_name": "雪球",
        "icon": "📈",
        "fallback": None,
        "source": "orz",
    },
    "cls": {
        "orz_name": "cls",
        "dailyhot_name": None,
        "display_name": "财联社",
        "icon": "📊",
        "fallback": None,
        "source": "orz",
    },

    # ===== 仅 DailyHotApi =====
    "kuaishou": {
        "orz_name": None,
        "dailyhot_name": "kuaishou",
        "display_name": "快手热榜",
        "icon": "🎬",
        "fallback": None,
        "source": "dailyhot",
    },
    "csdn": {
        "orz_name": None,
        "dailyhot_name": "csdn",
        "display_name": "CSDN",
        "icon": "🎓",
        "fallback": None,
        "source": "dailyhot",
    },
    "netease_news": {
        "orz_name": None,
        "dailyhot_name": "neteaseNews",
        "display_name": "网易新闻",
        "icon": "📣",
        "fallback": None,
        "source": "dailyhot",
    },
    "sina": {
        "orz_name": None,
        "dailyhot_name": "sina",
        "display_name": "新浪热点",
        "icon": "🌐",
        "fallback": None,
        "source": "dailyhot",
    },
    "thepaper": {
        "orz_name": None,
        "dailyhot_name": "thepaper",
        "display_name": "澎湃新闻",
        "icon": "🌊",
        "fallback": None,
        "source": "dailyhot",
    },
    "coolapk": {
        "orz_name": None,
        "dailyhot_name": "coolapk",
        "display_name": "酷安",
        "icon": "📱",
        "fallback": None,
        "source": "dailyhot",
    },
    "acfun": {
        "orz_name": None,
        "dailyhot_name": "acfun",
        "display_name": "AcFun",
        "icon": "猿",
        "fallback": None,
        "source": "dailyhot",
    },
    "weread": {
        "orz_name": None,
        "dailyhot_name": "weread",
        "display_name": "微信读书",
        "icon": "📚",
        "fallback": None,
        "source": "dailyhot",
    },
    "hellogithub": {
        "orz_name": None,
        "dailyhot_name": "hellogithub",
        "display_name": "HelloGitHub",
        "icon": "🌟",
        "fallback": None,
        "source": "dailyhot",
    },
    "52pojie": {
        "orz_name": "52pojie",
        "dailyhot_name": None,
        "display_name": "吾爱破解",
        "icon": "🔓",
        "fallback": None,
        "source": "orz",
    },
}

# 全局缓存实例（30 分钟 TTL，匹配 orz.ai 数据刷新频率）
_cache = Cache(
    ttl=1800,
    cache_dir=".cache/hot_api",
)

# 请求会话
_session = requests.Session()
_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
})


def _parse_orz_response(data: dict, platform_key: str) -> list[dict]:
    """解析 orz.ai API 响应

    响应格式:
    {
      "status": "success",
      "data": [{"title": "...", "url": "...", "content": "...", "source": "...", "publish_time": "..."}],
      "msg": ""
    }
    """
    config = PLATFORM_CONFIG[platform_key]
    display_name = config["display_name"]

    items_raw = data.get("data", [])
    if not isinstance(items_raw, list):
        if isinstance(data, list):
            items_raw = data
        else:
            logger.warning(f"[{display_name}] orz API 返回格式异常: {type(data)}")
            return []

    items = []
    for idx, entry in enumerate(items_raw[:30], 1):
        if not isinstance(entry, dict):
            continue

        # orz.ai 没有 hot 值，用排名序号代替
        content = str(entry.get("content", "") or "").strip()
        if content and len(content) > 200:
            content = content[:200] + "..."
        items.append({
            "platform": display_name,
            "title": str(entry.get("title", "") or ""),
            "url": str(entry.get("url", "") or ""),
            "hot": "",
            "label": str(entry.get("source", "") or ""),
            "rank": idx,
            "content": content,
        })

    return items


def _parse_dailyhot_response(data: dict, platform_key: str) -> list[dict]:
    """解析 DailyHotApi 响应

    响应格式:
    {
      "success": true,
      "data": [{"title": "...", "url": "...", "hot": 12345, ...}]
    }
    """
    config = PLATFORM_CONFIG[platform_key]
    display_name = config["display_name"]

    items_raw = data.get("data", [])
    if not isinstance(items_raw, list):
        if isinstance(data, list):
            items_raw = data
        else:
            logger.warning(f"[{display_name}] DailyHotApi 返回格式异常: {type(data)}")
            return []

    items = []
    for idx, entry in enumerate(items_raw[:25], 1):
        if not isinstance(entry, dict):
            continue

        hot = entry.get("hot") or entry.get("hotNum") or entry.get("heat") or entry.get("score") or ""
        label = ""
        for label_key in ("label", "tag", "category", "desc"):
            v = entry.get(label_key)
            if v and isinstance(v, str) and len(v) < 20:
                label = v
                break

        items.append({
            "platform": display_name,
            "title": str(entry.get("title", "") or entry.get("name", "")),
            "url": str(entry.get("url", "") or entry.get("link", "")),
            "hot": str(hot) if hot else "",
            "label": label,
            "rank": idx,
        })

    return items


def fetch_from_api(platform_key: str, timeout: int = 15) -> list[dict]:
    """从 API 获取单个平台数据（优先 orz.ai，备选 DailyHotApi）

    Args:
        platform_key: PLATFORM_CONFIG 中的键名
        timeout: 请求超时秒数

    Returns:
        标准化的热点列表
    """
    config = PLATFORM_CONFIG.get(platform_key)
    if not config:
        logger.error(f"未知平台: {platform_key}")
        return []

    display_name = config["display_name"]
    cache_key = f"api:{platform_key}"

    # 检查缓存
    cached = _cache.get(cache_key)
    if cached is not None:
        logger.info(f"📦 {display_name}: 缓存命中 ({len(cached)} 条)")
        return cached

    items = []

    # 1) 尝试 orz.ai
    orz_name = config.get("orz_name")
    if orz_name:
        try:
            url = f"{ORZ_API_BASE}?platform={orz_name}"
            resp = _session.get(url, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()

            if isinstance(data, dict) and data.get("status") in ("success", "200"):
                items = _parse_orz_response(data, platform_key)
                if items:
                    _cache.set(cache_key, items)
                    logger.info(f"✅ {display_name}: orz.ai 获取 {len(items)} 条")
                    return items
                else:
                    # data 为空列表是正常的（该平台暂无数据）
                    logger.debug(f"📭 {display_name}: orz.ai 返回空数据")
            elif isinstance(data, dict) and data.get("status") in ("404", "error"):
                # 平台参数错误
                logger.warning(f"⚠️ {display_name}: orz.ai 平台参数无效 - {data.get('msg', '')[:80]}")
        except requests.exceptions.Timeout:
            logger.warning(f"⏰ {display_name}: orz.ai 超时")
        except requests.exceptions.ConnectionError:
            logger.warning(f"🔌 {display_name}: orz.ai 连接失败")
        except Exception as e:
            logger.warning(f"❌ {display_name}: orz.ai 异常 - {e}")

    # 2) fallback 到 DailyHotApi 自部署
    dailyhot_name = config.get("dailyhot_name")
    if not items and dailyhot_name:
        try:
            url = f"{DAILYHOT_API_BASE}/{dailyhot_name}"
            resp = _session.get(url, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()

            if isinstance(data, dict):
                success = data.get("success", True)
                if success is False:
                    logger.warning(f"⚠️ {display_name}: DailyHotApi 返回失败")
                else:
                    items = _parse_dailyhot_response(data, platform_key)
                    if items:
                        _cache.set(cache_key, items)
                        logger.info(f"✅ {display_name}: DailyHotApi 获取 {len(items)} 条")
                        return items
                    else:
                        logger.warning(f"⚠️ {display_name}: DailyHotApi 返回空数据")
        except requests.exceptions.ConnectionError:
            logger.debug(f"🔌 {display_name}: DailyHotApi 不可用（未部署？）")
        except Exception as e:
            logger.debug(f"⚠️ {display_name}: DailyHotApi 异常 - {e}")

    if not items:
        logger.info(f"📭 {display_name}: 所有 API 均无数据")

    return items


def fetch_all_from_api(platforms: list[str] = None, timeout: int = 15) -> dict[str, list[dict]]:
    """从 API 获取多个平台的数据

    Args:
        platforms: 平台列表，None 表示全部
        timeout: 单个请求超时

    Returns:
        {display_name: [items]} 格式的字典
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    keys = platforms if platforms else list(PLATFORM_CONFIG.keys())
    results: dict[str, list[dict]] = {}

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(fetch_from_api, k, timeout): k for k in keys}
        for future in as_completed(futures):
            items = future.result()
            if items:
                display_name = items[0]["platform"]
                results[display_name] = items

    return results


def clear_cache() -> None:
    """清空 API 缓存"""
    _cache.clear()
    logger.info("已清空 API 缓存")


def get_platform_list() -> list[str]:
    """返回所有支持的平台标识列表"""
    return list(PLATFORM_CONFIG.keys())


def get_platform_display_name(key: str) -> str:
    """获取平台显示名"""
    config = PLATFORM_CONFIG.get(key, {})
    return config.get("display_name", key)


def get_fallback_fetcher_name(key: str) -> Optional[str]:
    """获取对应本地 fallback 的 fetcher name"""
    config = PLATFORM_CONFIG.get(key, {})
    return config.get("fallback")
