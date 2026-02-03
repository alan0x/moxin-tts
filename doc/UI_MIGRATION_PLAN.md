# UI 迁移计划：MoYoYo.tts → mofa-studio

## 📅 创建日期：2026-02-03

## 🎯 目标

将 MoYoYo.tts 的界面设计和交互逻辑迁移到 mofa-studio 项目中。

**第一期目标**：
1. 复刻 MoYoYo.tts 的基本 UI 组件/配色/风格
2. 迁移 TTS 生成部分的 UI

**后续目标**：
- 音色管理界面
- 语音克隆界面

---

## 🎨 MoYoYo.tts UI 设计分析

### 配色方案

#### 浅色主题（Light Theme）
```scss
--bg-primary: #ffffff          // 主背景
--bg-secondary: #f5f7fa        // 次级背景（卡片）
--bg-sidebar: #1a1a2e          // 侧边栏（深蓝黑色）
--text-primary: #303133        // 主文本
--text-secondary: #606266      // 次级文本
--text-muted: #909399          // 弱化文本
--border-color: #dcdfe6        // 边框颜色
--border-color-light: #e4e7ed  // 浅边框
--shadow-color: rgba(0,0,0,0.1)// 阴影

// 品牌色
--primary-color: #6366f1       // 靛蓝色（主品牌色）
--primary-color-light: #818cf8 // 浅品牌色
--primary-color-dark: #4f46e5  // 深品牌色

// 功能色
--success-color: #10b981       // 成功（绿色）
--warning-color: #f59e0b       // 警告（黄色）
--danger-color: #ef4444        // 危险（红色）
--info-color: #3b82f6          // 信息（蓝色）
```

#### 深色主题（Dark Theme）
```scss
--bg-primary: #1a1a1a          // 主背景
--bg-secondary: #252525        // 次级背景
--bg-sidebar: #0f0f1a          // 侧边栏
--text-primary: #e5eaf3        // 主文本
--text-secondary: #a3a6ad      // 次级文本
--text-muted: #73767a          // 弱化文本
--border-color: #4c4d4f        // 边框颜色
--border-color-light: #3a3a3c  // 浅边框
--shadow-color: rgba(0,0,0,0.3)// 阴影
```

### 尺寸规范
```scss
--sidebar-width: 240px         // 侧边栏宽度
--header-height: 60px          // 头部高度
--border-radius: 8px           // 常规圆角
--border-radius-lg: 12px       // 大圆角
```

### 布局结构

```
┌─────────────────────────────────────────┐
│  Sidebar (240px)  │  Main Content       │
│                   │                     │
│  Logo + Theme     │  ┌───────────────┐ │
│                   │  │  Page Title   │ │
│  Navigation:      │  └───────────────┘ │
│  - Text to Speech │                     │
│  - Voice Library  │  ┌───────────────┐ │
│  - Voice Clone    │  │  Selectors    │ │
│                   │  │  (Voice+Lang) │ │
│  User Info        │  └───────────────┘ │
│                   │                     │
│                   │  ┌───────────────┐ │
│                   │  │  Text Input   │ │
│                   │  │  + Generate   │ │
│                   │  └───────────────┘ │
│                   │                     │
│                   │  ┌───────────────┐ │
│                   │  │  Audio Player │ │
│                   │  └───────────────┘ │
└─────────────────────────────────────────┘
```

### TTS 生成界面结构

1. **页面标题**
   - 字体：24px, 粗体
   - 颜色：`--text-primary`

2. **选择器行**
   - 网格布局：2fr（语音选择器） + 1fr（语言选择器）
   - 间距：16px
   - 标签：14px, 中等粗细, `--text-secondary`

3. **文本输入区域**
   - 背景：`--bg-secondary`
   - 圆角：`--border-radius-lg` (12px)
   - 内边距：16px
   - 文本域：10行，无边框，透明背景
   - 底部栏：字符计数 + 生成按钮

4. **音频播放器区域**
   - 背景：`--bg-secondary`
   - 圆角：`--border-radius-lg` (12px)
   - 内边距：20px
   - 组件：播放/暂停按钮 + 进度条 + 时间显示 + 保存按钮

---

## 🔄 Makepad 转换策略

### CSS → Makepad 映射

| CSS 特性 | Makepad 实现 |
|---------|-------------|
| 颜色变量 | `live_design!` 中定义常量 |
| flex 布局 | `flow: Right/Down` |
| grid 布局 | 使用嵌套 `View` + `width` 比例 |
| border-radius | `draw_bg` 中的 `border_radius` |
| padding | View 的 `padding: {left, right, top, bottom}` |
| margin | View 的 `margin: {left, right, top, bottom}` |
| hover 效果 | `draw_bg` 中的 `instance hover` |
| 过渡动画 | `animator` 定义 |
| 阴影 | `draw_bg` shader 中的 `sdf.blur()` |

### 主题切换实现

mofa-studio 当前使用 `dark_mode: 0.0/1.0` 来控制主题：
```rust
draw_bg: {
    instance dark_mode: 0.0
    fn pixel(self) -> vec4 {
        let light_color = vec4(1.0, 1.0, 1.0, 1.0);  // #ffffff
        let dark_color = vec4(0.1, 0.1, 0.1, 1.0);    // #1a1a1a
        return mix(light_color, dark_color, self.dark_mode);
    }
}
```

---

## 📦 实施计划

### Phase 1: 主题色定义（30分钟）

**文件**：`mofa-studio/mofa-widgets/src/theme.rs`

**任务**：
1. 添加 MoYoYo.tts 配色到主题定义
2. 更新现有组件使用新配色

**新增颜色常量**：
```rust
// MoYoYo.tts 浅色主题
MOYOYO_BG_PRIMARY = #ffffff
MOYOYO_BG_SECONDARY = #f5f7fa
MOYOYO_TEXT_PRIMARY = #303133
MOYOYO_TEXT_SECONDARY = #606266
MOYOYO_PRIMARY = #6366f1
MOYOYO_SUCCESS = #10b981
MOYOYO_BORDER = #dcdfe6

// MoYoYo.tts 深色主题
MOYOYO_BG_PRIMARY_DARK = #1a1a1a
MOYOYO_BG_SECONDARY_DARK = #252525
MOYOYO_TEXT_PRIMARY_DARK = #e5eaf3
MOYOYO_TEXT_SECONDARY_DARK = #a3a6ad
MOYOYO_BORDER_DARK = #4c4d4f
```

### Phase 2: 基础 UI 组件（2-3小时）

#### 2.1 卡片组件（Card）
**文件**：新建 `mofa-studio/mofa-widgets/src/card.rs`

**特性**：
- 背景色：`MOYOYO_BG_SECONDARY`（随主题变化）
- 圆角：12px
- 内边距：可配置
- 阴影（可选）

#### 2.2 选择器组件（Selector）
**文件**：新建 `mofa-studio/mofa-widgets/src/selector.rs`

**特性**：
- 下拉列表样式
- 标签 + 选择框组合
- hover 效果
- 支持刷新按钮

#### 2.3 文本输入区组件（TextArea）
**文件**：新建 `mofa-studio/mofa-widgets/src/textarea.rs`

**特性**：
- 多行文本输入
- 字符计数
- 最大长度限制
- 底部操作栏

#### 2.4 音频播放器组件（AudioPlayer）
**文件**：增强现有 `apps/mofa-tts/src/audio_player.rs`

**特性**：
- 播放/暂停按钮（圆形，大尺寸）
- 进度条（可拖动）
- 时间显示（当前/总时长）
- 保存按钮

### Phase 3: TTS 界面重构（2-3小时）

**文件**：`apps/mofa-tts/src/screen.rs`

**任务**：
1. 移除旧的布局结构
2. 应用新的 MoYoYo.tts 布局
3. 使用新的组件和配色
4. 保持现有的 Dora 集成逻辑

**新布局结构**：
```rust
TTSScreen = {
    width: Fill, height: Fill
    flow: Right  // 水平布局

    // 不再需要侧边栏（moxin-tts 是独立应用）

    // 主内容区
    main_content = <View> {
        width: Fill, height: Fill
        flow: Down
        align: {x: 0.5}  // 水平居中
        padding: {left: 24, right: 24, top: 24}

        // 容器（最大宽度 800px）
        content_container = <View> {
            width: 800, height: Fill
            flow: Down
            spacing: 24

            // 页面标题
            page_title = <Label> { text: "Text to Speech" }

            // 选择器行
            selectors_row = <View> {
                width: Fill
                flow: Right
                spacing: 16

                voice_selector = <VoiceSelector> { width: 520 }
                language_selector = <LanguageSelector> { width: 260 }
            }

            // 文本输入卡片
            text_input_card = <Card> {
                textarea = <TextArea> { max_length: 5000 }
                generate_button = <Button> {}
            }

            // 音频播放器卡片（条件显示）
            audio_player_card = <Card> {
                visible: false
                player = <AudioPlayer> {}
            }
        }
    }
}
```

### Phase 4: 细节优化（1-2小时）

1. **动画和过渡**
   - hover 效果
   - 按钮点击反馈
   - 加载状态动画

2. **响应式调整**
   - 小屏幕适配
   - 组件大小调整

3. **可访问性**
   - 键盘导航
   - 屏幕阅读器支持

---

## 🔍 当前 mofa-studio UI 分析

### 现有组件位置
- **TTS 界面**：`apps/mofa-tts/src/screen.rs` (800+ 行)
- **语音选择器**：`apps/mofa-tts/src/voice_selector.rs`
- **克隆模态框**：`apps/mofa-tts/src/voice_clone_modal.rs`
- **音频播放器**：`apps/mofa-tts/src/audio_player.rs`
- **主题**：`mofa-studio/mofa-widgets/src/theme.rs`

### 需要保留的逻辑
- Dora dataflow 集成
- 语音数据管理
- TTS 生成流程
- 音频录制功能

### 需要更新的部分
- 布局结构（改为 MoYoYo.tts 风格）
- 配色方案（应用新主题）
- 组件样式（卡片式设计）
- 间距和尺寸（统一规范）

---

## 📊 工作量评估

| 阶段 | 任务 | 预计时间 |
|------|------|---------|
| Phase 1 | 主题色定义 | 30 分钟 |
| Phase 2 | 基础 UI 组件 | 2-3 小时 |
| Phase 3 | TTS 界面重构 | 2-3 小时 |
| Phase 4 | 细节优化 | 1-2 小时 |
| **总计** | | **6-9 小时** |

---

## 🚀 开始实施

### 第一步：主题色定义

修改 `mofa-studio/mofa-widgets/src/theme.rs`，添加 MoYoYo.tts 配色方案。

### 第二步：创建基础组件

按优先级创建：
1. Card 组件（最基础）
2. TextArea 组件（文本输入）
3. Selector 组件（语音选择）
4. AudioPlayer 组件（音频播放）

### 第三步：重构 TTS 界面

使用新组件和布局重构 `screen.rs`。

---

## 📝 注意事项

1. **保持现有功能**：迁移时不能破坏现有的 TTS 生成功能
2. **渐进式迁移**：逐步替换，确保每步都可编译运行
3. **代码复用**：尽量复用现有的业务逻辑代码
4. **测试验证**：每个阶段完成后进行功能测试

---

## 📚 参考资料

- MoYoYo.tts 源码：`C:\Users\FPG_123\Documents\projects\moxin\MoYoYo.tts`
- Makepad 文档：https://github.com/makepad/makepad
- mofa-studio 现有实现：`apps/mofa-tts/src/`

---

**文档版本**：1.0
**创建者**：Claude Sonnet 4.5
**最后更新**：2026-02-03
