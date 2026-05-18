"""今日头条热点"""

from fetchers.base import BaseFetcher


class ToutiaoFetcher(BaseFetcher):
    name = "toutiao"
    display_name = "今日头条"

    def fetch(self) -> list:
        url = "https://www.toutiao.com/hot-event/hot-board/"
        params = {"origin": "hot_board"}
        data = self._get(url, params=params, as_json=True)
        if not data or "data" not in data:
            return []

        items = []
        for entry in data["data"][:20]:
            items.append({
                "platform": self.display_name,
                "title": entry.get("Title", ""),
                "url": entry.get("Url", ""),
                "hot": entry.get("HotValue", ""),
                "label": entry.get("Label", ""),
                "rank": len(items) + 1,
            })
        return items
