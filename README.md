# 🔥 全网热点聚合工具

实时抓取各大平台的热门内容，生成美观的 HTML 热点聚合报告。

![效果预览](screenshots/preview.png)

## ✨ 特性

- 🌐 **25+ 平台**覆盖，本地自爬 + API 双模式
- 🎨 **深色主题**响应式 HTML 报告，直接浏览器打开
- ⚡ **并发抓取**，支持自定义并发数
- 💾 **两级缓存**（内存 + 文件），减少重复请求
- 📊 **SQLite 数据持久化**，历史数据可回溯
- 🆓 **orz.ai 公开 API**，免费无需部署即可获取 22 个平台数据
- 🐳 **Docker 部署** DailyHotApi，一键扩展至 40+ 平台
- 🖥️ **Tauri 桌面端**（开发中）

## 支持平台

### 本地自爬（13 个）

| 平台 | 类型 | 说明 |
|------|------|------|
| 微博热搜 | 社交 | 实时热搜榜 |
| 知乎热榜 | 问答 | 全站热榜 |
| B站热门 | 视频 | 全站排行榜 |
| 抖音热点 | 短视频 | 热点榜单 |
| 今日头条 | 新闻 | 热榜 |
| 百度热搜 | 搜索 | 实时热点 |
| 36氪 | 科技媒体 | 热门文章 |
| 虎嗅 | 商业媒体 | 热文 |
| 少数派 | 数码生活 | 周热榜 |
| IT之家 | 科技资讯 | 热门资讯 |
| GitHub Trending | 开源 | 全球趋势项目（日/周/月） |
| 掘金 | 技术博客 | 推荐热文 |
| V2EX | 社区 | 热门话题 |

### orz.ai 公开 API（22 个，免费免部署）

微博、知乎、豆瓣、贴吧、虎扑、B站、抖音、今日头条、百度、腾讯新闻、36氪、少数派、IT之家、快手、CSDN、网易新闻、澎湃新闻、酷安、AcFun、HelloGitHub 等

### DailyHotApi 自部署（40+ 平台）

额外支持：微信读书、新浪热点等。需 Docker 部署。

## 安装

```bash
git clone https://github.com/bqhehe/hot-search.git
cd hot-search
pip install -r requirements.txt
```

## 使用

```bash
# 默认模式：orz.ai API 优先 + 自爬 fallback（推荐）
python main.py

# 纯本地自爬（不调用任何 API）
python main.py --api off

# 仅 API（不自爬）
python main.py --api only

# 指定平台
python main.py -p bilibili douyin toutiao

# 指定输出目录
python main.py -o ~/Desktop/hot

# 调整并发数
python main.py -w 10

# 清除缓存
python main.py --clear-cache
```

### 自部署 DailyHotApi（扩展更多平台）

```bash
# Docker 部署
docker run -d --name dailyhot -p 6688:6688 imsyy/dailyhot-api

# 设置环境变量切换数据源
export DAILYHOT_API_URL=http://localhost:6688

# 然后运行
python main.py --api only
```

## 输出

运行后在 `output/` 目录生成：
- `latest.html` - 最新报告（覆盖）
- `hot_YYYYMMDD_HHMMSS.html` - 带时间戳的报告
- `hot_YYYYMMDD_HHMMSS.json` - JSON 数据备份

报告为深色主题的响应式页面，直接浏览器打开即可。

## 项目结构

```
├── main.py                # 主入口
├── report.py              # HTML 报告生成器（Jinja2 模板）
├── cache.py               # 两级缓存（内存 + 文件）
├── db.py                  # SQLite 数据持久化
├── requirements.txt       # Python 依赖
├── fetchers/
│   ├── base.py            # 爬取器基类
│   ├── dailyhot_api.py    # orz.ai + DailyHotApi 聚合接口
│   ├── weibo.py           # 微博热搜
│   ├── zhihu.py           # 知乎热榜
│   ├── bilibili.py        # B站热门
│   ├── douyin.py          # 抖音热点
│   ├── toutiao.py         # 今日头条
│   ├── baidu.py           # 百度热搜
│   ├── kr36.py            # 36氪
│   ├── huxiu.py           # 虎嗅
│   ├── sspai.py           # 少数派
│   ├── ithome.py          # IT之家
│   ├── github.py          # GitHub Trending
│   ├── juejin.py          # 掘金
│   └── v2ex.py            # V2EX
├── utils/                 # 工具函数
├── desktop/               # Tauri v2 桌面端（开发中）
│   └── hot-search-app/
├── screenshots/           # 效果截图
├── output/                # 报告输出目录（gitignore）
└── .cache/                # API 缓存目录（gitignore）
```

## 参考开源项目

| 项目 | 说明 |
|------|------|
| [imsyy/DailyHotApi](https://github.com/imsyy/DailyHotApi) | 今日热榜 API，40+ 平台，支持自部署 |
| [orz.ai](https://orz.ai) | 公开热点 API，免费免部署 |

## License

[MIT License](LICENSE)
