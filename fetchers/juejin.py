"""稀土掘金热榜"""

from fetchers.base import BaseFetcher


class JuejinFetcher(BaseFetcher):
    name = "juejin"
    display_name = "掘金"

    def fetch(self) -> list:
        url = "https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed"
        payload = {"id_type": 2, "sort_type": 200, "cursor": "0", "limit": 20}
        data = self._get_json_post(url, payload)
        if not data:
            return []

        items = []
        for entry in data.get("data", [])[:20]:
            article = entry.get("article_info", {})
            items.append({
                "platform": self.display_name,
                "title": article.get("title", ""),
                "url": f"https://juejin.cn/post/{article.get('article_id', '')}",
                "hot": article.get("view_count", ""),
                "label": entry.get("category", {}).get("category_name", ""),
                "rank": len(items) + 1,
            })
        return items

    def _get_json_post(self, url, payload):
        import json
        try:
            resp = self.session.post(url, json=payload, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None
