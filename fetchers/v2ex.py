"""V2EX 热门话题"""

from fetchers.base import BaseFetcher


class V2exFetcher(BaseFetcher):
    name = "v2ex"
    display_name = "V2EX"

    def fetch(self) -> list:
        url = "https://www.v2ex.com/api/topics/hot.json"
        data = self._get(url, as_json=True)
        if not data:
            return []

        items = []
        for entry in data[:20]:
            items.append({
                "platform": self.display_name,
                "title": entry.get("title", ""),
                "url": entry.get("url", ""),
                "hot": entry.get("replies", 0),
                "label": entry.get("node", {}).get("title", ""),
                "rank": len(items) + 1,
            })
        return items
