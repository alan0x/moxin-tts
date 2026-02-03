# Widget ID 路径映射表

## 旧布局 → 新布局路径映射

### Hero (系统状态栏)
```
旧: content_wrapper.main_content.left_column.hero
新: main_content.content_container.hero
```

### 文本输入区域
```
旧: content_wrapper.main_content.left_column.content_area.input_section.input_container.text_input
新: main_content.content_container.text_input_card.text_input

旧: content_wrapper.main_content.left_column.content_area.input_section.bottom_bar.char_count
新: main_content.content_container.text_input_card.input_footer.char_count

旧: content_wrapper.main_content.left_column.content_area.input_section.bottom_bar.generate_section.generate_btn
新: main_content.content_container.text_input_card.input_footer.generate_btn

旧: content_wrapper.main_content.left_column.content_area.input_section.bottom_bar.generate_section.generate_spinner
新: [移除 - 新UI不使用spinner]
```

### 语音选择器
```
旧: content_wrapper.main_content.left_column.content_area.controls_panel.voice_section.voice_selector
新: main_content.content_container.selectors_row.voice_selector_section.voice_selector_container.voice_selector
```

### 音频播放器（底部栏 → 卡片）
```
旧: content_wrapper.audio_player_bar.*
新: main_content.content_container.audio_player_card.*

旧: content_wrapper.audio_player_bar.voice_info.voice_name_container.current_voice_name
新: [移除 - 新UI不显示当前语音名]

旧: content_wrapper.audio_player_bar.playback_controls.controls_row.play_btn
新: main_content.content_container.audio_player_card.player_controls.play_btn

旧: content_wrapper.audio_player_bar.playback_controls.controls_row.stop_btn
新: [移除 - 新UI只有play/pause]

旧: content_wrapper.audio_player_bar.playback_controls.progress_row.progress_bar_container.progress_bar
新: main_content.content_container.audio_player_card.player_controls.progress_container.progress_bar

旧: content_wrapper.audio_player_bar.playback_controls.progress_row.current_time
新: main_content.content_container.audio_player_card.player_controls.progress_container.time_row.current_time

旧: content_wrapper.audio_player_bar.playback_controls.progress_row.total_time
新: main_content.content_container.audio_player_card.player_controls.progress_container.time_row.total_time

旧: content_wrapper.audio_player_bar.download_section.download_btn
新: main_content.content_container.audio_player_card.player_controls.download_btn
```

### 日志面板（移除）
```
旧: content_wrapper.main_content.log_section.*
新: [完全移除 - 简化的独立应用不需要日志面板]

旧: content_wrapper.main_content.splitter
新: [移除 - 不需要可调整大小的分隔条]
```

### Toast 通知
```
旧: toast_overlay.download_toast.*
新: toast.*
```

### 模态框
```
confirm_delete_modal.* - 保持不变
voice_clone_modal - 保持不变
```

## 需要移除的功能引用

以下功能在新 UI 中不存在，需要注释掉或移除：

1. **日志面板相关**：
   - `update_log_display()`
   - `toggle_log_panel()`
   - `resize_log_panel()`
   - `log_panel_width`
   - `log_panel_collapsed`
   - `splitter_dragging`
   - 所有 `log_section` 引用

2. **Spinner 动画**：
   - `generate_spinner` 相关代码
   - spinner 动画播放逻辑

3. **停止按钮**：
   - `stop_btn` 相关逻辑

4. **语音名称显示**：
   - 播放器栏中的 `current_voice_name` 显示
   - `voice_avatar` 显示

## 简化建议

由于新 UI 大幅简化，建议：

1. **保留 add_log() 方法**，但改为只输出到控制台（用于调试）
2. **移除所有日志面板 UI 更新代码**
3. **简化播放器控制**：只保留播放/暂停，移除停止按钮
4. **移除 Toast overlay wrapper**：Toast 已经在 TTSScreen 的根层级

## 新增功能

新 UI 中需要添加的功能：

1. **语言选择按钮处理**：
   ```rust
   // 处理语言选择按钮点击
   if self.view.button(ids!(main_content.content_container.selectors_row.language_selector_section.language_buttons.lang_zh_btn)).clicked(&actions) {
       // 切换到中文
   }
   ```

2. **音频播放器卡片可见性**：
   ```rust
   // 生成音频后显示播放器卡片
   self.view
       .view(ids!(main_content.content_container.audio_player_card))
       .set_visible(cx, true);
   ```
