# Moxin-TTS 独立桌面应用实施方案

## 需求分析

### 目标
从当前的mofa-studio多应用平台中，提取mofa-tts创建一个独立的桌面应用moxin-tts。

### 需求清单
- ✅ 只包含mofa-tts应用功能
- ✅ 移除所有其他应用（mofa-fm, mofa-debate, mofa-settings等）
- ✅ 移除应用切换功能（sidebar/tabs）
- ✅ 移除通用的设置/profile页面
- ✅ 直接启动到TTS界面
- ✅ 保留必要的基础设施（mofa-ui, mofa-widgets, mofa-dora-bridge）
- ✅ 应用名称和品牌更新为Moxin TTS

### 不改变的部分
- ✅ TTS核心功能（文本转语音、音色选择、零样本克隆）
- ✅ Dora集成（dora-primespeech, dora-asr）
- ✅ 音频播放和录制
- ✅ 语音持久化

---

## 当前架构分析

### 项目结构
```
mofa-studio/
├── mofa-studio-shell/          # 主Shell（包含sidebar、app切换）
│   ├── src/
│   │   ├── main.rs             # 入口：解析CLI参数
│   │   ├── app.rs              # App结构：sidebar + dashboard + 多app
│   │   └── widgets/
│   │       ├── sidebar.rs      # 侧边栏（app切换）
│   │       ├── dashboard.rs    # Dashboard（显示当前app）
│   │       └── tabs.rs         # 标签页（Profile/Settings）
│   └── Cargo.toml              # Features: mofa-fm, mofa-settings, mofa-tts...
│
├── mofa-widgets/               # ✅ 保留（共享组件）
├── mofa-ui/                    # ✅ 保留（主题、系统监控）
├── mofa-dora-bridge/           # ✅ 保留（Dora集成）
│
└── apps/
    ├── mofa-tts/               # ✅ 核心目标
    ├── mofa-fm/                # ❌ 移除
    ├── mofa-debate/            # ❌ 移除
    └── mofa-settings/          # ❌ 移除
```

### 依赖关系
```
mofa-studio-shell
├── mofa-widgets (共享UI组件)
├── mofa-ui (主题、日志、系统监控)
├── mofa-dora-bridge (Dora集成)
├── mofa-tts (TTS应用)
├── mofa-fm (optional)
├── mofa-settings (optional)
└── mofa-debate (optional)

mofa-tts
├── mofa-widgets
├── mofa-ui
└── mofa-dora-bridge
```

### 关键发现
1. **mofa-tts已经是独立的库crate** - 不依赖其他apps
2. **mofa-studio-shell使用feature flags** - 可选择性编译apps
3. **基础设施完整** - mofa-widgets/mofa-ui/mofa-dora-bridge都是独立的
4. **插件系统清晰** - MofaApp trait定义了app接口

---

## 实施方案

### 方案A: 创建新的独立Shell ⭐⭐⭐⭐⭐ (推荐)

**概述**: 创建`moxin-tts-shell/`作为新的独立应用入口，只包含TTS功能。

#### 优势
- ✅ 完全独立，不依赖mofa-studio-shell
- ✅ 代码简洁，没有多余的app切换逻辑
- ✅ 未来可以独立演进
- ✅ 打包更小（不包含其他apps）
- ✅ 品牌独立（Moxin TTS vs MoFA Studio）

#### 劣势
- ⚠️ 需要创建新的shell代码（但很简单，约200行）
- ⚠️ 需要维护两套shell（如果继续维护mofa-studio）

#### 实施步骤

##### 1. 创建新的Shell目录结构
```
mofa-studio/
├── moxin-tts-shell/              # 新建独立Shell
│   ├── Cargo.toml
│   ├── src/
│   │   ├── main.rs               # 简化的入口
│   │   └── app.rs                # 简化的App（只有TTS）
│   └── resources/
│       ├── fonts/
│       ├── icons/
│       └── moxin-logo.png
└── apps/mofa-tts/                # 保持不变
```

##### 2. Cargo.toml配置
```toml
[package]
name = "moxin-tts"
version = "0.1.0"
edition = "2021"
license = "Apache-2.0"

[dependencies]
makepad-widgets.workspace = true
mofa-widgets = { path = "../mofa-widgets" }
mofa-ui = { path = "../mofa-ui" }
mofa-dora-bridge = { path = "../mofa-dora-bridge" }
mofa-tts = { path = "../apps/mofa-tts" }

# Audio
cpal.workspace = true

# Async runtime
tokio.workspace = true

# Utilities
parking_lot.workspace = true
serde.workspace = true
serde_json.workspace = true
log.workspace = true
env_logger.workspace = true
dirs.workspace = true
sysinfo.workspace = true
ctrlc = "3.4"

# CLI (可选，如果需要命令行参数)
clap = { version = "4.4", features = ["derive"] }

[[bin]]
name = "moxin-tts"
path = "src/main.rs"
```

##### 3. main.rs (简化版本)
```rust
//! Moxin TTS - Standalone TTS Application
//!
//! A standalone desktop application for text-to-speech with voice cloning,
//! powered by GPT-SoVITS.

mod app;

use clap::Parser;

#[derive(Parser, Debug, Default)]
#[command(name = "moxin-tts")]
#[command(about = "Moxin TTS - Voice Cloning & Text-to-Speech")]
struct Args {
    /// Log level (trace, debug, info, warn, error)
    #[arg(short, long, default_value = "info")]
    log_level: String,

    /// Dora dataflow YAML file path
    #[arg(short, long)]
    dataflow: Option<String>,
}

fn main() {
    // Parse CLI arguments
    let args = Args::parse();

    // Configure logging
    env_logger::Builder::from_env(
        env_logger::Env::default().default_filter_or(&args.log_level),
    )
    .init();

    log::info!("Starting Moxin TTS");

    if let Some(ref dataflow) = args.dataflow {
        log::info!("Using dataflow: {}", dataflow);
    }

    // Store args for app access (if needed)
    app::set_cli_args(args);

    // Start the application
    app::app_main();
}
```

##### 4. app.rs (简化版本)
```rust
//! Moxin TTS App - Main application
//!
//! This is a simplified shell that directly shows the TTS screen
//! without sidebar, tabs, or app switching.

use makepad_widgets::*;
use mofa_dora_bridge::SharedDoraState;
use mofa_ui::{MofaAppData, MofaTheme};
use mofa_tts::{MoFaTTSApp, TTSScreenWidgetRefExt};
use mofa_widgets::MofaApp;

use std::sync::OnceLock;
use crate::Args;

// ============================================================================
// CLI ARGS STORAGE
// ============================================================================

static CLI_ARGS: OnceLock<Args> = OnceLock::new();

pub fn set_cli_args(args: Args) {
    CLI_ARGS.set(args).ok();
}

pub fn get_cli_args() -> &'static Args {
    CLI_ARGS.get_or_init(Args::default)
}

// ============================================================================
// UI DEFINITIONS
// ============================================================================

live_design! {
    use link::theme::*;
    use link::shaders::*;
    use link::widgets::*;

    use mofa_widgets::theme::DARK_BG;
    use mofa_ui::MofaTheme;

    // Import TTS screen
    use mofa_tts::screen::TTSScreen;

    // ========================================================================
    // App Window - Simplified (no sidebar, no tabs)
    // ========================================================================

    App = {{App}} {
        ui: <Window> {
            window: {
                title: "Moxin TTS - Voice Cloning & Text-to-Speech"
                inner_size: vec2(1200, 800)
            }
            pass: { clear_color: (DARK_BG) }

            // Direct TTS screen (no wrapper, no sidebar)
            tts_screen = <TTSScreen> {}
        }
    }
}

// ============================================================================
// APP STRUCT
// ============================================================================

#[derive(Live, LiveHook)]
pub struct App {
    #[live]
    ui: WidgetRef,

    #[rust]
    app_data: Option<MofaAppData>,
}

impl LiveRegister for App {
    fn live_register(cx: &mut Cx) {
        // Register theme
        mofa_ui::live_design(cx);

        // Register TTS app
        MoFaTTSApp::live_design(cx);

        // Register this app
        crate::app::live_design(cx);
    }
}

impl AppMain for App {
    fn handle_event(&mut self, cx: &mut Cx, event: &Event) {
        self.ui.handle_event(cx, event, &mut Scope::empty());
        self.match_event(cx, event);
    }
}

impl MatchEvent for App {
    fn handle_startup(&mut self, cx: &mut Cx) {
        log::info!("Moxin TTS application started");

        // Initialize app data
        let app_data = MofaAppData::new();

        // Initialize Dora state
        let dora_state = SharedDoraState::new();

        // Start Dora dataflow if specified
        if let Some(dataflow_path) = &get_cli_args().dataflow {
            log::info!("Starting Dora dataflow: {}", dataflow_path);
            // TODO: Start dataflow
        }

        self.app_data = Some(app_data);
    }

    fn handle_shutdown(&mut self, _cx: &mut Cx) {
        log::info!("Moxin TTS application shutting down");
    }
}

impl App {
    // No additional methods needed for simplified app
}

// ============================================================================
// APP ENTRY POINT
// ============================================================================

pub fn app_main() {
    let app = app_main_with_args! {
        App,
        makepad_widgets,
    };
    app.run();
}
```

##### 5. 更新工作区Cargo.toml
```toml
# 在根目录的Cargo.toml中添加
[workspace]
members = [
    "mofa-studio-shell",
    "moxin-tts-shell",        # 新增
    "mofa-widgets",
    "mofa-ui",
    "mofa-dora-bridge",
    "apps/*",
]

# 可选：设置默认运行的应用
[workspace.metadata]
default-members = ["moxin-tts-shell"]
```

##### 6. 构建和运行
```bash
# 构建moxin-tts
cargo build --package moxin-tts --release

# 运行
cargo run --package moxin-tts

# 或者
./target/release/moxin-tts

# 带参数运行
./target/release/moxin-tts --log-level debug --dataflow path/to/dataflow.yml
```

---

### 方案B: 使用Feature Flags简化Shell ⭐⭐⭐

**概述**: 在mofa-studio-shell中添加"standalone-tts"模式，隐藏sidebar和其他apps。

#### 优势
- ✅ 代码复用（使用现有shell）
- ✅ 维护成本低（一套代码）

#### 劣势
- ❌ 代码复杂（需要条件编译）
- ❌ 不够独立（仍然依赖mofa-studio-shell）
- ❌ 打包包含无用代码

#### 实施（如果选择此方案）
```toml
# mofa-studio-shell/Cargo.toml
[features]
default = ["mofa-fm", "mofa-settings", "mofa-debate", "mofa-tts"]
standalone-tts = ["mofa-tts"]  # 只启用TTS
```

```rust
// app.rs
#[cfg(feature = "standalone-tts")]
fn show_sidebar() -> bool { false }

#[cfg(not(feature = "standalone-tts"))]
fn show_sidebar() -> bool { true }
```

**不推荐原因**: 代码会变得复杂，充满条件编译。

---

## 推荐方案对比

| 维度 | 方案A (新Shell) | 方案B (Feature Flags) |
|------|----------------|---------------------|
| **代码独立性** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **代码简洁性** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **维护成本** | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **打包大小** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **未来扩展性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **实施难度** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **总分** | 29/30 | 17/30 |

---

## 推荐实施计划

### 🏆 推荐：方案A - 创建新的独立Shell

#### Phase 1: 基础搭建 (1-2小时)

**任务清单**:
- [ ] 创建`moxin-tts-shell/`目录
- [ ] 编写`Cargo.toml`
- [ ] 实现简化的`main.rs`
- [ ] 实现简化的`app.rs`
- [ ] 更新工作区`Cargo.toml`

**验证**:
```bash
cargo build --package moxin-tts
cargo run --package moxin-tts
```

#### Phase 2: UI调整 (0.5-1小时)

**任务清单**:
- [ ] 更新窗口标题为"Moxin TTS"
- [ ] 调整窗口默认大小
- [ ] 确保TTS屏幕填满整个窗口
- [ ] 测试响应式布局

#### Phase 3: 功能验证 (0.5-1小时)

**任务清单**:
- [ ] 测试TTS生成功能
- [ ] 测试音色选择
- [ ] 测试零样本克隆
- [ ] 测试音频播放
- [ ] 测试Dora集成

#### Phase 4: 打包和文档 (1小时)

**任务清单**:
- [ ] 添加应用图标
- [ ] 编写README.md
- [ ] 创建发布脚本
- [ ] 测试打包

**预计总时间**: 3-5小时

---

## 文件清单

### 新增文件
```
moxin-tts-shell/
├── Cargo.toml                  # 新建
├── src/
│   ├── main.rs                 # 新建 (~50行)
│   └── app.rs                  # 新建 (~150行)
└── resources/
    ├── fonts/                  # 复制自mofa-studio-shell
    ├── icons/                  # 复制自mofa-studio-shell
    └── moxin-logo.png         # 新增应用图标
```

### 修改文件
```
Cargo.toml                      # 更新workspace members
```

### 保持不变
```
mofa-widgets/                   # 不变
mofa-ui/                        # 不变
mofa-dora-bridge/               # 不变
apps/mofa-tts/                  # 不变
node-hub/                       # 不变
```

---

## 风险评估

### 低风险 ✅
- **基础设施完整**: mofa-tts不依赖其他apps
- **插件系统成熟**: MofaApp trait设计良好
- **代码量小**: 只需约200行新代码

### 中风险 ⚠️
- **资源文件**: 需要复制fonts/icons（可共享）
- **Dora启动**: 需要验证独立应用中的Dora启动流程

### 缓解措施
```bash
# 共享资源文件（软链接或相对路径）
moxin-tts-shell/resources -> ../mofa-studio-shell/resources
```

---

## 后续规划

### Short-term (完成独立应用后)
1. **Few-shot训练功能** - 按之前的决策分析实施
2. **用户反馈** - 收集使用体验
3. **Bug修复** - 稳定性改进

### Mid-term (1-3个月)
1. **用户系统** - 添加登录/注册
2. **Profile页面** - Moxin TTS自己的用户资料页
3. **云端同步** - 音色云端存储

### Long-term (3个月+)
1. **商业化** - 付费功能
2. **跨平台** - macOS/Linux支持
3. **移动端** - iOS/Android应用

---

## 命名和品牌

### 应用名称
- **技术名称**: `moxin-tts`
- **显示名称**: "Moxin TTS"
- **完整标题**: "Moxin TTS - Voice Cloning & Text-to-Speech"

### 包名和标识
```toml
[package]
name = "moxin-tts"

[workspace.package]
version = "0.1.0"
edition = "2021"
license = "Apache-2.0"
```

### 窗口标题
```rust
window: {
    title: "Moxin TTS - Voice Cloning & Text-to-Speech"
    inner_size: vec2(1200, 800)
}
```

---

## 总结

### ✅ 推荐实施方案A

**理由**:
1. **完全独立** - 不依赖mofa-studio复杂的shell
2. **代码简洁** - 只有200行核心代码
3. **易于维护** - 没有条件编译的复杂性
4. **未来独立** - 可以独立演进和发布
5. **品牌独立** - Moxin TTS作为独立产品

**工作量**: 3-5小时即可完成基础版本

**风险**: 低（基础设施完整，依赖清晰）

**建议**: 立即开始实施，先完成Phase 1建立基础，然后逐步完善。

---

**生成时间**: 2026-02-02
**文档作者**: Claude Sonnet 4.5
**项目**: Moxin TTS独立应用
