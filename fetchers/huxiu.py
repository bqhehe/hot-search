"""虎嗅热文"""

from fetchers.base import BaseFetcher


class HuxiuFetcher(BaseFetcher):
    name = "huxiu"
    display_name = "虎嗅"

    def fetch(self) -> list:
        url = "https://www.huxiu.com/v2_action/article_list"
        params = {"platform": "www", "recommend": 1}
        headers = {
            **self.session.headers,
            "Referer": "https://www.huxiu.com/",
        }
        data = self._get(url, params=params, headers=headers, as_json=True)

        items = []
        if data and "data" in data:
            for entry in data["data"].get("datalist", [])[:20]:
                items.append({
                    "platform": self.display_name,
                    "title": entry.get("title", ""),
                    "url": f"https://www.huxiu.com/article/{entry.get('aid', '')}.html",
                    "hot": entry.get("count_info", {}).get("digg", ""),
                    "label": entry.get("topic", ""),
                    "rank": len(items) + 1,
                })
        return items
