# MoYoYo.tts 风格 UI 实现文档

> 基于 MoYoYo.tts 参考设计的现代化 UI 布局实现

**实现日期**: 2026-02-03  
**版本**: 1.0  
**状态**: ✅ 已完成

---

## 📋 概述

为 Moxin TTS 应用实现了双 UI 布局系统，允许用户通过 Cargo feature flags 在两种界面风格之间切换：

1. **默认布局** - 原始 MoFA 风格（带系统监控和日志面板）
2. **MoYoYo 布局** - 现代 sidebar 设计（更简洁、更美观）

---

## 🎨 设计特点

### MoYoYo.tts 风格布局

#### 视觉特性

- **左侧 Sidebar** (220px)
  - 深色背景 (`MOYOYO_BG_SIDEBAR`: #1a1a2e)
  - Logo 区域（顶部）
  - 导航菜单（中部）
  - 用户信息（底部）

- **主体内容区**
  - 浅灰背景 (`MOYOYO_BG_PRIMARY`: #f5f5f7)
  - 白色卡片设计（16px 圆角）
  - 移除 MofaHero 状态栏
  - 隐藏右侧日志面板

- **主题色**
  - Primary: `#6366f1` (紫色)
  - Primary Light: `#8789ff`
  - 文字颜色：深灰/中灰/浅灰分级

#### 布局结构

```
TTSScreen (Overlay)
└── app_layout (Right)
    ├── sidebar (220px, dark)
    │   ├── sidebar_header (Logo + Theme Toggle)
    │   ├── sidebar_nav (Navigation Items)
    │   └── sidebar_footer (User Info)
    └── content_wrapper (Fill, light gray bg)
        └── main_content
            └── left_column
                ├── hero (hidden, height: 0)
                ├── page_header (页面标题)
                └── content_area
                    └── cards_container (horizontal)
                        ├── input_section (text input card)
                        └── controls_panel (voice selector)
```

---

## 🛠️ 技术实现

### 文件结构

```
apps/mofa-tts/
├── src/
│   ├── lib.rs                 # 条件编译模块选择
│   ├── screen.rs              # 默认布局
│   └── screen_moyoyo.rs       # MoYoYo.tts 布局 ⭐ 新增
├── Cargo.toml                 # 添加 moyoyo-ui feature

moxin-tts-shell/
└── Cargo.toml                 # Feature 透传配置
```

### 条件编译配置

**apps/mofa-tts/Cargo.toml:**

```toml
[features]
default = []
moyoyo-ui = []
```

**moxin-tts-shell/Cargo.toml:**

```toml
[features]
default = []
moyoyo-ui = ["mofa-tts/moyoyo-ui"]
```

**apps/mofa-tts/src/lib.rs:**

```rust
// Screen modules - conditionally compiled based on features
#[cfg(not(feature = "moyoyo-ui"))]
pub mod screen;

#[cfg(feature = "moyoyo-ui")]
#[path = "screen_moyoyo.rs"]
pub mod screen;
```

### Widget Path 兼容性

为了保持事件处理代码的兼容性，MoYoYo 布局保留了原有的 widget path 结构：

```rust
// 按钮路径保持一致
content_wrapper
    .main_content
    .left_column
    .content_area
    .input_section
    .bottom_bar
    .generate_section
    .generate_btn
```

这意味着所有事件处理代码无需修改即可工作。

---

## 🚀 使用方法

### 运行不同布局

**默认布局（MoFA 风格）:**

```bash
cargo run -p moxin-tts
```

**MoYoYo 布局:**

```bash
cargo run -p moxin-tts --features moyoyo-ui
```

### 编译检查

```bash
# 检查默认布局
cargo check -p moxin-tts

# 检查 MoYoYo 布局
cargo check -p moxin-tts --features moyoyo-ui
```

---

## 📝 主要组件

### Sidebar 导航菜单

```rust
NavItem = <Button> {
    // 悬停和激活状态样式
    draw_bg: {
        instance hover: 0.0
        instance active: 0.0
        // Normal: transparent
        // Hover: rgba(255, 255, 255, 0.08)
        // Active: MOYOYO_PRIMARY
    }
}
```

### 文本输入卡片

- 白色背景，16px 圆角
- 透明输入框背景（文字直接显示在卡片上）
- 底部边框分隔字符计数和生成按钮

### 生成按钮

- 紫色主题色 (`MOYOYO_PRIMARY`)
- 44px 高度，28px 左右内边距
- 10px 圆角
- 悬停时颜色变浅

---

## 🎯 设计决策

### 为什么使用条件编译？

1. **代码分离** - 两种布局完全独立，互不影响
2. **性能优化** - 只编译使用的布局，减少二进制大小
3. **维护性** - 易于分别维护和更新两种布局
4. **灵活性** - 未来可轻松添加更多布局选项

### 为什么保持 Widget Path？

1. **兼容性** - 所有事件处理代码无需修改
2. **稳定性** - 降低引入 bug 的风险
3. **效率** - 快速实现，无需重构大量代码

### 为什么隐藏而不删除某些组件？

```rust
// MofaHero 设置为不可见而非删除
hero = <MofaHero> {
    width: Fill
    height: 0
    visible: false
}
```

原因：

- 保持 widget 树结构完整
- 避免破坏现有引用
- 未来可能需要重新启用

---

## 🔍 关键代码片段

### Sidebar 实现

```rust
sidebar = <View> {
    width: 220, height: Fill
    flow: Down
    spacing: 0

    show_bg: true
    draw_bg: {
        fn pixel(self) -> vec4 {
            return (MOYOYO_BG_SIDEBAR);
        }
    }

    sidebar_header = <View> { /* Logo */ }
    sidebar_nav = <View> { /* Navigation */ }
    sidebar_footer = <View> { /* User Info */ }
}
```

### 卡片样式

```rust
input_section = <RoundedView> {
    width: Fill, height: Fill
    flow: Down
    show_bg: true
    draw_bg: {
        instance dark_mode: 0.0
        border_radius: 16.0
        fn pixel(self) -> vec4 {
            let sdf = Sdf2d::viewport(self.pos * self.rect_size);
            sdf.box(0., 0., self.rect_size.x, self.rect_size.y, self.border_radius);
            let bg = mix((WHITE), (SLATE_800), self.dark_mode);
            sdf.fill(bg);
            return sdf.result;
        }
    }
}
```

---

## ✅ 完成清单

- [x] 创建 `screen_moyoyo.rs` 文件
- [x] 实现 Sidebar 布局（Logo、导航、用户信息）
- [x] 重构主体内容区域（移除 MofaHero、简化布局）
- [x] 应用 MoYoYo.tts 主题色和样式
- [x] 隐藏日志面板和分隔线
- [x] 设置条件编译（feature flags）
- [x] 保持 widget path 兼容性
- [x] 测试两种布局编译和运行
- [x] 中文化按钮文字
- [x] 更新文档

---

## 🔮 未来改进

### 短期

- [ ] 添加主题切换功能（浅色/深色）
- [ ] 优化 Sidebar 动画效果
- [ ] 完善用户信息显示

### 中期

- [ ] 实现 Sidebar 可折叠功能
- [ ] 添加更多导航项（音色库、音色克隆等）
- [ ] 优化卡片阴影效果

### 长期

- [ ] 支持自定义主题色
- [ ] 实现布局切换动画
- [ ] 响应式布局适配

---

## 📚 参考资料

- MoYoYo.tts 项目: `C:\Users\FPG_123\Documents\projects\moxin\MoYoYo.tts`
- Makepad UI 框架: https://github.com/makepad/makepad
- 主题色定义: `mofa-widgets/src/theme.rs`

---

## 🙏 致谢

本实现参考了 MoYoYo.tts 项目的优秀设计，感谢其简洁美观的 UI 启发。
