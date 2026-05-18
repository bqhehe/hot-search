# 全网热点聚合工具

实时抓取各大平台的热门内容，生成美观的 HTML 热点聚合报告。

## 参考开源项目

本项目参考了以下优秀开源项目的实现思路：

| 项目 | Stars | 说明 |
|------|-------|------|
| [imsyy/DailyHotApi](https://github.com/imsyy/DailyHotApi) | 3.8k | 今日热榜 API，40+ 平台，支持自部署 |
| [baiwumm/next-daily-hot](https://github.com/baiwumm/next-daily-hot) | - | Next.js 热点聚合前端，30+ 平台 |
| [sansan0/TrendRadar](https://github.com/sansan0/TrendRadar) | - | AI 驱动的热点监控，35+ 平台，多渠道推送 |

## 支持平台（13 个本地 + 25 个 API）

### 本地自爬（默认模式）
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
| GitHub Trending | 开源 | 全球趋势项目 |
| 掘金 | 技术博客 | 推荐热文 |
| V2EX | 社区 | 热门话题 |

### API 模式（需自部署 DailyHotApi）
额外支持 12 个平台：快手、CSDN、豆瓣电影、网易新闻、腾讯新闻、新浪热点、澎湃新闻、百度贴吧、虎扑、酷安、AcFun、微信读书、HelloGitHub

## 安装

```bash
cd /Users/libuqiu/Documents/test-code
pip install -r requirements.txt
```

## 使用

```bash
# 默认模式：纯本地自爬
python main.py

# API 模式：需先部署 DailyHotApi
docker run -d --name dailyhot -p 6688:6688 imsyy/dailyhot-api
python main.py --api on

# 仅 API 模式（不自爬）
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

## 自部署 DailyHotApi（推荐）

```bash
# Docker 部署
docker run -d --name dailyhot -p 6688:6688 imsyy/dailyhot-api

# 或使用 Docker Compose
# docker-compose.yml 已包含在 DailyHotApi 项目中

# 设置环境变量
export DAILYHOT_API_URL=http://localhost:6688

# 然后运行
python main.py --api on
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
├── report.py              # HTML 报告生成器
├── cache.py               # 缓存模块（内存+文件）
├── requirements.txt       # Python 依赖
├── fetchers/
│   ├── base.py           # 爬取器基类
│   ├── dailyhot_api.py   # DailyHotApi 接口封装
│   ├── weibo.py          # 微博热搜
│   ├── zhihu.py          # 知乎热榜
│   ├── bilibili.py       # B站热门
│   ├── douyin.py         # 抖音热点
│   ├── toutiao.py        # 今日头条
│   ├── baidu.py          # 百度热搜
│   ├── kr36.py           # 36氪
│   ├── huxiu.py          # 虎嗅
│   ├── sspai.py          # 少数派
│   ├── ithome.py         # IT之家
│   ├── github.py         # GitHub Trending
│   ├── juejin.py         # 掘金
│   └── v2ex.py           # V2EX
├── output/                # 报告输出目录
└── .cache/                # API 缓存目录
```
