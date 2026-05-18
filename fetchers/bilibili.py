"""B站热门视频"""

from fetchers.base import BaseFetcher


class BilibiliFetcher(BaseFetcher):
    name = "bilibili"
    display_name = "B站热门"

    def fetch(self) -> list:
        url = "https://api.bilibili.com/x/web-interface/ranking/v2"
        params = {"rid": 0, "type": "all"}
        data = self._get(url, params=params, as_json=True)
        if not data or "data" not in data:
            return []

        items = []
        for video in data["data"].get("list", [])[:30]:
            owner = video.get("owner", {})
            stat = video.get("stat", {})
            items.append({
                "platform": self.display_name,
                "title": video.get("title", ""),
                "url": video.get("short_link_v2", f"https://www.bilibili.com/video/{video.get('bvid', '')}"),
                "hot": stat.get("view", 0),
                "label": f"👆{self._fmt(stat.get('view', 0))} 💬{self._fmt(stat.get('danmaku', 0))}",
                "rank": len(items) + 1,
                "author": owner.get("name", ""),
                "cover": video.get("pic", ""),
            })
        return items

    @staticmethod
    def _fmt(num) -> str:
        if isinstance(num, str):
            return num
        if num >= 10000_0000:
            return f"{num/10000_0000:.1f}亿"
        if num >= 10000:
            return f"{num/10000:.1f}万"
        return str(num)
