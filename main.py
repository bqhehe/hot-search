"""全网热点聚合 - 主入口（支持 orz.ai API + DailyHotApi + 自爬 fallback）"""

import os
import sys
import json
import logging
import argparse
import glob
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 将项目根目录加入 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetchers.weibo import WeiboFetcher
from fetchers.zhihu import ZhihuFetcher
from fetchers.bilibili import BilibiliFetcher
from fetchers.douyin import DouyinFetcher
from fetchers.toutiao import ToutiaoFetcher
from fetchers.baidu import BaiduFetcher
from fetchers.kr36 import Kr36Fetcher
from fetchers.huxiu import HuxiuFetcher
from fetchers.sspai import SspaiFetcher
from fetchers.ithome import IthomeFetcher
from fetchers.github import GithubFetcher, GithubWeeklyFetcher, GithubMonthlyFetcher
from fetchers.juejin import JuejinFetcher
from fetchers.v2ex import V2exFetcher
from fetchers.dailyhot_api import (
    fetch_from_api,
    fetch_all_from_api,
    PLATFORM_CONFIG,
    clear_cache as clear_api_cache,
    get_fallback_fetcher_name,
    get_platform_display_name,
)
from report import generate_report
from db import save_batch, cleanup_old as db_cleanup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")

# 所有本地爬取器
ALL_FETCHERS = [
    WeiboFetcher,
    ZhihuFetcher,
    BilibiliFetcher,
    DouyinFetcher,
    ToutiaoFetcher,
    BaiduFetcher,
    Kr36Fetcher,
    HuxiuFetcher,
    SspaiFetcher,
    IthomeFetcher,
    GithubFetcher,
    GithubWeeklyFetcher,
    GithubMonthlyFetcher,
    JuejinFetcher,
    V2exFetcher,
]

# 本地 fetcher name -> class 映射
FETCHER_MAP: dict[str, type] = {fc.name: fc for fc in ALL_FETCHERS}


def _sanitize(items):
    """确保所有 item 字段类型正确"""
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue
        hot = item.get("hot", "")
        if hot is None or (isinstance(hot, (int, float)) and hot == 0):
            hot = ""
        else:
            hot = str(hot)
        result.append({
            "platform": str(item.get("platform", "")),
            "title": str(item.get("title", "")),
            "url": str(item.get("url", "")),
            "hot": hot,
            "label": str(item.get("label", "") or ""),
            "rank": int(item.get("rank", 0)),
            "content": str(item.get("content", "") or ""),
        })
    return result


def fetch_one_local(fetcher_cls):
    """抓取单个平台（自爬）"""
    fetcher = fetcher_cls()
    try:
        items = fetcher.fetch()
        items = _sanitize(items)
        logger.info(f"✅ {fetcher.display_name}: 自爬获取 {len(items)} 条")
        return fetcher.display_name, items
    except Exception as e:
        logger.error(f"❌ {fetcher.display_name}: 自爬失败 - {e}")
        return fetcher.display_name, []


def run(
    output_dir: str = None,
    platforms: list = None,
    workers: int = 6,
    use_api: bool = True,
    api_only: bool = False,
):
    """运行热点聚合

    Args:
        output_dir: 输出目录
        platforms: 指定平台列表
        workers: 并发线程数
        use_api: 是否优先使用 DailyHotApi
        api_only: 是否只使用 API（不 fallback 到自爬）
    """
    logger.info("=" * 50)
    logger.info("🚀 全网热点聚合启动")
    mode = "API优先+自爬Fallback" if (use_api and not api_only) else ("仅API" if api_only else "纯自爬")
    logger.info(f"📡 数据模式: {mode}")
    logger.info("=" * 50)

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "output")

    # 确定要抓取的平台
    api_platforms = platforms if platforms else list(PLATFORM_CONFIG.keys())

    all_data: dict[str, list] = {}
    success = 0
    fail = 0
    # 数据源追踪
    source_stats = {
        "orz.ai": 0,
        "DailyHotApi": 0,
        "自爬": 0,
        "_per_platform": {},  # 平台名 -> 来源标签
    }

    if use_api:
        # ---- 阶段1: 从 API 获取数据（优先 orz.ai，备选 DailyHotApi） ----
        logger.info("📡 阶段1: 从 API 获取数据（orz.ai 优先）...")
        api_results = fetch_all_from_api(api_platforms)
        for name, items in api_results.items():
            all_data[name] = _sanitize(items)
            if items:
                success += 1
                # 追踪数据源：API 结果的 items 中 platform 字段即 display_name
                # 默认标记为 orz.ai（主数据源）
                src = items[0].get("_source", "orz.ai") if items else "orz.ai"
                source_stats[src] = source_stats.get(src, 0) + 1
                source_stats["_per_platform"][name] = src
            else:
                fail += 1

        if not api_only:
            # ---- 阶段2: fallback 自爬 - 对 API 失败的平台 ----
            failed_keys = []
            for key in api_platforms:
                config = PLATFORM_CONFIG.get(key)
                if not config:
                    continue
                display = config["display_name"]
                if display not in all_data or not all_data[display]:
                    fb_name = config.get("fallback")
                    if fb_name and fb_name in FETCHER_MAP:
                        failed_keys.append((key, fb_name))

            if failed_keys:
                logger.info(f"🔄 阶段2: Fallback 自爬 {len(failed_keys)} 个平台...")
                with ThreadPoolExecutor(max_workers=workers) as pool:
                    futures = {}
                    for _key, fb_name in failed_keys:
                        fc = FETCHER_MAP[fb_name]
                        futures[pool.submit(fetch_one_local, fc)] = _key
                    for future in as_completed(futures):
                        name, items = future.result()
                        if items:
                            all_data[name] = items
                            success += 1
                            fail = max(0, fail - 1)
                            source_stats["自爬"] += 1
                            source_stats["_per_platform"][name] = "自爬"

        # 同时也把没有在 API 结果中的本地 fetcher 跑一下（如 v2ex）
        if not api_only:
            local_only = []
            covered_names = set()
            for config in PLATFORM_CONFIG.values():
                fb = config.get("fallback")
                if fb:
                    covered_names.add(fb)
            for fc in ALL_FETCHERS:
                if fc.name not in covered_names:
                    # 像 v2ex 这种没有对应 API 的
                    if platforms is None or fc.name in platforms:
                        local_only.append(fc)

            if local_only:
                logger.info(f"🔧 阶段3: 爬取本地独有平台 {len(local_only)} 个...")
                with ThreadPoolExecutor(max_workers=workers) as pool:
                    futures = {pool.submit(fetch_one_local, fc): fc for fc in local_only}
                    for future in as_completed(futures):
                        name, items = future.result()
                        if items:
                            all_data[name] = items
                            success += 1
                            source_stats["自爬"] += 1
                            source_stats["_per_platform"][name] = "自爬"
                        else:
                            fail += 1

    else:
        # ---- 纯自爬模式 ----
        logger.info("🕷️ 纯自爬模式")
        fetchers = ALL_FETCHERS
        if platforms:
            # 尝试把 api 风格的 name 映射到本地 fetcher
            mapped = set()
            for p in platforms:
                fb = None
                for config in PLATFORM_CONFIG.values():
                    if config["api_name"] == p or config["display_name"] == p:
                        fb = config.get("fallback")
                        break
                if fb and fb in FETCHER_MAP:
                    mapped.add(fb)
                elif p in FETCHER_MAP:
                    mapped.add(p)
            fetchers = [FETCHER_MAP[n] for n in mapped if n in FETCHER_MAP]
            if not fetchers:
                fetchers = [f for f in ALL_FETCHERS if f.name in platforms]
            if not fetchers:
                logger.error(f"未找到匹配的平台: {platforms}")
                return

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(fetch_one_local, fc): fc for fc in fetchers}
            for future in as_completed(futures):
                name, items = future.result()
                all_data[name] = items
                if items:
                    success += 1
                else:
                    fail += 1

    logger.info("-" * 50)
    logger.info(f"📊 抓取完成: {success} 成功, {fail} 失败, 共 {len(all_data)} 个平台")

    if not all_data:
        logger.error("未获取到任何数据，退出")
        return

    # 保存到 SQLite 数据库
    try:
        batch_id = save_batch(all_data, mode=mode, source_stats=source_stats)
        logger.info(f"💾 数据已持久化: 批次 {batch_id}")
    except Exception as e:
        logger.warning(f"⚠️ 数据库保存失败（不影响报告生成）: {e}")

    # 清理数据库中超过 30 天的旧数据
    try:
        db_cleanup(days=30)
    except Exception:
        pass

    # 生成报告
    filepath = generate_report(all_data, output_dir, source_stats=source_stats)
    logger.info(f"📄 报告已生成: {filepath}")

    # 保存 JSON 备份
    json_path = filepath.replace(".html", ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    # 清理超过 7 天的旧报告文件
    _cleanup_old_reports(output_dir, keep_days=7)

    return filepath


def _cleanup_old_reports(output_dir: str, keep_days: int = 7):
    """清理超过 keep_days 天的旧报告文件"""
    cutoff = time.time() - keep_days * 86400
    removed = 0
    for fpath in glob.glob(os.path.join(output_dir, "hot_*")):
        if os.path.getmtime(fpath) < cutoff:
            try:
                os.remove(fpath)
                removed += 1
            except OSError:
                pass
    if removed:
        logger.info(f"🧹 已清理 {removed} 个超过 {keep_days} 天的旧报告")


def main():
    parser = argparse.ArgumentParser(description="全网热点聚合工具")
    parser.add_argument("-o", "--output", default=None, help="输出目录")
    parser.add_argument("-p", "--platforms", nargs="+", default=None,
                        help="指定平台，如: weibo zhihu bilibili")
    parser.add_argument("-w", "--workers", type=int, default=6, help="并发数")
    parser.add_argument("--api", choices=["on", "off", "only"], default="on",
                        help="API 模式: on=API优先+fallback自爬(默认), "
                             "off=纯自爬, only=仅API不fallback")
    parser.add_argument("--clear-cache", action="store_true",
                        help="清空 DailyHotApi 缓存后运行")
    args = parser.parse_args()

    if args.clear_cache:
        clear_api_cache()
        logger.info("已清空 API 缓存")

    use_api = args.api in ("on", "only")
    api_only = args.api == "only"

    run(
        output_dir=args.output,
        platforms=args.platforms,
        workers=args.workers,
        use_api=use_api,
        api_only=api_only,
    )


if __name__ == "__main__":
    main()
