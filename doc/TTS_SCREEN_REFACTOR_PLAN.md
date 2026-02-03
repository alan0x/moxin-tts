# TTS Screen 重构方案

## 当前结构分析

### 布局结构
```
TTSScreen (Overlay)
└── content_wrapper
    ├── main_content (横向布局)
    │   ├── left_column
    │   │   ├── hero (MofaHero - 系统状态)
    │   │   └── content_area (横向)
    │   │       ├── input_section (文本输入)
    │   │       └── controls_panel (语音选择器, 280px 宽)
    │   ├── splitter (可拖动分隔条)
    │   └── log_section (系统日志, 300px 宽)
    └── audio_player_bar (底部播放器栏, 90px 高)
```

### 关键功能
1. **MofaHero**: 系统状态（Dataflow、CPU、Memory、GPU、VRAM）
2. **文本输入**: TextInput 组件，支持多行输入
3. **语音选择器**: VoiceSelector 组件，显示预置和自定义语音
4. **音频播放器**: 底部播放器栏，显示播放进度
5. **日志面板**: 右侧可调整大小的日志显示
6. **模态框**:
   - VoiceCloneModal: 语音克隆
   - ConfirmDeleteModal: 删除确认
   - Toast: 成功提示

## MoYoYo.tts 目标结构

### 布局结构
```
TTSScreen
└── main_content (居中)
    └── content_container (最大宽度 800px)
        ├── page_title "Text to Speech"
        ├── selectors_row (横向)
        │   ├── voice_selector (2/3 宽度)
        │   └── language_selector (1/3 宽度)
        ├── text_input_card (Card)
        │   ├── TextArea
        │   └── footer (字符计数 + Generate 按钮)
        └── audio_player_card (Card, 条件显示)
            └── AudioPlayer
```

### 简化点
1. **移除日志面板**: moxin-tts 是独立应用，不需要复杂的调试界面
2. **简化布局**: 单列居中布局，不需要可调整大小的面板
3. **保留核心功能**: MofaHero、文本输入、语音选择、音频播放
4. **卡片式设计**: 使用 Card 组件，更现代的外观

## 重构步骤

### Step 1: 保留现有功能代码
- Rust 结构体和业务逻辑保持不变
- 保留所有 Dora 集成代码
- 保留所有事件处理逻辑

### Step 2: 简化 live_design! UI 定义
- 替换复杂的三栏布局为单列布局
- 使用 Card 组件替代 RoundedView
- 应用 MoYoYo.tts 配色方案

### Step 3: 语言选择器
- 暂时保留为简单的标签或按钮组
- 后续可以创建专门的 Selector 组件

### Step 4: 音频播放器
- 将底部播放器栏改为卡片式
- 只在生成音频后显示

## 配色映射

| 原配色 | 新配色 (MoYoYo) |
|--------|----------------|
| DARK_BG (#f5f7fa) | MOYOYO_BG_PRIMARY (#ffffff) |
| PANEL_BG (#ffffff) | MOYOYO_BG_SECONDARY (#f5f7fa) |
| PRIMARY_500 (#3b82f6) | MOYOYO_PRIMARY (#6366f1) |
| TEXT_PRIMARY | MOYOYO_TEXT_PRIMARY |
| TEXT_SECONDARY | MOYOYO_TEXT_SECONDARY |

## 实施计划

1. ✅ 备份原始文件
2. 🔄 创建新的 live_design! 布局
3. ⏳ 调整事件处理器路径
4. ⏳ 测试编译
5. ⏳ 功能测试

## 注意事项

- 保持所有 widget ID 路径的一致性
- 确保 dark_mode 切换正常工作
- 保留模态框功能
- 保持与 Dora 的集成
