"""知乎热榜"""

from fetchers.base import BaseFetcher


class ZhihuFetcher(BaseFetcher):
    name = "zhihu"
    display_name = "知乎热榜"

    def fetch(self) -> list:
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
        params = {"limit": 30, "desktop": "true"}
        headers = {
            **self.session.headers,
            "Referer": "https://www.zhihu.com/hot",
        }
        data = self._get(url, params=params, headers=headers, as_json=True)
        if not data or "data" not in data:
            # 降级：尝试页面解析
            return self._fetch_from_page()

        items = []
        for entry in data["data"][:30]:
            target = entry.get("target", {})
            items.append({
                "platform": self.display_name,
                "title": target.get("title", ""),
                "url": f"https://www.zhihu.com/question/{target.get('id', '')}",
                "hot": entry.get("detail_text", "").replace("万热度", "").strip(),
                "label": "热" if entry.get("type") else "",
                "rank": len(items) + 1,
            })
        return items

    def _fetch_from_page(self) -> list:
        """API 不可用时从页面抓取"""
        url = "https://www.zhihu.com/hot"
        html = self._get(url)
        if not html:
            return []
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        items = []
        for i, sec in enumerate(soup.select("section.HotItem"), 1):
            title_el = sec.select_one(".HotItem-title")
            link_el = sec.select_one(".HotItem-content a")
            if title_el:
                items.append({
                    "platform": self.display_name,
                    "title": title_el.get_text(strip=True),
                    "url": link_el["href"] if link_el and link_el.get("href") else "",
                    "hot": "",
                    "label": "",
                    "rank": i,
                })
        return items
