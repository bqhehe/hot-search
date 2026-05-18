"""少数派热榜"""

from fetchers.base import BaseFetcher
from bs4 import BeautifulSoup


class SspaiFetcher(BaseFetcher):
    name = "sspai"
    display_name = "少数派"

    def fetch(self) -> list:
        url = "https://sspai.com/api/v1/article/rank/page/get"
        params = {"limit": 20, "offset": 0, "created_at": 7}
        data = self._get(url, params=params, as_json=True)

        items = []
        if data and isinstance(data, dict) and "data" in data:
            entries = data["data"]
            if isinstance(entries, list):
                for entry in entries[:20]:
                    if not isinstance(entry, dict):
                        continue
                    items.append({
                        "platform": self.display_name,
                        "title": entry.get("title", ""),
                        "url": f"https://sspai.com/post/{entry.get('id', '')}",
                        "hot": str(entry.get("like_count", "") or ""),
                        "label": "",
                        "rank": len(items) + 1,
                    })
        return items
