# 上下文恢复文档 - Moxin TTS项目

> 本文档用于快速恢复工作上下文，继续Moxin TTS独立应用开发

**文档创建时间**: 2026-02-02
**最后更新时间**: 2026-02-03
**文档版本**: 2.0
**当前阶段**: Phase 3 完成（Few-Shot训练功能），Moxin TTS 独立应用可正常运行

---

## 📋 快速恢复检查清单

**在开始工作前，请确认以下内容：**

- [ ] 项目位置：`C:\Users\FPG_123\Documents\projects\moxin\mofa-studio`
- [ ] Git仓库：`https://github.com/alan0x/moxin-tts.git`
- [ ] 当前分支：`main`
- [ ] 已读完整文档（本文档）
- [ ] 理解当前进度和下一步任务
- [ ] 环境配置正常

---

## 🎯 项目概述

### 项目背景

**原始项目**: mofa-studio - 一个包含多个应用的AI桌面平台
**新项目**: Moxin TTS - 从mofa-studio中提取的独立TTS应用

### 核心目标

从mofa-studio多应用平台中提取mofa-tts，创建一个**独立的桌面应用**：
- ✅ 只包含TTS功能（文本转语音、语音克隆）
- ✅ 移除应用切换、sidebar、通用设置等
- ✅ 直接启动到TTS界面
- ✅ 完全独立，可独立发布

### 技术栈

- **UI框架**: Makepad (Rust, GPU加速)
- **TTS引擎**: GPT-SoVITS v2
- **数据流**: Dora (dataflow framework)
- **语言**: Rust (前端) + Python (TTS节点)

---

## 📂 项目结构

### 目录树

```
C:\Users\FPG_123\Documents\projects\moxin\mofa-studio\
├── moxin-tts-shell/          # ⭐ 新创建的独立应用
│   ├── Cargo.toml            # 包配置
│   ├── src/
│   │   ├── main.rs           # 入口（47行）
│   │   └── app.rs            # 应用逻辑（147行）
│   ├── resources/            # 资源目录（待添加）
│   ├── README.md
│   ├── BUILDING.md
│   └── IMPLEMENTATION_SUMMARY.md
│
├── apps/mofa-tts/            # TTS应用逻辑（库）
│   ├── src/
│   │   ├── lib.rs
│   │   ├── screen.rs         # TTS屏幕
│   │   ├── voice_selector.rs
│   │   ├── voice_clone_modal.rs
│   │   └── dora_integration.rs
│   └── Cargo.toml
│
├── mofa-widgets/             # 共享UI组件
├── mofa-ui/                  # 主题和系统监控
├── mofa-dora-bridge/         # Dora集成
│
├── node-hub/                 # Python Dora节点
│   ├── dora-primespeech/     # TTS节点
│   ├── dora-asr/             # ASR节点
│   └── ...
│
├── doc/                      # 📚 文档目录
│   ├── CONTEXT_RESUME.md     # 本文档
│   ├── TTS项目对比分析报告.md
│   ├── mofa-tts-fewshot决策分析.md
│   ├── mofa-tts-fewshot疑问解答.md
│   └── moxin-tts独立应用实施方案.md
│
├── Cargo.toml                # 工作区配置（已更新）
└── README.md
```

### 关键文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| **应用入口** | `moxin-tts-shell/src/main.rs` | CLI参数解析和启动 |
| **应用逻辑** | `moxin-tts-shell/src/app.rs` | 主应用结构 |
| **TTS屏幕** | `apps/mofa-tts/src/screen.rs` | TTS界面实现 |
| **包配置** | `moxin-tts-shell/Cargo.toml` | 依赖和构建配置 |
| **构建指南** | `moxin-tts-shell/BUILDING.md` | 详细构建说明 |
| **实施总结** | `moxin-tts-shell/IMPLEMENTATION_SUMMARY.md` | Phase 1完成情况 |
| **二进制** | `target/release/moxin-tts.exe` | 编译输出 |

---

## ✅ 已完成工作

### Phase 1: 基础搭建 (100%完成)

#### 1.1 创建独立Shell
- ✅ 创建`moxin-tts-shell/`目录结构
- ✅ 编写`main.rs` (CLI入口，47行)
- ✅ 编写`app.rs` (应用逻辑，147行)
- ✅ 配置`Cargo.toml` (44行)

#### 1.2 工作区集成
- ✅ 更新根目录`Cargo.toml`，添加`moxin-tts-shell`到members
- ✅ 配置正确的依赖关系

#### 1.3 编译验证
- ✅ Debug编译成功
- ✅ Release编译成功（34.81秒）
- ✅ 无严重错误，只有2个警告（dead_code）

#### 1.4 文档创建
- ✅ `README.md` - 项目介绍
- ✅ `BUILDING.md` - 构建指南
- ✅ `IMPLEMENTATION_SUMMARY.md` - 实施总结
- ✅ `.gitignore` - Git配置
- ✅ 方案设计文档（在doc/目录）

### 编译输出

```bash
# 成功编译
cargo build --package moxin-tts --release
# Output: Finished `release` profile [optimized] target(s) in 34.81s

# 二进制位置
./target/release/moxin-tts.exe  # Windows
./target/release/moxin-tts      # Unix
```

### Phase 2: Moxin TTS Shell 修复 (100%完成)

#### 2.1 Makepad初始化问题修复
- ✅ 添加`makepad_widgets::live_design(cx)`到LiveRegister
- ✅ 移除重复的`crate::app::live_design(cx)`调用
- ✅ 修复app_main!宏位置（移到模块级别）
- ✅ 移除live_design!中的MofaTheme导入

#### 2.2 编译错误修复
- ✅ 修复window标签显示问题
- ✅ 解决shader解析错误
- ✅ 确认dora-node-api版本（0.3.12）

#### 2.3 运行验证
- ✅ 应用成功启动
- ✅ TTS屏幕正常显示
- ✅ Dora dataflow正常连接

### Phase 3: Few-Shot训练功能集成 (100%完成)

#### 3.1 UI组件实现
- ✅ 添加CloneMode枚举（Express/Pro模式）
- ✅ 实现ModeTabButton组件
- ✅ 添加mode_tabs UI（模式切换标签）
- ✅ 重构body结构：
  - express_mode_content（零样本克隆，3-10秒音频）
  - pro_mode_content（Few-Shot训练，3-10分钟音频）
- ✅ 更新footer为条件按钮组（express_actions/pro_actions）

#### 3.2 训练管理实现
- ✅ 创建`training_manager.rs`
  - TrainingManager：异步训练编排
  - TrainingProgress：进度状态结构
  - TrainingStatus枚举
- ✅ 创建`training_service.py`
  - Python训练服务包装
  - 进度日志输出
  - 与GPT-SoVITS训练脚本集成

#### 3.3 VoiceCloneModal扩展
- ✅ 添加训练相关字段到struct
- ✅ 实现LiveHook trait（初始化TrainingManager）
- ✅ 添加事件处理器：
  - 模式切换（express_tab/pro_tab）
  - 长录音按钮（toggle_training_recording）
  - 训练按钮（start_training/cancel_training）
  - 进度轮询（poll_training_progress）

#### 3.4 新增方法（11个）
- ✅ `switch_to_mode()` - 切换Express/Pro模式
- ✅ `toggle_training_recording()` - 切换长录音状态
- ✅ `start_training_recording()` - 开始长录音（3-10分钟）
- ✅ `stop_training_recording()` - 停止长录音并保存
- ✅ `start_training()` - 启动训练流程
- ✅ `cancel_training()` - 取消训练
- ✅ `poll_training_progress()` - 轮询训练进度
- ✅ `update_training_ui()` - 更新UI进度显示
- ✅ `on_training_completed()` - 训练完成回调
- ✅ `check_gpu_availability()` - GPU检测
- ✅ `add_training_log()` - 添加训练日志

#### 3.5 编译错误修复
- ✅ LiveHook冲突（从derive移除，手动实现）
- ✅ 方法签名修复（添加cx参数）
- ✅ CloneMode所有权（添加Copy trait）
- ✅ log命名冲突（使用::log::）
- ✅ Shader颜色定义（替换为hex值）
- ✅ border_radius shader错误（使用直接值）

#### 3.6 文档创建
- ✅ `FEW_SHOT_UI_IMPLEMENTATION_GUIDE.md` - 完整实施指南
- ✅ `VOICE_CLONE_MODAL_MODIFICATIONS_SUMMARY.md` - 修改总结

---

## 🔑 关键决策记录

### 决策1: 使用方案A（创建新Shell）而非方案B（Feature Flags）

**原因**:
- ✅ 代码独立性：完全独立，不依赖mofa-studio-shell
- ✅ 代码简洁性：约200行 vs 复杂的条件编译
- ✅ 未来扩展性：可独立演进
- ✅ 打包大小：不包含无用代码

**评分**: 方案A 29/30 vs 方案B 17/30

### 决策2: Few-Shot语音克隆使用dora-primespeech

**原因**:
- ✅ dora-primespeech已包含完整的GPT-SoVITS训练工具链
- ✅ 避免重复依赖（MoYoYo.tts核心与dora-primespeech相同）
- ✅ 架构一致（都是Dora节点）
- ⚠️ 定期同步MoYoYo.tts更新以获取新特性

**参考文档**: `doc/mofa-tts-fewshot决策分析.md`

### 决策3: 使用dora-asr而非dora-primespeech内置ASR

**原因**:
- ✅ dora-asr专为实时识别优化
- ✅ dora-primespeech ASR是批处理工具（用于训练数据准备）
- ✅ 两者互补，各司其职

**参考文档**: `doc/mofa-tts-fewshot疑问解答.md`

### 决策4: Git远程仓库更改

**从**: Fork仓库 (mofa-org/mofa-studio)
**到**: 新仓库 (alan0x/moxin-tts)
**原因**: 独立开发，不再作为上游项目的fork

---

## 📊 当前状态

### Git状态

```bash
# 工作目录
C:\Users\FPG_123\Documents\projects\moxin\mofa-studio

# 远程仓库
origin: https://github.com/alan0x/moxin-tts.git

# 当前分支
main

# 未提交的更改
M  Cargo.toml                              # 已修改
?? doc/moxin-tts独立应用实施方案.md         # 新文件
?? moxin-tts-shell/                        # 新目录
```

### 编译状态

```
✅ 编译成功
⚠️ 2个警告（dead_code，可忽略）
✅ 二进制已生成：./target/release/moxin-tts.exe
```

### 功能状态

| 功能 | 状态 | 说明 |
|------|------|------|
| 编译 | ✅ 完成 | Release build成功 |
| 运行 | 🚧 待测试 | 需要运行验证 |
| TTS生成 | 🚧 待测试 | 核心功能 |
| 语音选择 | 🚧 待测试 | 14+预置语音 |
| 零样本克隆 | 🚧 待测试 | 5-10秒音频 |
| Few-shot训练 | ❌ 未实现 | Phase 3任务 |

---

## 🚀 下一步计划

### Phase 2: UI调整和功能验证 (预计0.5-1小时)

#### 2.1 运行测试
```bash
cd "C:\Users\FPG_123\Documents\projects\moxin\mofa-studio"
cargo run -p moxin-tts
```

**验证清单**:
- [ ] 应用成功启动
- [ ] 窗口标题显示："Moxin TTS - Voice Cloning & Text-to-Speech"
- [ ] 窗口大小合适（1200x800）
- [ ] TTS屏幕正常显示
- [ ] 没有sidebar或tabs

#### 2.2 功能测试
- [ ] **语音选择**: 能够选择不同语音
- [ ] **文本输入**: 能够输入文本
- [ ] **TTS生成**: 点击"Generate Speech"生成音频
- [ ] **音频播放**: 能够播放生成的音频
- [ ] **音频下载**: 能够下载音频文件
- [ ] **零样本克隆**: 能够上传/录制音频进行克隆
- [ ] **ASR识别**: 录制音频后能够自动识别文本

#### 2.3 UI调整（如需要）
- [ ] 调整窗口默认大小
- [ ] 优化布局
- [ ] 添加应用图标（可选）
- [ ] 确认暗色模式正常

### Phase 3: 文档和提交 (预计0.5小时)

#### 3.1 更新文档
- [ ] 更新根目录`README.md`
  - 添加Moxin TTS介绍
  - 更新项目结构说明
- [ ] 创建快速开始指南
- [ ] 编写故障排除文档

#### 3.2 Git提交
```bash
# 添加文件
git add Cargo.toml
git add moxin-tts-shell/
git add doc/

# 提交
git commit -m "feat: add moxin-tts standalone application

- Create new moxin-tts-shell binary crate
- Simplified app structure without sidebar and tabs
- Direct display of TTS screen
- Standalone Dora state and app data initialization
- CLI support for log level and dataflow configuration
- Complete build and packaging documentation

This is a standalone TTS application extracted from mofa-studio,
focused solely on voice cloning and text-to-speech functionality.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# 推送
git push origin main
```

### Phase 4: Few-Shot训练功能 (预计3-5小时)

**参考**: `doc/mofa-tts-fewshot决策分析.md` 方案1B

#### 4.1 训练流程设计
- [ ] 设计训练UI流程
- [ ] 音频上传/录制界面
- [ ] 音色命名界面
- [ ] 训练进度显示

#### 4.2 封装训练脚本
- [ ] Rust subprocess调用Python训练脚本
- [ ] 参数传递和配置生成
- [ ] 日志文件解析
- [ ] 训练进度监控

#### 4.3 集成到UI
- [ ] 添加"Few-Shot Clone"按钮
- [ ] 训练完成后刷新语音列表
- [ ] 错误处理和用户提示

---

## 🔧 环境配置

### 开发环境

```
操作系统: Windows
工作目录: C:\Users\FPG_123\Documents\projects\moxin\mofa-studio
Rust版本: 1.70+ (stable)
Python版本: 3.8+
```

### 依赖检查

#### Rust依赖
```bash
# 检查Rust版本
rustc --version

# 更新Rust (如需要)
rustup update

# 检查cargo
cargo --version
```

#### Python依赖
```bash
# 检查dora-primespeech
cd node-hub/dora-primespeech
pip show dora-primespeech

# 检查dora-asr
cd ../dora-asr
pip show dora-asr

# 如果未安装，执行：
pip install -e .
```

### 构建命令

```bash
# 开发构建（快速）
cargo build -p moxin-tts

# Release构建（优化）
cargo build -p moxin-tts --release

# 运行
cargo run -p moxin-tts

# 运行带日志
cargo run -p moxin-tts -- --log-level debug

# 清理
cargo clean
```

---

## 📚 关键参考文档

### 内部文档（doc/目录）

1. **TTS项目对比分析报告.md**
   - MoYoYo.tts vs dora-primespeech对比
   - 功能完整性分析
   - 推荐使用场景

2. **mofa-tts-fewshot决策分析.md**
   - Few-shot实施方案对比
   - 推荐使用dora-primespeech方案1B
   - 详细实施步骤

3. **mofa-tts-fewshot疑问解答.md**
   - 两个项目核心是否相同？（不完全相同但兼容）
   - 为什么使用dora-asr？（实时 vs 批处理）
   - 版本同步策略

4. **moxin-tts独立应用实施方案.md**
   - 完整的方案设计
   - 方案A vs 方案B对比
   - 实施计划和风险评估

### 应用内文档（moxin-tts-shell/）

1. **README.md** - 项目介绍和快速开始
2. **BUILDING.md** - 详细构建指南
3. **IMPLEMENTATION_SUMMARY.md** - Phase 1实施总结

### 外部参考

1. **GPT-SoVITS**: https://github.com/RVC-Boss/GPT-SoVITS
2. **Makepad**: https://github.com/makepad/makepad
3. **Dora**: https://github.com/dora-rs/dora

---

## 🐛 已知问题

### 编译警告

```rust
// moxin-tts-shell/src/app.rs:26
warning: function `get_cli_args` is never used
// 原因: 预留用于未来功能
// 影响: 无，可忽略

// moxin-tts-shell/src/app.rs:68
warning: struct `App` is never constructed
// 原因: Makepad的宏系统会使用，编译器检测不到
// 影响: 无，可忽略
```

### 运行时问题（待验证）

以下问题需要在Phase 2测试时验证：
- [ ] 是否需要手动启动Dora dataflow
- [ ] Python节点是否正确加载
- [ ] 音频设备是否正确初始化
- [ ] 模型文件是否自动下载

---

## 💡 技术要点

### Makepad框架特点

1. **live_design!宏**: 定义UI布局和样式
2. **Widget系统**: 组件化UI
3. **Event驱动**: 通过MatchEvent处理交互
4. **GPU加速**: 高性能渲染

### Dora集成

1. **SharedDoraState**: 共享Dora状态
2. **DataflowExecution**: 数据流执行
3. **Node通信**: 通过Arrow IPC

### 状态管理

```rust
// MofaAppData包含：
- dora_state: Arc<SharedDoraState>  // Dora状态
- theme: MofaTheme                  // 主题配置
- config: AppConfig                 // 应用配置
- registry: Arc<MofaWidgetRegistry> // Widget注册表
```

---

## 🔍 调试技巧

### 查看日志

```bash
# Debug级别日志
cargo run -p moxin-tts -- --log-level debug

# 只看特定模块
RUST_LOG=moxin_tts=debug cargo run -p moxin-tts

# 保存日志到文件
cargo run -p moxin-tts 2>&1 | tee moxin-tts.log
```

### 常见问题排查

#### 应用无法启动
1. 检查Python节点是否安装
2. 检查Dora是否可用
3. 查看日志输出

#### TTS不生成音频
1. 检查dora-primespeech节点状态
2. 验证模型文件是否下载
3. 检查GPU/CPU配置

#### ASR无法识别
1. 检查dora-asr节点状态
2. 验证麦克风权限
3. 检查音频设备配置

---

## 📞 快速联系方式

### 项目信息
- **GitHub**: https://github.com/alan0x/moxin-tts
- **Issues**: https://github.com/alan0x/moxin-tts/issues
- **开发者**: alan0x

### 相关项目
- **上游项目**: https://github.com/mofa-org/mofa-studio
- **GPT-SoVITS**: https://github.com/RVC-Boss/GPT-SoVITS
- **Makepad**: https://github.com/makepad/makepad

---

## 🎯 恢复工作流程

### 标准恢复流程

1. **阅读本文档**（10分钟）
   - 通读完整文档
   - 理解当前状态
   - 确认下一步任务

2. **验证环境**（5分钟）
   ```bash
   cd "C:\Users\FPG_123\Documents\projects\moxin\mofa-studio"
   git status
   git log --oneline -5
   cargo --version
   rustc --version
   ```

3. **重新编译**（2分钟）
   ```bash
   cargo build -p moxin-tts --release
   ```

4. **开始Phase 2**（按计划执行）
   - 运行测试
   - 功能验证
   - 问题修复

### 快速命令参考

```bash
# 项目位置
cd "C:\Users\FPG_123\Documents\projects\moxin\mofa-studio"

# 构建
cargo build -p moxin-tts --release

# 运行
cargo run -p moxin-tts

# 测试运行
cargo run -p moxin-tts -- --log-level debug

# 查看状态
git status
git log --oneline -10

# 查看文档
cat moxin-tts-shell/README.md
cat moxin-tts-shell/IMPLEMENTATION_SUMMARY.md
```

---

## 📝 更新记录

| 日期 | 版本 | 更新内容 | 作者 |
|------|------|---------|------|
| 2026-02-02 | 1.0 | 初始创建，Phase 1完成 | Claude Sonnet 4.5 |

---

## ✅ 最终检查清单

在恢复工作前，确认以下内容：

- [ ] 已完整阅读本文档
- [ ] 理解项目目标和背景
- [ ] 知道当前进度（Phase 1完成）
- [ ] 清楚下一步任务（Phase 2: 功能测试）
- [ ] 环境配置正常
- [ ] 代码可以编译
- [ ] 已阅读相关参考文档
- [ ] 准备好开始工作

---

**祝工作顺利！** 🚀

如有疑问，请参考：
1. 本文档的"关键参考文档"部分
2. `moxin-tts-shell/IMPLEMENTATION_SUMMARY.md`
3. `doc/moxin-tts独立应用实施方案.md`
