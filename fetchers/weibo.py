"""微博热搜榜"""

from fetchers.base import BaseFetcher


class WeiboFetcher(BaseFetcher):
    name = "weibo"
    display_name = "微博热搜"

    def fetch(self) -> list:
        # 微博热搜 AJAX 接口
        url = "https://weibo.com/ajax/side/hotSearch"
        data = self._get(url, as_json=True)
        if not data or "data" not in data:
            return []

        items = []
        for entry in data["data"].get("realtime", [])[:30]:
            label = ""
            if entry.get("label_name"):
                label = entry["label_name"]
            elif entry.get("is_hot") == 1:
                label = "热"
            elif entry.get("is_new") == 1:
                label = "新"

            items.append({
                "platform": self.display_name,
                "title": entry.get("note", ""),
                "url": f"https://s.weibo.com/weibo?q=%23{entry.get('word', '')}%23",
                "hot": entry.get("num", 0),
                "label": label,
                "rank": len(items) + 1,
            })
        return items
