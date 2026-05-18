"""百度热搜"""

from fetchers.base import BaseFetcher


class BaiduFetcher(BaseFetcher):
    name = "baidu"
    display_name = "百度热搜"

    def fetch(self) -> list:
        url = "https://top.baidu.com/api/board"
        params = {"platform": "wise", "tab": "realtime"}
        data = self._get(url, params=params, as_json=True)
        if not data or "data" not in data:
            return []

        items = []
        cards = data["data"].get("cards", [])
        for card in cards:
            for entry in card.get("content", [])[:20]:
                items.append({
                    "platform": self.display_name,
                    "title": entry.get("query", "") or entry.get("word", ""),
                    "url": entry.get("url", ""),
                    "hot": entry.get("hotScore", "") or "",
                    "label": entry.get("label", ""),
                    "rank": len(items) + 1,
                })
                if len(items) >= 30:
                    break
            if len(items) >= 30:
                break
        return items
