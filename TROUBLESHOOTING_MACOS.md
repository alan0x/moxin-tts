# macOS 故障排除指南

本文档列出了在 macOS 上运行 Moxin TTS 时的常见问题和解决方案。

## 安装问题

### 1. pyaudio 安装失败

**错误信息**:
```
fatal error: 'portaudio.h' file not found
```

**原因**: 缺少 PortAudio 系统库

**解决方案**:
```bash
# 安装 portaudio
brew install portaudio

# 如果仍然失败，设置编译标志
export CFLAGS="-I$(brew --prefix portaudio)/include"
export LDFLAGS="-L$(brew --prefix portaudio)/lib"
pip install pyaudio
```

### 2. Homebrew 未找到

**错误信息**:
```
brew: command not found
```

**解决方案**:
```bash
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 根据安装提示添加到 PATH（通常是）
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 3. Conda 命令未找到

**错误信息**:
```
conda: command not found
```

**解决方案**:
```bash
# 方案 1: 重启终端

# 方案 2: 手动激活
source ~/miniconda3/bin/activate

# 方案 3: 添加到 shell 配置
echo 'source ~/miniconda3/bin/activate' >> ~/.zshrc
source ~/.zshrc
```

### 4. Rust 编译错误

**错误信息**:
```
error: linker `cc` not found
```

**解决方案**:
```bash
# 安装 Xcode Command Line Tools
xcode-select --install

# 如果已安装但仍有问题，重置
sudo rm -rf /Library/Developer/CommandLineTools
xcode-select --install
```

### 5. NumPy 版本冲突

**错误信息**:
```
ImportError: numpy.core.multiarray failed to import
```

**解决方案**:
```bash
conda activate mofa-studio
pip install numpy==1.26.4 --force-reinstall
```

## 运行时问题

### 6. Dora CLI 未找到

**错误信息**:
```
dora: command not found
```

**解决方案**:
```bash
# 确保 Rust 已安装
cargo --version

# 重新安装 dora-cli
cargo install dora-cli --version 0.3.12 --locked

# 添加到 PATH
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 7. 模型下载失败

**错误信息**:
```
ConnectionError: Failed to download model
```

**解决方案**:
```bash
# 检查网络连接
ping huggingface.co

# 使用代理（如果需要）
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port

# 或使用镜像站点（中国用户）
export HF_ENDPOINT=https://hf-mirror.com
```

### 8. 音频设备错误

**错误信息**:
```
OSError: No Default Input Device Available
```

**解决方案**:
```bash
# 检查音频设备
python -c "import pyaudio; p = pyaudio.PyAudio(); print(p.get_default_input_device_info())"

# 授予麦克风权限
# 系统设置 > 隐私与安全性 > 麦克风 > 允许终端/应用访问
```

### 9. 内存不足

**错误信息**:
```
RuntimeError: [enforce fail at alloc_cpu.cpp:114] . DefaultCPUAllocator: can't allocate memory
```

**解决方案**:
```bash
# 减少批处理大小
export BATCH_SIZE=1

# 关闭其他应用释放内存
```

## TTS 特定问题

### 10. Express Mode 自定义语音 TTS 挂起

**错误现象**:
- 使用 Express Mode 创建的自定义语音生成 TTS 时卡住不动
- 日志显示模型重新加载完成，但推理流程永久阻塞

**根本原因**:
1. Dora 节点 `send_log()` 方法在模型重载后阻塞
2. SDPA 注意力机制在 CNHuBERT 和 BERT 模型中死锁
3. PyTorch 多线程与 Apple Accelerate BLAS 冲突

**解决方案** (已在代码中修复):

1. **日志阻塞修复**:
   - `moyoyo_tts_wrapper_streaming_fix.py` 的 `log()` 方法优先使用 `sys.stderr`
   - 所有 Dora 日志调用包裹在 try/except 中

2. **SDPA 死锁修复**:
   - `moyoyo_tts/feature_extractor/cnhubert.py`: 添加 `attn_implementation="eager"` 到 HubertModel
   - `moyoyo_tts/TTS_infer_pack/TTS.py`: 添加 `attn_implementation="eager"` 到 BERT 模型

3. **多线程冲突修复**:
   - `moyoyo_tts_wrapper_streaming_fix.py`: 模块级别设置 `torch.set_num_threads(1)`
   - 设置环境变量 `OPENBLAS_NUM_THREADS=1`

4. **参考音频自动截断**:
   - `moyoyo_tts/TTS_infer_pack/TTS.py`: 将 >10 秒的参考音频自动截断而非报错

**验证修复**:
```bash
# 重启 Dora 进程以加载最新代码
dora destroy && dora up

# 重新运行应用
cargo run -p moxin-tts
```

### 11. Pro Mode 训练后音色产生噪音/空白

**错误现象**:
- Pro Mode 训练完成，但生成的音频只有噪音或空白
- 训练过程没有错误提示

**根本原因**:
缺少 GPT-SoVITS 预训练基础模型。从零开始训练需要大量数据和时间，3-10 分钟的音频不足以收敛。

**解决方案**:

下载三个预训练模型文件（总计约 410 MB）：

```bash
mkdir -p ~/.dora/models/primespeech/moyoyo/gsv-v2final-pretrained
cd ~/.dora/models/primespeech/moyoyo/gsv-v2final-pretrained

# GPT 预训练模型 (155 MB)
curl -L -o s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt \
  https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch%3D12-step%3D369668.ckpt

# SoVITS 生成器 (~170 MB)
curl -L -o s2G2333k.pth \
  https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/gsv-v2final-pretrained/s2G2333k.pth

# SoVITS 判别器 (~85 MB)
curl -L -o s2D2333k.pth \
  https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/gsv-v2final-pretrained/s2D2333k.pth
```

验证下载：
```bash
ls -lh ~/.dora/models/primespeech/moyoyo/gsv-v2final-pretrained/
# 应该看到三个文件
```

### 12. Pro Mode 训练依赖缺失

**错误信息**:
```
ModuleNotFoundError: No module named 'datasets'
ModuleNotFoundError: No module named 'simplejson'
ModuleNotFoundError: No module named 'tensorboard'
```

**解决方案**:
```bash
conda activate mofa-studio
pip install "datasets<3.0.0" simplejson sortedcontainers tensorboard matplotlib
```

**注意**: `datasets>=3.0.0` 与 `modelscope 1.34.0` 不兼容，必须安装 `datasets<3.0.0`。

### 13. Pro Mode SoVITS 训练使用 CPU 而非 GPU

**现象**:
- GPT 训练使用 MPS (GPU)
- SoVITS 训练使用 CPU，速度较慢

**说明**:
这是正常行为，不是 bug。SoVITS 训练使用 `torch.stft` 产生复数梯度（ComplexFloat），PyTorch MPS 后端不支持复数类型的反向传播。

**影响**:
- GPT 训练（~8 epochs）：GPU 加速，快速
- SoVITS 训练（~15 epochs）：CPU 模式，约 30-90 分钟（取决于音频长度和 CPU 性能）

无需修复，这是 PyTorch MPS 当前的技术限制。

## 性能问题

### 14. TTS 生成速度慢

**Apple Silicon (M1/M2/M3/M4)**:
```bash
# 确认使用 ARM64 原生 Python
python -c "import platform; print(platform.machine())"
# 应输出: arm64

# 确认 PyTorch 使用 Accelerate
python -c "import torch; print(torch.__config__.show())" | grep BLAS
# 应显示: BLAS_INFO=accelerate
```

**Intel Mac**:
```bash
# 使用 CPU 后端
export BACKEND=cpu

# 考虑减少文本长度或分段处理
```

### 15. 应用启动慢

**解决方案**:
```bash
# 使用 release 模式编译
cargo build -p moxin-tts --release
cargo run -p moxin-tts --release

# 清理并重新编译
cargo clean
cargo build -p moxin-tts --release
```

## 环境问题

### 16. Python 版本不匹配

**错误信息**:
```
Python version mismatch: expected 3.12, got 3.9
```

**解决方案**:
```bash
# 删除并重新创建环境
conda deactivate
conda env remove -n mofa-studio
cd models/setup-local-models
./setup_isolated_env.sh
```

### 17. 依赖冲突

**错误信息**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**解决方案**:
```bash
# 创建全新环境
conda deactivate
conda env remove -n mofa-studio
cd models/setup-local-models
./setup_isolated_env.sh
```

### 18. Git LFS 文件未下载

**错误信息**:
```
Error: File is a Git LFS pointer
```

**解决方案**:
```bash
# 安装 Git LFS
brew install git-lfs
git lfs install

# 拉取 LFS 文件
git lfs pull
```

## 诊断工具

### 运行依赖检查

```bash
cd models/setup-local-models

# 检查系统依赖
./check_macos_deps.sh

# 检查 Python 依赖
conda activate mofa-studio
python test_dependencies.py
```

### 查看详细日志

```bash
# Dora 日志
dora logs <dataflow-id>

# Rust 应用日志
RUST_LOG=debug cargo run -p moxin-tts

# Python 节点日志
export LOG_LEVEL=DEBUG
```

### 检查系统信息

```bash
# macOS 版本
sw_vers

# CPU 架构
uname -m

# Python 信息
python --version
python -c "import platform; print(platform.machine())"

# Homebrew 包
brew list

# Conda 环境
conda env list
conda list -n mofa-studio
```

## 获取帮助

如果以上方法都无法解决问题：

1. **收集信息**:
   ```bash
   # 系统信息
   sw_vers > debug_info.txt
   uname -m >> debug_info.txt

   # 依赖信息
   brew list >> debug_info.txt
   conda list -n mofa-studio >> debug_info.txt

   # 错误日志
   # 复制完整的错误信息
   ```

2. **搜索已知问题**:
   - 查看 [GitHub Issues](https://github.com/alan0x/moxin-tts/issues)
   - 搜索错误信息

3. **提交新 Issue**:
   - 包含系统信息
   - 包含完整错误日志
   - 描述重现步骤
   - 附上 `debug_info.txt`

4. **社区支持**:
   - 查看项目文档
   - 参考 [MACOS_SETUP.md](MACOS_SETUP.md)

## 预防措施

### 保持环境清洁

```bash
# 定期更新 Homebrew
brew update && brew upgrade

# 定期清理 Conda 缓存
conda clean --all

# 定期清理 Cargo 缓存
cargo cache --autoclean
```

### 使用虚拟环境

- 始终在 `mofa-studio` 环境中工作
- 不要在 base 环境中安装包
- 每个项目使用独立环境

### 版本管理

- 记录工作的依赖版本
- 使用 `requirements.txt` 或 `environment.yml`
- 定期备份环境配置

---

**最后更新**: 2026-02-14

如有新问题或解决方案，欢迎贡献到本文档！
