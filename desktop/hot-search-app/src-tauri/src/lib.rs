use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use tauri::State;

// ===== Data Structures =====

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlatformConfig {
    pub name: String,
    pub orz_name: String,
    pub display_name: String,
    pub icon: String,
    pub category: String,
    pub description: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HotItem {
    pub platform: String,
    pub title: String,
    pub url: String,
    pub hot: String,
    pub label: String,
    pub rank: i32,
    pub content: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlatformData {
    pub name: String,
    pub display_name: String,
    pub icon: String,
    pub category: String,
    pub description: String,
    pub source: String,
    pub entries: Vec<HotItem>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CachedData {
    pub platforms: Vec<PlatformData>,
    pub total: i32,
    pub updated_at: String,
}

pub struct AppState {
    pub cached: Mutex<Option<CachedData>>,
}

// ===== Platform Configs =====

fn get_platform_configs() -> Vec<PlatformConfig> {
    vec![
        // Social
        PlatformConfig {
            name: "weibo".into(),
            orz_name: "weibo".into(),
            display_name: "微博热搜".into(),
            icon: "🔥".into(),
            category: "social".into(),
            description: "".into(),
        },
        PlatformConfig {
            name: "zhihu".into(),
            orz_name: "zhihu".into(),
            display_name: "知乎热榜".into(),
            icon: "💡".into(),
            category: "social".into(),
            description: "".into(),
        },
        PlatformConfig {
            name: "douban".into(),
            orz_name: "douban".into(),
            display_name: "豆瓣".into(),
            icon: "🎬".into(),
            category: "social".into(),
            description: "".into(),
        },
        PlatformConfig {
            name: "tieba".into(),
            orz_name: "tieba".into(),
            display_name: "百度贴吧".into(),
            icon: "💭".into(),
            category: "social".into(),
            description: "".into(),
        },
        PlatformConfig {
            name: "hupu".into(),
            orz_name: "hupu".into(),
            display_name: "虎扑".into(),
            icon: "🏀".into(),
            category: "social".into(),
            description: "".into(),
        },
        // Video
        PlatformConfig {
            name: "bilibili".into(),
            orz_name: "bilibili".into(),
            display_name: "B站热门".into(),
            icon: "📺".into(),
            category: "video".into(),
            description: "".into(),
        },
        PlatformConfig {
            name: "douyin".into(),
            orz_name: "douyin".into(),
            display_name: "抖音热点".into(),
            icon: "🎵".into(),
            category: "video".into(),
            description: "".into(),
        },
        // News
        PlatformConfig {
            name: "toutiao".into(),
            orz_name: "jinritoutiao".into(),
            display_name: "今日头条".into(),
            icon: "📰".into(),
            category: "news".into(),
            description: "".into(),
        },
        PlatformConfig {
            name: "baidu".into(),
            orz_name: "baidu".into(),
            display_name: "百度热搜".into(),
            icon: "🔍".into(),
            category: "news".into(),
            description: "".into(),
        },
        PlatformConfig {
            name: "tencent_news".into(),
            orz_name: "tenxunwang".into(),
            display_name: "腾讯新闻".into(),
            icon: "📡".into(),
            category: "news".into(),
            description: "".into(),
        },
        // Tech
        PlatformConfig {
            name: "36kr".into(),
            orz_name: "36kr".into(),
            display_name: "36氪".into(),
            icon: "🚀".into(),
            category: "tech".into(),
            description: "".into(),
        },
        PlatformConfig {
            name: "sspai".into(),
            orz_name: "shaoshupai".into(),
            display_name: "少数派".into(),
            icon: "🎯".into(),
            category: "tech".into(),
            description: "".into(),
        },
        // Dev
        PlatformConfig {
            name: "juejin".into(),
            orz_name: "juejin".into(),
            display_name: "掘金".into(),
            icon: "⛏️".into(),
            category: "dev".into(),
            description: "前端/后端/AI技术分享".into(),
        },
        PlatformConfig {
            name: "github".into(),
            orz_name: "github".into(),
            display_name: "GitHub日榜".into(),
            icon: "🐙".into(),
            category: "dev".into(),
            description: "最近24小时最受关注的开源项目".into(),
        },
        PlatformConfig {
            name: "v2ex".into(),
            orz_name: "v2ex".into(),
            display_name: "V2EX".into(),
            icon: "💬".into(),
            category: "dev".into(),
            description: "创意工作者社区热议话题".into(),
        },
        PlatformConfig {
            name: "stackoverflow".into(),
            orz_name: "stackoverflow".into(),
            display_name: "Stack Overflow".into(),
            icon: "🧑‍💻".into(),
            category: "dev".into(),
            description: "程序员问答社区热门问题".into(),
        },
        PlatformConfig {
            name: "hackernews".into(),
            orz_name: "hackernews".into(),
            display_name: "Hacker News".into(),
            icon: "🟠".into(),
            category: "dev".into(),
            description: "硅谷科技圈最热讨论".into(),
        },
        PlatformConfig {
            name: "52pojie".into(),
            orz_name: "52pojie".into(),
            display_name: "吾爱破解".into(),
            icon: "🔓".into(),
            category: "dev".into(),
            description: "软件逆向与安全研究".into(),
        },
        // Finance
        PlatformConfig {
            name: "sina_finance".into(),
            orz_name: "sina_finance".into(),
            display_name: "新浪财经".into(),
            icon: "💹".into(),
            category: "finance".into(),
            description: "".into(),
        },
        PlatformConfig {
            name: "eastmoney".into(),
            orz_name: "eastmoney".into(),
            display_name: "东方财富".into(),
            icon: "💰".into(),
            category: "finance".into(),
            description: "".into(),
        },
        PlatformConfig {
            name: "xueqiu".into(),
            orz_name: "xueqiu".into(),
            display_name: "雪球".into(),
            icon: "📈".into(),
            category: "finance".into(),
            description: "".into(),
        },
        PlatformConfig {
            name: "cls".into(),
            orz_name: "cls".into(),
            display_name: "财联社".into(),
            icon: "📊".into(),
            category: "finance".into(),
            description: "".into(),
        },
    ]
}

// ===== API Response Parsing =====

async fn fetch_single_platform(config: &PlatformConfig) -> Result<Vec<HotItem>, String> {
    let url = format!(
        "https://orz.ai/api/v1/dailynews?platform={}",
        config.orz_name
    );

    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(15))
        .build()
        .map_err(|e| format!("创建HTTP客户端失败: {}", e))?;

    let resp = client
        .get(&url)
        .header(
            "User-Agent",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        .header("Accept", "application/json")
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;

    let body: serde_json::Value = resp
        .json()
        .await
        .map_err(|e| format!("解析JSON失败: {}", e))?;

    // Check status field - can be "success" or "200"
    let status_ok = match &body["status"] {
        serde_json::Value::String(s) => s == "success" || s == "200",
        serde_json::Value::Number(n) => n.as_i64() == Some(200),
        _ => false,
    };

    if !status_ok {
        return Err(format!("API返回错误状态: {}", body["status"]));
    }

    // Extract data array
    let items_raw = match &body["data"] {
        serde_json::Value::Array(arr) => arr.clone(),
        _ => {
            // Sometimes the whole response might be an array
            if body.is_array() {
                body.as_array().unwrap().clone()
            } else {
                return Ok(vec![]);
            }
        }
    };

    let mut items = Vec::new();
    for (idx, entry) in items_raw.iter().take(30).enumerate() {
        if !entry.is_object() {
            continue;
        }

        let title = entry
            .get("title")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let url = entry
            .get("url")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let content = {
            let c = entry
                .get("content")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            match c.char_indices().nth(200) {
                Some((idx, _)) => format!("{}...", &c[..idx]),
                None => c,
            }
        };

        let label = entry
            .get("source")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        items.push(HotItem {
            platform: config.display_name.clone(),
            title,
            url,
            hot: String::new(),
            label,
            rank: (idx + 1) as i32,
            content,
        });
    }

    Ok(items)
}

// ===== Tauri Commands =====

#[tauri::command]
async fn fetch_all_platforms(state: State<'_, AppState>) -> Result<CachedData, String> {
    let configs = get_platform_configs();
    let mut handles = Vec::new();

    for config in &configs {
        let config_clone = config.clone();
        handles.push(tokio::spawn(async move {
            match fetch_single_platform(&config_clone).await {
                Ok(items) => PlatformData {
                    name: config_clone.name,
                    display_name: config_clone.display_name,
                    icon: config_clone.icon,
                    category: config_clone.category,
                    description: config_clone.description,
                    source: "orz.ai".into(),
                    entries: items,
                },
                Err(_) => PlatformData {
                    name: config_clone.name,
                    display_name: config_clone.display_name,
                    icon: config_clone.icon,
                    category: config_clone.category,
                    description: config_clone.description,
                    source: "orz.ai".into(),
                    entries: vec![],
                },
            }
        }));
    }

    let mut platforms = Vec::new();
    let mut total = 0;
    for handle in handles {
        match handle.await {
            Ok(pd) => {
                total += pd.entries.len() as i32;
                platforms.push(pd);
            }
            Err(e) => {
                return Err(format!("任务执行失败: {}", e));
            }
        }
    }

    // Sort by number of entries (descending)
    platforms.sort_by(|a, b| b.entries.len().cmp(&a.entries.len()));

    let now = chrono::Local::now();
    let updated_at = now.format("%Y年%m月%d日 %H:%M:%S").to_string();

    let cached_data = CachedData {
        platforms,
        total,
        updated_at,
    };

    // Store in state
    {
        let mut cache = state.cached.lock().map_err(|e| format!("锁错误: {}", e))?;
        *cache = Some(cached_data.clone());
    }

    Ok(cached_data)
}

#[tauri::command]
async fn fetch_platform(name: String) -> Result<PlatformData, String> {
    let configs = get_platform_configs();
    let config = configs
        .iter()
        .find(|c| c.name == name)
        .ok_or_else(|| format!("未知平台: {}", name))?;

    let items = fetch_single_platform(config).await?;

    Ok(PlatformData {
        name: config.name.clone(),
        display_name: config.display_name.clone(),
        icon: config.icon.clone(),
        category: config.category.clone(),
        description: config.description.clone(),
        source: "orz.ai".into(),
        entries: items,
    })
}

#[tauri::command]
fn get_cached_data(state: State<'_, AppState>) -> Result<Option<CachedData>, String> {
    let cache = state.cached.lock().map_err(|e| format!("锁错误: {}", e))?;
    Ok(cache.clone())
}

#[tauri::command]
fn get_platform_list() -> Vec<PlatformConfig> {
    get_platform_configs()
}

// ===== App Entry =====

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(AppState {
            cached: Mutex::new(None),
        })
        .invoke_handler(tauri::generate_handler![
            fetch_all_platforms,
            fetch_platform,
            get_cached_data,
            get_platform_list,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
