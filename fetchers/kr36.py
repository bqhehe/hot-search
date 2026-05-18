"""36氪热榜"""

from fetchers.base import BaseFetcher
from bs4 import BeautifulSoup


class Kr36Fetcher(BaseFetcher):
    name = "36kr"
    display_name = "36氪"

    def fetch(self) -> list:
        url = "https://36kr.com/hot-list/catalog"
        data = self._get(url, as_json=True)
        if data and "data" in data:
            return self._parse_api(data)

        # 降级：页面抓取
        return self._fetch_from_page()

    def _parse_api(self, data) -> list:
        items = []
        for entry in data.get("data", {}).get("hotList", [])[:20]:
            item = entry.get("entity", {})
            items.append({
                "platform": self.display_name,
                "title": item.get("title", ""),
                "url": f"https://36kr.com/p/{item.get('id', '')}",
                "hot": item.get("stat", {}).get("pv", ""),
                "label": item.get("column", {}).get("name", ""),
                "rank": len(items) + 1,
            })
        return items

    def _fetch_from_page(self) -> list:
        url = "https://36kr.com/hot-list/catalog"
        html = self._get(url)
        if not html:
            return []
        soup = BeautifulSoup(html, "lxml")
        items = []
        for i, article in enumerate(soup.select(".article-item-title"), 1):
            items.append({
                "platform": self.display_name,
                "title": article.get_text(strip=True),
                "url": article.get("href", ""),
                "hot": "",
                "label": "",
                "rank": i,
            })
        return items
