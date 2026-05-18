"""HTML 报告生成器 - 现代深色主题，卡片式布局，支持搜索/分类过滤"""

import os
from datetime import datetime
from jinja2 import Template

TEMPLATE_STR = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全网热点聚合 - {{ date }}</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-card: #16161f;
    --bg-card-hover: #1c1c28;
    --border-color: #252535;
    --border-hover: #3a3a50;
    --text-primary: #e8e8f0;
    --text-secondary: #9090a8;
    --text-muted: #5a5a72;
    --accent: #6c5ce7;
    --accent-light: #a29bfe;
    --accent-glow: rgba(108, 92, 231, 0.3);
    --hot-1: #ff6b6b;
    --hot-2: #ffa502;
    --hot-3: #eccc68;
    --gradient-1: linear-gradient(135deg, #6c5ce7, #a29bfe);
    --gradient-2: linear-gradient(135deg, #fd79a8, #e84393);
    --gradient-3: linear-gradient(135deg, #00cec9, #0984e3);
    --radius: 16px;
    --radius-sm: 10px;
    --shadow: 0 4px 24px rgba(0,0,0,0.3);
    --shadow-hover: 0 8px 40px rgba(108,92,231,0.15);
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC",
                 "Noto Sans SC", "Microsoft YaHei", sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
}
/* Header */
.header {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    padding: 48px 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at center, var(--accent-glow) 0%, transparent 70%);
    opacity: 0.3;
    animation: pulse 8s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.2; }
    50% { transform: scale(1.1); opacity: 0.4; }
}
.header-content { position: relative; z-index: 1; }
.header h1 {
    font-size: 2.4em;
    font-weight: 800;
    background: var(--gradient-1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}
.header .date {
    color: var(--text-secondary);
    font-size: 1.05em;
    font-weight: 400;
}
.header .stats {
    margin-top: 16px;
    display: flex;
    justify-content: center;
    gap: 24px;
    flex-wrap: wrap;
}
.stat-item {
    display: flex;
    align-items: center;
    gap: 6px;
    color: var(--text-muted);
    font-size: 0.9em;
}
.stat-value {
    color: var(--accent-light);
    font-weight: 700;
    font-size: 1.1em;
}
/* Source badge */
.source-badge {
    display: inline-block;
    margin-top: 12px;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.75em;
    background: rgba(108,92,231,0.15);
    color: var(--accent-light);
    border: 1px solid rgba(108,92,231,0.25);
}
/* Search bar */
.search-bar {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    padding: 10px 24px;
    position: sticky;
    top: 0;
    z-index: 200;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
}
.search-inner {
    max-width: 1600px;
    margin: 0 auto;
    display: flex;
    gap: 12px;
    align-items: center;
}
.search-input {
    flex: 1;
    max-width: 400px;
    padding: 8px 16px;
    border-radius: 20px;
    border: 1px solid var(--border-color);
    background: var(--bg-card);
    color: var(--text-primary);
    font-size: 0.9em;
    outline: none;
    transition: border-color 0.2s;
}
.search-input:focus { border-color: var(--accent); }
.search-input::placeholder { color: var(--text-muted); }
.search-count {
    font-size: 0.8em;
    color: var(--text-muted);
    white-space: nowrap;
}
.search-count span { color: var(--accent-light); font-weight: 600; }
/* Category tabs */
.category-bar {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    padding: 8px 24px;
}
.category-inner {
    max-width: 1600px;
    margin: 0 auto;
    display: flex;
    gap: 8px;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
}
.category-inner::-webkit-scrollbar { display: none; }
.cat-chip {
    flex-shrink: 0;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.82em;
    background: var(--bg-card);
    color: var(--text-secondary);
    border: 1px solid var(--border-color);
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
    user-select: none;
}
.cat-chip:hover {
    background: var(--accent);
    color: #fff;
    border-color: var(--accent);
    transform: translateY(-1px);
}
.cat-chip.active {
    background: var(--accent);
    color: #fff;
    border-color: var(--accent);
}
/* Navigation */
.nav-bar {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    padding: 10px 24px;
}
.nav-inner {
    max-width: 1600px;
    margin: 0 auto;
    display: flex;
    gap: 8px;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
}
.nav-inner::-webkit-scrollbar { display: none; }
.nav-chip {
    flex-shrink: 0;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82em;
    background: var(--bg-card);
    color: var(--text-secondary);
    border: 1px solid var(--border-color);
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    white-space: nowrap;
}
.nav-chip:hover {
    background: var(--accent);
    color: #fff;
    border-color: var(--accent);
    transform: translateY(-1px);
}
/* Container */
.container {
    max-width: 1600px;
    margin: 0 auto;
    padding: 24px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
}
@media (max-width: 500px) {
    .container { grid-template-columns: 1fr; padding: 12px; gap: 12px; }
    .header h1 { font-size: 1.6em; }
    .header { padding: 32px 16px; }
    .nav-chip { font-size: 0.75em; padding: 5px 10px; }
    .cat-chip { font-size: 0.75em; padding: 5px 10px; }
    .search-inner { flex-wrap: wrap; }
    .search-input { max-width: 100%; }
}
/* Card */
.card {
    background: var(--bg-card);
    border-radius: var(--radius);
    overflow: hidden;
    border: 1px solid var(--border-color);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: var(--shadow);
}
.card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--shadow-hover);
    transform: translateY(-3px);
}
.card.hidden { display: none; }
.card-header {
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    background: var(--bg-secondary);
}
.card-header .platform-info {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}
.platform-desc {
    font-size: 12px;
    color: var(--text-muted);
    opacity: 0.7;
    font-weight: 400;
}
.card-header .platform-icon {
    font-size: 1.4em;
}
.card-header h2 {
    font-size: 1.05em;
    font-weight: 600;
    color: var(--text-primary);
}
.card-header .right-badges {
    display: flex;
    align-items: center;
    gap: 8px;
}
.count-badge {
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78em;
    font-weight: 600;
    background: rgba(108,92,231,0.15);
    color: var(--accent-light);
}
.source-tag {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.68em;
    font-weight: 500;
    background: rgba(0,206,201,0.12);
    color: #00cec9;
    border: 1px solid rgba(0,206,201,0.2);
}
/* Item row */
.card-body { padding: 0; }
.item {
    display: flex;
    align-items: flex-start;
    padding: 12px 20px;
    border-bottom: 1px solid rgba(37,37,53,0.6);
    transition: background 0.2s;
    gap: 12px;
}
.item:last-child { border-bottom: none; }
.item:hover { background: var(--bg-card-hover); }
.item.hidden { display: none; }
.rank {
    min-width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.8em;
    margin-top: 2px;
    flex-shrink: 0;
    background: var(--bg-secondary);
    color: var(--text-muted);
}
.rank.r1 { background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: #fff; }
.rank.r2 { background: linear-gradient(135deg, #ffa502, #eccc68); color: #fff; }
.rank.r3 { background: linear-gradient(135deg, #6c5ce7, #a29bfe); color: #fff; }
.info { flex: 1; min-width: 0; }
.title-link {
    display: block;
    color: var(--text-primary);
    text-decoration: none;
    font-size: 0.92em;
    line-height: 1.55;
    word-break: break-all;
    transition: color 0.2s;
}
.title-link:hover { color: var(--accent-light); }
.meta-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 6px;
    flex-wrap: wrap;
}
.label-tag {
    display: inline-block;
    padding: 1px 8px;
    border-radius: 4px;
    font-size: 0.72em;
    font-weight: 500;
    background: rgba(108,92,231,0.12);
    color: var(--accent-light);
}
/* Hot bar */
.hot-container {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 120px;
    margin-top: 2px;
}
.hot-bar-wrap {
    flex: 1;
    height: 4px;
    background: var(--bg-secondary);
    border-radius: 2px;
    overflow: hidden;
    min-width: 60px;
}
.hot-bar {
    height: 100%;
    border-radius: 2px;
    background: var(--gradient-1);
    transition: width 0.5s ease;
}
.hot-value {
    font-size: 0.72em;
    color: var(--text-muted);
    white-space: nowrap;
    min-width: 32px;
    text-align: right;
}
/* Empty card */
.empty-card {
    background: var(--bg-card);
    border: 1px dashed var(--border-color);
    border-radius: var(--radius);
    padding: 40px;
    text-align: center;
    color: var(--text-muted);
    grid-column: 1 / -1;
}
.no-results {
    display: none;
    background: var(--bg-card);
    border: 1px dashed var(--border-color);
    border-radius: var(--radius);
    padding: 40px;
    text-align: center;
    color: var(--text-muted);
    grid-column: 1 / -1;
}
/* Footer */
.footer {
    text-align: center;
    padding: 40px 24px 30px;
    color: var(--text-muted);
    font-size: 0.82em;
    line-height: 1.8;
}
.footer a {
    color: var(--accent-light);
    text-decoration: none;
}
.footer a:hover { text-decoration: underline; }
/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
/* Animation */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.card { animation: fadeIn 0.4s ease forwards; opacity: 0; }
{% for i in range(30) %}
.card:nth-child({{ i + 1 }}) { animation-delay: {{ i * 0.04 }}s; }
{% endfor %}
/* Theme transitions */
body, .card, .header, .nav-bar, .search-bar {
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}
/* Light theme */
[data-theme="light"] {
    --bg-primary: #f5f5f7;
    --bg-secondary: #ffffff;
    --bg-card: #ffffff;
    --bg-card-hover: #f0f0f5;
    --border-color: #e0e0e5;
    --border-hover: #c0c0c8;
    --text-primary: #1a1a2e;
    --text-secondary: #555570;
    --text-muted: #8888a0;
    --shadow: 0 4px 24px rgba(0,0,0,0.06);
    --shadow-hover: 0 8px 40px rgba(108,92,231,0.1);
}
[data-theme="light"] .item {
    border-bottom-color: rgba(224,224,229,0.6);
}
[data-theme="light"] .search-bar {
    background: rgba(255,255,255,0.85);
}
[data-theme="light"] .source-badge {
    background: rgba(108,92,231,0.1);
    border-color: rgba(108,92,231,0.2);
}
[data-theme="light"] .count-badge {
    background: rgba(108,92,231,0.1);
}
/* Theme controls */
.theme-controls {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-left: auto;
    flex-shrink: 0;
}
.accent-dots {
    display: flex;
    gap: 6px;
    align-items: center;
}
.accent-dot {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    cursor: pointer;
    border: 2px solid transparent;
    transition: transform 0.2s, border-color 0.2s;
    flex-shrink: 0;
}
.accent-dot:hover { transform: scale(1.2); }
.accent-dot.active { border-color: var(--text-primary); transform: scale(1.15); }
.theme-toggle {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    border-radius: 20px;
    padding: 4px 12px;
    cursor: pointer;
    font-size: 0.9em;
    transition: all 0.2s;
    flex-shrink: 0;
    line-height: 1.4;
}
.theme-toggle:hover { border-color: var(--accent); }
@media (max-width: 500px) {
    .theme-controls { gap: 6px; }
    .accent-dot { width: 14px; height: 14px; }
}
</style>
</head>
<body>
<script>
(function(){
    var t=localStorage.getItem("hot-theme")||"dark";
    var a=localStorage.getItem("hot-accent")||"purple";
    document.documentElement.setAttribute("data-theme",t);
    var accents={
        purple:{accent:"#6c5ce7",light:"#a29bfe",glow:"rgba(108,92,231,0.3)",g1:"linear-gradient(135deg,#6c5ce7,#a29bfe)",g2:"linear-gradient(135deg,#fd79a8,#e84393)",g3:"linear-gradient(135deg,#00cec9,#0984e3)"},
        blue:{accent:"#0984e3",light:"#74b9ff",glow:"rgba(9,132,227,0.3)",g1:"linear-gradient(135deg,#0984e3,#74b9ff)",g2:"linear-gradient(135deg,#00cec9,#0984e3)",g3:"linear-gradient(135deg,#6c5ce7,#0984e3)"},
        green:{accent:"#00b894",light:"#55efc4",glow:"rgba(0,184,148,0.3)",g1:"linear-gradient(135deg,#00b894,#55efc4)",g2:"linear-gradient(135deg,#00cec9,#00b894)",g3:"linear-gradient(135deg,#00b894,#0984e3)"},
        pink:{accent:"#e84393",light:"#fd79a8",glow:"rgba(232,67,147,0.3)",g1:"linear-gradient(135deg,#e84393,#fd79a8)",g2:"linear-gradient(135deg,#fd79a8,#e84393)",g3:"linear-gradient(135deg,#e84393,#6c5ce7)"},
        orange:{accent:"#e17055",light:"#fab1a0",glow:"rgba(225,112,85,0.3)",g1:"linear-gradient(135deg,#e17055,#fab1a0)",g2:"linear-gradient(135deg,#ffa502,#e17055)",g3:"linear-gradient(135deg,#e17055,#e84393)"}
    };
    var c=accents[a]||accents.purple;
    var r=document.documentElement.style;
    r.setProperty("--accent",c.accent);
    r.setProperty("--accent-light",c.light);
    r.setProperty("--accent-glow",c.glow);
    r.setProperty("--gradient-1",c.g1);
    r.setProperty("--gradient-2",c.g2);
    r.setProperty("--gradient-3",c.g3);
})();
</script>

<div class="header">
    <div class="header-content">
        <h1>🔥 全网热点聚合</h1>
        <div class="date">{{ date }}</div>
        <div class="stats">
            <span class="stat-item">📊 <span class="stat-value">{{ platforms|length }}</span> 个平台</span>
            <span class="stat-item">📝 <span class="stat-value">{{ total }}</span> 条热点</span>
            <span class="stat-item">⚡ <span class="stat-value">{{ data_source }}</span></span>
        </div>
        <div class="source-badge">Powered by orz.ai + DailyHotApi + Local Fetchers</div>
    </div>
</div>

<div class="search-bar">
    <div class="search-inner">
        <input class="search-input" type="text" id="searchInput" placeholder="🔍 搜索热点关键词..." autocomplete="off">
        <span class="search-count" id="searchCount">共 <span>{{ total }}</span> 条</span>
        <div class="theme-controls">
            <div class="accent-dots" id="accentDots">
                <span class="accent-dot active" data-accent="purple" style="background:#6c5ce7" title="紫色"></span>
                <span class="accent-dot" data-accent="blue" style="background:#0984e3" title="蓝色"></span>
                <span class="accent-dot" data-accent="green" style="background:#00b894" title="绿色"></span>
                <span class="accent-dot" data-accent="pink" style="background:#e84393" title="粉色"></span>
                <span class="accent-dot" data-accent="orange" style="background:#e17055" title="橙色"></span>
            </div>
            <button class="theme-toggle" id="themeToggle" title="切换主题"></button>
        </div>
    </div>
</div>

<div class="category-bar">
    <div class="category-inner" id="categoryTabs">
        <span class="cat-chip active" data-cat="all">📋 全部</span>
        <span class="cat-chip" data-cat="social">👥 社交</span>
        <span class="cat-chip" data-cat="video">🎬 视频</span>
        <span class="cat-chip" data-cat="news">📰 新闻</span>
        <span class="cat-chip" data-cat="tech">💡 科技</span>
        <span class="cat-chip" data-cat="dev">🛠️ 技术</span>
        <span class="cat-chip" data-cat="finance">💰 财经</span>
        <span class="cat-chip" data-cat="other">📌 其他</span>
    </div>
</div>

{% if platforms %}
<div class="nav-bar">
    <div class="nav-inner" id="navChips">
        {% for p in platforms %}
        <a class="nav-chip" href="#card-{{ p.name | replace(' ', '-') }}" data-platform="{{ p.name }}">
            {{ p.icon }} {{ p.name }}
        </a>
        {% endfor %}
    </div>
</div>
{% endif %}

<div class="container" id="cardContainer">
{% for platform in platforms %}
    {% if platform.entries %}
    <div class="card" id="card-{{ platform.name | replace(' ', '-') }}" data-category="{{ platform.category }}" data-platform="{{ platform.name }}">
        <div class="card-header">
            <div class="platform-info">
                <span class="platform-icon">{{ platform.icon }}</span>
                <h2>{{ platform.name }}</h2>
                {% if platform.description %}
                <span class="platform-desc">{{ platform.description }}</span>
                {% endif %}
            </div>
            <div class="right-badges">
                <span class="source-tag">{{ platform.source }}</span>
                <span class="count-badge">{{ platform.entries|length }} 条</span>
            </div>
        </div>
        <div class="card-body">
        {% for item in platform.entries %}
            <div class="item" data-title="{{ item.title | lower | e }}">
                <div class="rank {% if item.rank == 1 %}r1{% elif item.rank == 2 %}r2{% elif item.rank == 3 %}r3{% endif %}">
                    {{ item.rank }}
                </div>
                <div class="info">
                    <a class="title-link" href="{{ item.url }}" target="_blank" rel="noopener">{{ item.title }}</a>
                    <div class="meta-row">
                        {% if item.label %}
                        <span class="label-tag">{{ item.label }}</span>
                        {% endif %}
                        {% if item.hot and item.hot != "0" and item.hot != "0.0" and item.hot != "" %}
                        <div class="hot-container">
                            <div class="hot-bar-wrap">
                                <div class="hot-bar" style="width: {{ item.hot_pct }}%"></div>
                            </div>
                            <span class="hot-value">{{ item.hot_display }}</span>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        {% endfor %}
        </div>
    </div>
    {% endif %}
{% endfor %}
{% if not platforms or platforms|length == 0 %}
    <div class="empty-card">
        <p>😕 未获取到热点数据</p>
        <p style="margin-top:8px">请检查网络连接或稍后重试</p>
    </div>
{% endif %}
<div class="no-results" id="noResults">
    <p>🔍 没有匹配的结果</p>
    <p style="margin-top:8px">试试其他关键词</p>
</div>
</div>

<div class="footer">
    <p>数据来源: orz.ai · DailyHotApi · 本地爬虫 · {{ data_source_detail }}</p>
    <p>Generated by Hot Aggregator · {{ gen_time }}</p>
</div>

<script>
(function() {
    var input = document.getElementById('searchInput');
    var countEl = document.getElementById('searchCount');
    var container = document.getElementById('cardContainer');
    var noResults = document.getElementById('noResults');
    var cards = container.querySelectorAll('.card');
    var activeCat = 'all';

    // Category click
    document.getElementById('categoryTabs').addEventListener('click', function(e) {
        var chip = e.target.closest('.cat-chip');
        if (!chip) return;
        document.querySelectorAll('.cat-chip').forEach(function(c) { c.classList.remove('active'); });
        chip.classList.add('active');
        activeCat = chip.getAttribute('data-cat');
        applyFilters();
    });

    // Search input
    var timer;
    input.addEventListener('input', function() {
        clearTimeout(timer);
        timer = setTimeout(applyFilters, 150);
    });

    function applyFilters() {
        var q = input.value.trim().toLowerCase();
        var visible = 0;
        cards.forEach(function(card) {
            var matchCat = activeCat === 'all' || card.getAttribute('data-category') === activeCat;
            var matchSearch = true;
            if (q) {
                var items = card.querySelectorAll('.item');
                var hasMatch = false;
                items.forEach(function(item) {
                    var title = item.getAttribute('data-title') || '';
                    if (title.indexOf(q) >= 0) {
                        item.classList.remove('hidden');
                        hasMatch = true;
                    } else {
                        item.classList.add('hidden');
                    }
                });
                matchSearch = hasMatch;
            } else {
                card.querySelectorAll('.item').forEach(function(item) {
                    item.classList.remove('hidden');
                });
            }
            if (matchCat && matchSearch) {
                card.classList.remove('hidden');
                visible++;
            } else {
                card.classList.add('hidden');
            }
        });
        noResults.style.display = visible === 0 ? 'block' : 'none';
        countEl.innerHTML = '共 <span>' + countVisible() + '</span> 条';
    }

    function countVisible() {
        var n = 0;
        cards.forEach(function(card) {
            if (!card.classList.contains('hidden')) {
                card.querySelectorAll('.item').forEach(function(item) {
                    if (!item.classList.contains('hidden')) n++;
                });
            }
        });
        return n;
    }

    // === Theme switching ===
    var accents = {
        purple:{accent:"#6c5ce7",light:"#a29bfe",glow:"rgba(108,92,231,0.3)",g1:"linear-gradient(135deg,#6c5ce7,#a29bfe)",g2:"linear-gradient(135deg,#fd79a8,#e84393)",g3:"linear-gradient(135deg,#00cec9,#0984e3)"},
        blue:{accent:"#0984e3",light:"#74b9ff",glow:"rgba(9,132,227,0.3)",g1:"linear-gradient(135deg,#0984e3,#74b9ff)",g2:"linear-gradient(135deg,#00cec9,#0984e3)",g3:"linear-gradient(135deg,#6c5ce7,#0984e3)"},
        green:{accent:"#00b894",light:"#55efc4",glow:"rgba(0,184,148,0.3)",g1:"linear-gradient(135deg,#00b894,#55efc4)",g2:"linear-gradient(135deg,#00cec9,#00b894)",g3:"linear-gradient(135deg,#00b894,#0984e3)"},
        pink:{accent:"#e84393",light:"#fd79a8",glow:"rgba(232,67,147,0.3)",g1:"linear-gradient(135deg,#e84393,#fd79a8)",g2:"linear-gradient(135deg,#fd79a8,#e84393)",g3:"linear-gradient(135deg,#e84393,#6c5ce7)"},
        orange:{accent:"#e17055",light:"#fab1a0",glow:"rgba(225,112,85,0.3)",g1:"linear-gradient(135deg,#e17055,#fab1a0)",g2:"linear-gradient(135deg,#ffa502,#e17055)",g3:"linear-gradient(135deg,#e17055,#e84393)"}
    };

    function applyAccent(name) {
        var c = accents[name];
        if (!c) return;
        var r = document.documentElement.style;
        r.setProperty("--accent", c.accent);
        r.setProperty("--accent-light", c.light);
        r.setProperty("--accent-glow", c.glow);
        r.setProperty("--gradient-1", c.g1);
        r.setProperty("--gradient-2", c.g2);
        r.setProperty("--gradient-3", c.g3);
        localStorage.setItem("hot-accent", name);
        document.querySelectorAll(".accent-dot").forEach(function(d) {
            d.classList.toggle("active", d.getAttribute("data-accent") === name);
        });
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("hot-theme", theme);
        document.getElementById("themeToggle").textContent = theme === "dark" ? "☀️" : "🌙";
    }

    // Init toggle button text
    var currentTheme = localStorage.getItem("hot-theme") || "dark";
    var currentAccent = localStorage.getItem("hot-accent") || "purple";
    document.getElementById("themeToggle").textContent = currentTheme === "dark" ? "☀️" : "🌙";

    // Highlight active accent dot
    document.querySelectorAll(".accent-dot").forEach(function(d) {
        d.classList.toggle("active", d.getAttribute("data-accent") === currentAccent);
    });

    document.getElementById("themeToggle").addEventListener("click", function() {
        var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
        applyTheme(next);
    });

    document.getElementById("accentDots").addEventListener("click", function(e) {
        var dot = e.target.closest(".accent-dot");
        if (!dot) return;
        applyAccent(dot.getAttribute("data-accent"));
    });
})();
</script>
</body>
</html>
"""


# 平台分类映射
PLATFORM_CATEGORIES = {
    # 社交
    "微博热搜": "social", "知乎热榜": "social", "豆瓣": "social",
    "百度贴吧": "social", "虎扑": "social",
    # 视频
    "B站热门": "video", "抖音热点": "video",
    # 新闻
    "今日头条": "news", "百度热搜": "news", "腾讯新闻": "news",
    "网易新闻": "news", "新浪热点": "news", "澎湃新闻": "news",
    # 科技
    "36氪": "tech", "少数派": "tech", "IT之家": "tech",
    "虎嗅": "tech",
    # 技术
    "掘金": "dev", "GitHub日榜": "dev", "GitHub周榜": "dev", "GitHub月榜": "dev",
    "V2EX": "dev",
    "Stack Overflow": "dev", "Hacker News": "dev", "CSDN": "dev",
    "吾爱破解": "dev", "HelloGitHub": "dev",
    # 财经
    "新浪财经": "finance", "东方财富": "finance",
    "雪球": "finance", "财联社": "finance",
}


def _format_hot(value) -> tuple[str, float]:
    """格式化热度值，返回 (显示文本, 百分比)"""
    if not value or value in ("0", "0.0", ""):
        return "", 0

    try:
        num = float(str(value).replace(",", "").replace(" ", "").replace("🔥", ""))
    except (ValueError, TypeError):
        return str(value), 50

    # 计算百分比（对数缩放，避免极端值）
    import math
    if num <= 0:
        return "", 0
    log_val = math.log10(max(num, 1))
    pct = min(100, max(5, log_val / 8 * 100))

    # 格式化显示
    if num >= 1_0000_0000:
        display = f"{num/1_0000_0000:.1f}亿"
    elif num >= 1_0000:
        display = f"{num/1_0000:.1f}万"
    elif num >= 1000:
        display = f"{num/1000:.1f}k"
    else:
        display = str(int(num))

    return display, pct


def generate_report(all_data: dict, output_dir: str = "output",
                    source_stats: dict = None) -> str:
    """生成 HTML 报告，返回文件路径

    Args:
        all_data: {平台名: [items]} 字典
        output_dir: 输出目录
        source_stats: 数据源统计 {"orz.ai": N, "自爬": N, "DailyHotApi": N}
    """
    now = datetime.now()
    date_str = now.strftime("%Y年%m月%d日 %H:%M")
    gen_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # 平台描述映射
    platform_descriptions = {
        "GitHub日榜": "最近24小时最受关注的开源项目",
        "GitHub周榜": "最近7天最受关注的开源项目",
        "GitHub月榜": "最近30天最受关注的开源项目",
        "Hacker News": "硅谷科技圈最热讨论",
        "Stack Overflow": "程序员问答社区热门问题",
        "V2EX": "创意工作者社区热议话题",
        "掘金": "前端/后端/AI技术分享",
        "吾爱破解": "软件逆向与安全研究",
    }

    # 扩展的平台图标映射
    platform_icons = {
        # 社交
        "微博热搜": "🔥",
        "知乎热榜": "💡",
        "豆瓣": "🎬",
        "百度贴吧": "💭",
        "虎扑": "🏀",
        # 视频
        "B站热门": "📺",
        "抖音热点": "🎵",
        # 新闻
        "今日头条": "📰",
        "百度热搜": "🔍",
        "腾讯新闻": "📡",
        "网易新闻": "📣",
        "新浪热点": "🌐",
        "澎湃新闻": "🌊",
        # 科技
        "36氪": "🚀",
        "少数派": "🎯",
        "IT之家": "💻",
        "虎嗅": "🐅",
        # 技术
        "掘金": "⛏️",
        "GitHub日榜": "🐙",
        "GitHub周榜": "📅",
        "GitHub月榜": "📆",
        "V2EX": "💬",
        "Stack Overflow": "🧑‍💻",
        "Hacker News": "🟠",
        "CSDN": "🎓",
        "吾爱破解": "🔓",
        "HelloGitHub": "🌟",
        # 财经
        "新浪财经": "💹",
        "东方财富": "💰",
        "雪球": "📈",
        "财联社": "📊",
        # 其他
        "快手热榜": "🎬",
        "酷安": "📱",
        "AcFun": "猿",
        "微信读书": "📚",
    }

    # 计算全局最大热度（用于百分比计算）
    global_max_hot = 0
    for items in all_data.values():
        for item in items:
            hot_val = item.get("hot", "")
            if hot_val:
                try:
                    num = float(str(hot_val).replace(",", "").replace(" ", ""))
                    global_max_hot = max(global_max_hot, num)
                except (ValueError, TypeError):
                    pass

    platforms = []
    total = 0
    for name, items in all_data.items():
        icon = platform_icons.get(name, "📌")
        category = PLATFORM_CATEGORIES.get(name, "other")
        source = "自爬"
        if source_stats and name in source_stats.get("_per_platform", {}):
            source = source_stats["_per_platform"][name]

        # 为每个 item 添加热度显示和百分比
        entries = []
        for item in items:
            # 确保字段类型正确
            for key in ("hot", "label", "title", "url", "platform"):
                val = item.get(key, "")
                if val is None:
                    item[key] = ""
                elif not isinstance(val, str):
                    item[key] = str(val)
            if not isinstance(item.get("rank"), int):
                try:
                    item["rank"] = int(item.get("rank", 0))
                except (ValueError, TypeError):
                    item["rank"] = 0

            hot_display, hot_pct = _format_hot(item.get("hot", ""))
            item["hot_display"] = hot_display
            item["hot_pct"] = round(hot_pct, 1)
            entries.append(item)

        platforms.append({
            "name": name,
            "icon": icon,
            "description": platform_descriptions.get(name, ""),
            "entries": entries,
            "category": category,
            "source": source,
        })
        total += len(entries)

    # 按数量排序
    platforms.sort(key=lambda x: len(x["entries"]), reverse=True)

    # 动态生成数据源描述
    if source_stats:
        parts = []
        for src_name, count in source_stats.items():
            if src_name == "_per_platform":
                continue
            if count > 0:
                parts.append(f"{src_name}({count})")
        data_source = " + ".join(parts) if parts else "混合"
        data_source_detail = "、".join(s for s, c in source_stats.items() if s != "_per_platform" and c > 0)
    else:
        data_source = "混合"
        data_source_detail = "orz.ai · DailyHotApi · 本地爬虫"

    html = Template(TEMPLATE_STR).render(
        date=date_str,
        gen_time=gen_time,
        platforms=platforms,
        total=total,
        data_source=data_source,
        data_source_detail=data_source_detail,
    )

    os.makedirs(output_dir, exist_ok=True)
    filename = f"hot_{now.strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    # 同时保存一份 latest.html 方便查看
    latest_path = os.path.join(output_dir, "latest.html")
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(html)

    return filepath
