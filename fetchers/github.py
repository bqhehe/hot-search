"""GitHub Trending - 支持日榜/周榜/月榜"""

from fetchers.base import BaseFetcher
from bs4 import BeautifulSoup


class GithubFetcher(BaseFetcher):
    name = "github"
    display_name = "GitHub日榜"
    description = "最近24小时最受关注的开源项目"
    since = "daily"  # daily / weekly / monthly

    def fetch(self) -> list:
        url = f"https://github.com/trending?since={self.since}"
        html = self._get(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        items = []
        for i, repo in enumerate(soup.select("article.Box-row"), 1):
            name_el = repo.select_one("h2 a")
            desc_el = repo.select_one("p")
            stars_el = repo.select_one(".d-inline-block.float-sm-right")

            name = name_el.get_text(strip=True).replace("\n", "").replace(" ", "") if name_el else ""
            if not name:
                continue

            # 提取语言
            lang_el = repo.select_one("[itemprop='programmingLanguage']")
            lang = lang_el.get_text(strip=True) if lang_el else ""

            # 提取今日/本周新增 star
            period_label = {"daily": "today", "weekly": "this week", "monthly": "this month"}.get(self.since, "today")
            today_stars = ""
            for span in repo.select("span.d-inline-block.float-sm-right span"):
                text = span.get_text(strip=True)
                if period_label in text.lower():
                    today_stars = text
                    break

            desc = desc_el.get_text(strip=True) if desc_el else ""
            label_parts = []
            if lang:
                label_parts.append(lang)
            if today_stars:
                label_parts.append(today_stars)

            items.append({
                "platform": self.display_name,
                "title": name,
                "url": f"https://github.com/{name}",
                "hot": stars_el.get_text(strip=True) if stars_el else "",
                "label": " | ".join(label_parts) if label_parts else "⭐",
                "rank": i,
                "content": desc,
            })
        return items


class GithubWeeklyFetcher(GithubFetcher):
    """GitHub Trending 周榜"""
    name = "github_weekly"
    display_name = "GitHub周榜"
    description = "最近7天最受关注的开源项目"
    since = "weekly"


class GithubMonthlyFetcher(GithubFetcher):
    """GitHub Trending 月榜"""
    name = "github_monthly"
    display_name = "GitHub月榜"
    description = "最近30天最受关注的开源项目"
    since = "monthly"
