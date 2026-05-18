"""抖音热点"""

from fetchers.base import BaseFetcher


class DouyinFetcher(BaseFetcher):
    name = "douyin"
    display_name = "抖音热点"

    def fetch(self) -> list:
        url = "https://www.douyin.com/aweme/v1/web/hot/search/list/"
        params = {"device_platform": "webapp", "aid": "6383"}
        headers = {
            **self.session.headers,
            "Referer": "https://www.douyin.com/hot",
            "Cookie": "ttwid=1",
        }
        data = self._get(url, params=params, headers=headers, as_json=True)
        if not data:
            return []

        word_list = []
        try:
            word_list = data.get("data", {}).get("word_list", [])
        except Exception:
            pass

        items = []
        for entry in word_list[:20]:
            items.append({
                "platform": self.display_name,
                "title": entry.get("word", ""),
                "url": f"https://www.douyin.com/hot/{entry.get('sentence_id', '')}",
                "hot": entry.get("hot_value", 0),
                "label": entry.get("label", ""),
                "rank": len(items) + 1,
            })
        return items
