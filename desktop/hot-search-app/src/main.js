// Theme and accent initialization (runs before render)
(function() {
    var t = localStorage.getItem("hot-theme") || "dark";
    var a = localStorage.getItem("hot-accent") || "purple";
    document.documentElement.setAttribute("data-theme", t);
    var accents = {
        purple: { accent: "#6c5ce7", light: "#a29bfe", glow: "rgba(108,92,231,0.3)", g1: "linear-gradient(135deg,#6c5ce7,#a29bfe)", g2: "linear-gradient(135deg,#fd79a8,#e84393)", g3: "linear-gradient(135deg,#00cec9,#0984e3)" },
        blue: { accent: "#0984e3", light: "#74b9ff", glow: "rgba(9,132,227,0.3)", g1: "linear-gradient(135deg,#0984e3,#74b9ff)", g2: "linear-gradient(135deg,#00cec9,#0984e3)", g3: "linear-gradient(135deg,#6c5ce7,#0984e3)" },
        green: { accent: "#00b894", light: "#55efc4", glow: "rgba(0,184,148,0.3)", g1: "linear-gradient(135deg,#00b894,#55efc4)", g2: "linear-gradient(135deg,#00cec9,#00b894)", g3: "linear-gradient(135deg,#00b894,#0984e3)" },
        pink: { accent: "#e84393", light: "#fd79a8", glow: "rgba(232,67,147,0.3)", g1: "linear-gradient(135deg,#e84393,#fd79a8)", g2: "linear-gradient(135deg,#fd79a8,#e84393)", g3: "linear-gradient(135deg,#e84393,#6c5ce7)" },
        orange: { accent: "#e17055", light: "#fab1a0", glow: "rgba(225,112,85,0.3)", g1: "linear-gradient(135deg,#e17055,#fab1a0)", g2: "linear-gradient(135deg,#ffa502,#e17055)", g3: "linear-gradient(135deg,#e17055,#e84393)" }
    };
    var c = accents[a] || accents.purple;
    var r = document.documentElement.style;
    r.setProperty("--accent", c.accent);
    r.setProperty("--accent-light", c.light);
    r.setProperty("--accent-glow", c.glow);
    r.setProperty("--gradient-1", c.g1);
    r.setProperty("--gradient-2", c.g2);
    r.setProperty("--gradient-3", c.g3);
})();

// Main app logic
const invoke = window.__TAURI__.core.invoke;

let appState = {
    data: null,
    loading: false,
    activeCat: 'all',
    autoRefresh: false,
    autoRefreshTimer: null
};

// === Hot value formatting (same as Python) ===
function formatHot(value) {
    if (!value || value === "0" || value === "0.0" || value === "") return { display: "", pct: 0 };
    let num;
    try {
        num = parseFloat(String(value).replace(/,/g, "").replace(/ /g, "").replace(/🔥/g, ""));
    } catch {
        return { display: String(value), pct: 50 };
    }
    if (isNaN(num) || num <= 0) return { display: "", pct: 0 };

    // Logarithmic scale
    let logVal = Math.log10(Math.max(num, 1));
    let pct = Math.min(100, Math.max(5, logVal / 8 * 100));

    let display;
    if (num >= 1e8) display = (num / 1e8).toFixed(1) + "亿";
    else if (num >= 1e4) display = (num / 1e4).toFixed(1) + "万";
    else if (num >= 1000) display = (num / 1000).toFixed(1) + "k";
    else display = String(Math.floor(num));

    return { display, pct };
}

// === Render ===
function renderPlatforms(cachedData) {
    const container = document.getElementById('cardContainer');
    const navChips = document.getElementById('navChips');
    const noResults = document.getElementById('noResults');
    const searchCount = document.getElementById('searchCount');
    const dateEl = document.getElementById('dateDisplay');
    const platformCountEl = document.getElementById('platformCount');
    const totalCountEl = document.getElementById('totalCount');
    const updateTimeEl = document.getElementById('updateTime');

    if (!cachedData || !cachedData.platforms || cachedData.platforms.length === 0) {
        container.innerHTML = '<div class="empty-card"><p>😕 未获取到热点数据</p><p style="margin-top:8px">请检查网络连接或稍后重试</p></div>';
        navChips.innerHTML = '';
        searchCount.innerHTML = '共 <span>0</span> 条';
        return;
    }

    appState.data = cachedData;
    const { platforms, total, updated_at } = cachedData;

    // Update header
    dateEl.textContent = updated_at;
    platformCountEl.textContent = platforms.filter(p => p.entries.length > 0).length;
    totalCountEl.textContent = total;
    updateTimeEl.textContent = '更新: ' + updated_at;

    // Render nav chips
    let navHtml = '';
    for (const p of platforms) {
        if (p.entries.length === 0) continue;
        navHtml += `<span class="nav-chip" data-platform="${p.name}" onclick="scrollToCard('${p.name}')">${p.icon} ${p.display_name}</span>`;
    }
    navChips.innerHTML = navHtml;

    // Render cards
    let cardsHtml = '';
    for (const p of platforms) {
        if (p.entries.length === 0) continue;

        let itemsHtml = '';
        for (const item of p.entries) {
            let hotHtml = '';
            if (item.hot && item.hot !== "0" && item.hot !== "0.0" && item.hot !== "") {
                const { display, pct } = formatHot(item.hot);
                if (display) {
                    hotHtml = `<div class="hot-container">
                        <div class="hot-bar-wrap"><div class="hot-bar" style="width:${pct.toFixed(1)}%"></div></div>
                        <span class="hot-value">${display}</span>
                    </div>`;
                }
            }

            let labelHtml = '';
            if (item.label) {
                labelHtml = `<span class="label-tag">${escapeHtml(item.label)}</span>`;
            }

            let rankClass = '';
            if (item.rank === 1) rankClass = 'r1';
            else if (item.rank === 2) rankClass = 'r2';
            else if (item.rank === 3) rankClass = 'r3';

            itemsHtml += `<div class="item" data-title="${escapeHtml(item.title.toLowerCase())}">
                <div class="rank ${rankClass}">${item.rank}</div>
                <div class="info">
                    <a class="title-link" href="${escapeHtml(item.url)}" target="_blank" rel="noopener">${escapeHtml(item.title)}</a>
                    <div class="meta-row">
                        ${labelHtml}
                        ${hotHtml}
                    </div>
                </div>
            </div>`;
        }

        let descHtml = p.description ? `<span class="platform-desc">${escapeHtml(p.description)}</span>` : '';

        cardsHtml += `<div class="card" id="card-${p.name}" data-category="${p.category}" data-platform="${p.name}">
            <div class="card-header">
                <div class="platform-info">
                    <span class="platform-icon">${p.icon}</span>
                    <h2>${escapeHtml(p.display_name)}</h2>
                    ${descHtml}
                </div>
                <div class="right-badges">
                    <span class="source-tag">${escapeHtml(p.source)}</span>
                    <span class="count-badge">${p.entries.length} 条</span>
                </div>
            </div>
            <div class="card-body">
                ${itemsHtml}
            </div>
        </div>`;
    }

    if (cardsHtml === '') {
        cardsHtml = '<div class="empty-card"><p>😕 未获取到热点数据</p><p style="margin-top:8px">请检查网络连接或稍后重试</p></div>';
    }

    cardsHtml += '<div class="no-results" id="noResults"><p>🔍 没有匹配的结果</p><p style="margin-top:8px">试试其他关键词</p></div>';
    container.innerHTML = cardsHtml;

    searchCount.innerHTML = `共 <span>${total}</span> 条`;

    // Re-apply filters
    applyFilters();
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function scrollToCard(platformName) {
    const card = document.getElementById('card-' + platformName);
    if (card) {
        card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// === Fetch ===
async function fetchAllPlatforms() {
    const btn = document.getElementById('refreshBtn');
    if (appState.loading) return;
    appState.loading = true;
    btn.classList.add('loading');
    btn.innerHTML = '<span class="loading-spinner"></span>加载中...';

    try {
        const data = await invoke('fetch_all_platforms');
        renderPlatforms(data);
    } catch (e) {
        console.error('Fetch error:', e);
        const container = document.getElementById('cardContainer');
        container.innerHTML = `<div class="empty-card"><p>❌ 获取数据失败</p><p style="margin-top:8px">${escapeHtml(String(e))}</p></div>`;
    } finally {
        appState.loading = false;
        btn.classList.remove('loading');
        btn.textContent = '🔄 刷新数据';
    }
}

// === Search & Filter ===
let searchTimer;

function initSearch() {
    const input = document.getElementById('searchInput');
    input.addEventListener('input', function() {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(applyFilters, 150);
    });
}

function initCategoryTabs() {
    document.getElementById('categoryTabs').addEventListener('click', function(e) {
        const chip = e.target.closest('.cat-chip');
        if (!chip) return;
        document.querySelectorAll('.cat-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        appState.activeCat = chip.getAttribute('data-cat');
        applyFilters();
    });
}

function applyFilters() {
    const input = document.getElementById('searchInput');
    const countEl = document.getElementById('searchCount');
    const container = document.getElementById('cardContainer');
    const noResults = document.getElementById('noResults');
    if (!container) return;

    const cards = container.querySelectorAll('.card');
    const q = input ? input.value.trim().toLowerCase() : '';
    let visible = 0;

    cards.forEach(function(card) {
        const matchCat = appState.activeCat === 'all' || card.getAttribute('data-category') === appState.activeCat;
        let matchSearch = true;

        if (q) {
            const items = card.querySelectorAll('.item');
            let hasMatch = false;
            items.forEach(function(item) {
                const title = item.getAttribute('data-title') || '';
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

    if (noResults) {
        noResults.style.display = visible === 0 ? 'block' : 'none';
    }

    const totalCount = countVisible();
    if (countEl) {
        countEl.innerHTML = '共 <span>' + totalCount + '</span> 条';
    }
}

function countVisible() {
    const container = document.getElementById('cardContainer');
    if (!container) return 0;
    const cards = container.querySelectorAll('.card');
    let n = 0;
    cards.forEach(function(card) {
        if (!card.classList.contains('hidden')) {
            card.querySelectorAll('.item').forEach(function(item) {
                if (!item.classList.contains('hidden')) n++;
            });
        }
    });
    return n;
}

// === Theme ===
const accents = {
    purple: { accent: "#6c5ce7", light: "#a29bfe", glow: "rgba(108,92,231,0.3)", g1: "linear-gradient(135deg,#6c5ce7,#a29bfe)", g2: "linear-gradient(135deg,#fd79a8,#e84393)", g3: "linear-gradient(135deg,#00cec9,#0984e3)" },
    blue: { accent: "#0984e3", light: "#74b9ff", glow: "rgba(9,132,227,0.3)", g1: "linear-gradient(135deg,#0984e3,#74b9ff)", g2: "linear-gradient(135deg,#00cec9,#0984e3)", g3: "linear-gradient(135deg,#6c5ce7,#0984e3)" },
    green: { accent: "#00b894", light: "#55efc4", glow: "rgba(0,184,148,0.3)", g1: "linear-gradient(135deg,#00b894,#55efc4)", g2: "linear-gradient(135deg,#00cec9,#00b894)", g3: "linear-gradient(135deg,#00b894,#0984e3)" },
    pink: { accent: "#e84393", light: "#fd79a8", glow: "rgba(232,67,147,0.3)", g1: "linear-gradient(135deg,#e84393,#fd79a8)", g2: "linear-gradient(135deg,#fd79a8,#e84393)", g3: "linear-gradient(135deg,#e84393,#6c5ce7)" },
    orange: { accent: "#e17055", light: "#fab1a0", glow: "rgba(225,112,85,0.3)", g1: "linear-gradient(135deg,#e17055,#fab1a0)", g2: "linear-gradient(135deg,#ffa502,#e17055)", g3: "linear-gradient(135deg,#e17055,#e84393)" }
};

function applyAccent(name) {
    const c = accents[name];
    if (!c) return;
    const r = document.documentElement.style;
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

function initThemeControls() {
    const currentTheme = localStorage.getItem("hot-theme") || "dark";
    const currentAccent = localStorage.getItem("hot-accent") || "purple";
    document.getElementById("themeToggle").textContent = currentTheme === "dark" ? "☀️" : "🌙";
    document.querySelectorAll(".accent-dot").forEach(function(d) {
        d.classList.toggle("active", d.getAttribute("data-accent") === currentAccent);
    });

    document.getElementById("themeToggle").addEventListener("click", function() {
        const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
        applyTheme(next);
    });

    document.getElementById("accentDots").addEventListener("click", function(e) {
        const dot = e.target.closest(".accent-dot");
        if (!dot) return;
        applyAccent(dot.getAttribute("data-accent"));
    });
}

// === Auto-refresh ===
function initAutoRefresh() {
    const cb = document.getElementById('autoRefreshCb');
    cb.addEventListener('change', function() {
        appState.autoRefresh = cb.checked;
        if (appState.autoRefresh) {
            appState.autoRefreshTimer = setInterval(fetchAllPlatforms, 30 * 60 * 1000);
        } else {
            if (appState.autoRefreshTimer) {
                clearInterval(appState.autoRefreshTimer);
                appState.autoRefreshTimer = null;
            }
        }
    });
}

// === Init ===
document.addEventListener('DOMContentLoaded', async function() {
    initThemeControls();
    initSearch();
    initCategoryTabs();
    initAutoRefresh();

    // Show loading state
    const container = document.getElementById('cardContainer');
    container.innerHTML = '<div class="empty-card"><p><span class="loading-spinner"></span> 正在加载热点数据...</p></div>';

    // Try to load cached data first
    try {
        const cached = await invoke('get_cached_data');
        if (cached) {
            renderPlatforms(cached);
        } else {
            await fetchAllPlatforms();
        }
    } catch (e) {
        console.error('Init error:', e);
        await fetchAllPlatforms();
    }

    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', fetchAllPlatforms);
});
