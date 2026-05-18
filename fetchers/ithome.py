"""IT之家热榜"""

from fetchers.base import BaseFetcher
from bs4 import BeautifulSoup
import re
import json


class IthomeFetcher(BaseFetcher):
    name = "ithome"
    display_name = "IT之家"

    def fetch(self) -> list:
        url = "https://m.ithome.com"
        html = self._get(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        items = []

        # 尝试从页面 JSON 数据中提取
        scripts = soup.find_all("script")
        for script in scripts:
            text = script.string or ""
            if "newsData" in text or "hotList" in text:
                try:
                    match = re.search(r'(\[.*?\])', text, re.DOTALL)
                    if match:
                        news_list = json.loads(match.group(1))
                        for entry in news_list[:20]:
                            items.append({
                                "platform": self.display_name,
                                "title": entry.get("title", ""),
                                "url": entry.get("url", ""),
                                "hot": "",
                                "label": entry.get("typename", ""),
                                "rank": len(items) + 1,
                            })
                except (json.JSONDecodeError, AttributeError):
                    pass

        if not items:
            for i, pic in enumerate(soup.select(".swiper-slide a, .news-list a"), 1):
                title = pic.get_text(strip=True)
                href = pic.get("href", "")
                if title:
                    items.append({
                        "platform": self.display_name,
                        "title": title,
                        "url": href,
                        "hot": "",
                        "label": "",
                        "rank": i,
                    })
                if i >= 20:
                    break
        return items
