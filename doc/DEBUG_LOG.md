# Pro Mode Training Pipeline - Debug Log

Record of all errors encountered while implementing audio file upload for Pro Mode and debugging the few-shot training pipeline.

---

## Error 1: Makepad Label widget does not support `visible` property

**Error message:**
```
no matching field: visible
```

**Cause:**
In Makepad framework, `Label` widgets do not support the `visible` property directly. The `uploaded_file_info` Label was declared with `visible: false` in the `live_design!` macro, which Makepad cannot parse.

**Solution:**
Wrapped the `uploaded_file_info` Label inside a `<View>` container, since `View` supports the `visible` property. Updated runtime code to use `.view()` for `set_visible()` and `.label()` with nested path for `set_text()`.

**File:** `apps/mofa-tts/src/voice_clone_modal.rs`

---

## Error 2: Python backend still enforces 180s minimum duration

**Error message:**
```
Audio too short: 18.7s (minimum: 180.0s)
```

**Cause:**
The Rust UI validation was updated to accept audio >= 10 seconds, but the Python `training_service.py` backend still had `min_duration=180.0` as the default parameter in `validate_audio_file()`.

**Solution:**
Changed the default parameter in `validate_audio_file()` from `180.0` to `10.0` and updated the error message accordingly.

**File:** `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/training_service.py`

---

## Error 3: `slice()` missing 11 required positional arguments

**Error message:**
```
slice() missing 11 required positional arguments: 'inp', 'opt_root', ...
```

**Cause:**
`slice_audio.py` had `print(slice(*sys.argv[1:]))` at module level (line 47-48) without an `if __name__ == "__main__":` guard. When `training_service.py` imported the module via `from moyoyo_tts.tools.slice_audio import slice`, the top-level code executed immediately, calling `slice()` with no arguments from `sys.argv`.

**Solution:**
Wrapped the module-level execution code in an `if __name__ == "__main__":` guard.

**File:** `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/tools/slice_audio.py`

---

## Error 4: `cannot import name 'ALL_ALLOWED_EXTENSIONS' from 'datasets.load'`

**Error message:**
```
ImportError: cannot import name 'ALL_ALLOWED_EXTENSIONS' from 'datasets.load'
```

**Cause:**
`modelscope 1.33.0` was incompatible with `datasets 4.5.0`. The symbol `ALL_ALLOWED_EXTENSIONS` was renamed to `_ALL_ALLOWED_EXTENSIONS` in newer versions of the `datasets` library, but modelscope still referenced the old name.

**Solution:**
Installed `modelscope[framework]` which resolved dependency conflicts and installed `datasets==3.6.0` (within modelscope's required range `>=3.0.0,<=3.6.0`).

**Command:** `pip install modelscope[framework]`

---

## Error 5: `No module named 'simplejson'`

**Error message:**
```
ModuleNotFoundError: No module named 'simplejson'
```

**Cause:**
Missing runtime dependency for modelscope that was not automatically installed.

**Solution:**
```
pip install simplejson
```

---

## Error 6: `No module named 'sortedcontainers'`

**Error message:**
```
ModuleNotFoundError: No module named 'sortedcontainers'
```

**Cause:**
Another missing modelscope runtime dependency.

**Solution:**
```
pip install modelscope[framework]
```
This installed all framework dependencies including `sortedcontainers`.

---

## Error 7: `cnhubert_base_path` is None

**Error message:**
```
TypeError: _path_exists: path should be string, bytes, os.PathLike or integer, not NoneType
```

**Cause:**
The global variable `cnhubert.cnhubert_base_path` was initialized as `None` in `cnhubert.py` and was never set before `get_model()` was called from `training_service.py`. The `get_model()` function passes this path to `os.path.exists()`, which raises TypeError on `None`.

**Solution:**
Added initialization of `cnhubert.cnhubert_base_path` before each `get_model()` call in `training_service.py`:
```python
cnhubert.cnhubert_base_path = os.environ.get(
    "cnhubert_base_path",
    os.path.join(get_pretrained_models_dir(), "chinese-hubert-base")
)
```

**File:** `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/training_service.py`

---

## Error 8: Pretrained model paths resolve to nonexistent relative paths

**Error message:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'moyoyo_tts/pretrained_models/chinese-hubert-base'
```

**Cause:**
Model paths were hardcoded as relative paths (e.g., `moyoyo_tts/pretrained_models/chinese-hubert-base`), but the Python training process inherits the application's working directory, not `dora_primespeech/`. The actual pretrained models are stored at `~/.dora/models/primespeech/moyoyo/`.

**Solution:**
Added a `get_pretrained_models_dir()` helper function that resolves the model directory from `$PRIMESPEECH_MODEL_DIR` env var or falls back to `~/.dora/models/primespeech/moyoyo/`. Updated all model path references (chinese-hubert-base, pretrained GPT, pretrained SoVITS) to use this helper.

**File:** `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/training_service.py`

---

## Error 9: `No valid training data generated` (HuBERT API misuse)

**Error message:**
```
No valid training data generated for GPT training
```
(with per-segment errors hidden in tracebacks)

**Cause:**
The code called `ssl_model.model(audio_tensor)` directly, bypassing `Wav2Vec2FeatureExtractor` preprocessing. Also tried `ssl_model.extract_features()` which doesn't exist on the `CNHubert` class. The `Wav2Vec2FeatureExtractor` expects numpy arrays, not CUDA/half-precision tensors.

**Solution:**
Separated the feature extraction into two steps:
1. `ssl_model.feature_extractor(numpy_audio, ...)` — preprocesses raw audio (numpy array)
2. `ssl_model.model(input_tensor)` — runs the HuBERT model on preprocessed tensor

**File:** `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/training_service.py`

---

## Error 10: `chinese-roberta-wwm-ext-large` path not found

**Error message:**
```
Incorrect path_or_model_id: 'moyoyo_tts/pretrained_models/chinese-roberta-wwm-ext-large'
```

**Cause:**
`chinese2.py` had a hardcoded relative path for the BERT model used by G2PW (grapheme-to-phoneme). Same root cause as Error 8 — relative path doesn't resolve from the application's working directory.

**Solution:**
Updated `chinese2.py` to resolve the BERT model path via `PRIMESPEECH_MODEL_DIR` env var or default to `~/.dora/models/primespeech/moyoyo/chinese-roberta-wwm-ext-large`.

**File:** `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/text/chinese2.py`

---

## Error 11: `cleaned_text_to_sequence()` argument count mismatch

**Error message:**
```
TypeError: cleaned_text_to_sequence() takes from 1 to 2 positional arguments but 3 were given
```

**Cause:**
Code called `cleaned_text_to_sequence(norm_text, language, "v2")` — wrong function. `cleaned_text_to_sequence(cleaned_text, version=None)` only accepts 1-2 arguments. The correct function for text-to-phoneme conversion with language parameter is `clean_text(norm_text, language, "v2")` which returns `(phones, word2ph, norm_text)`.

**Solution:**
Changed the call from `cleaned_text_to_sequence(norm_text, language, "v2")` to `clean_text(norm_text, language, "v2")` and properly unpacked the tuple return value.

**File:** `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/training_service.py`

---

## Error 12: `'tuple' object has no attribute 'replace'`

**Error message:**
```
AttributeError: 'tuple' object has no attribute 'replace'
```

**Cause:**
`clean_text()` was called twice in sequence. The first call `norm_text = clean_text(norm_text, "zh")` assigned the tuple return value `(phones, word2ph, norm_text)` back to the variable `norm_text`. The second call then tried to process `norm_text` (now a tuple) as a string, calling `.replace()` on it.

**Solution:**
Removed the redundant first `clean_text` call. Kept only the single correct call: `phones, word2ph, norm_text = clean_text(norm_text, language, "v2")`.

**File:** `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/training_service.py`

---

## Error 13: `KeyError: 'hidden_dim'`

**Error message:**
```
KeyError: 'hidden_dim'
```

**Cause:**
`generate_gpt_config()` used incorrect field names for the GPT model configuration. It used generic names like `hidden_size`, `num_layers`, `num_heads`, but the `Text2SemanticDecoder` model class expects GPT-SoVITS-specific field names.

**Wrong fields:** `hidden_size`, `num_layers`, `num_heads`
**Correct fields:** `hidden_dim`, `embedding_dim`, `head`, `n_layer`, `vocab_size`, `phoneme_vocab_size`, `EOS`, `dropout`

**Solution:**
Updated the model config section in `generate_gpt_config()` to use correct field names and GPT-SoVITS v2 default values:
```python
"model": {
    "hidden_dim": 512,
    "embedding_dim": 512,
    "head": 8,
    "n_layer": 12,
    "vocab_size": 1025,
    "phoneme_vocab_size": 512,
    "EOS": 1024,
    "dropout": 0.0,
}
```

**File:** `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/training_service.py`

---

## Error 14: Semantic tokens are floats, not integers

**Error message:**
```
ValueError: invalid literal for int() with base 10: '-0.0107'
```

**Cause:**
The semantic token extraction in `extract_features_for_gpt_training()` was producing float values (raw HuBERT hidden state means via `codes.mean(axis=1)`) instead of integer codebook indices (0-1024). The GPT training dataset loader calls `int(idx)` on each token, which fails on float strings.

GPT-SoVITS requires discrete codebook tokens produced by the SoVITS VQ (Vector Quantization) model, not continuous features.

**Solution:**
Load a pretrained SoVITS model and use its VQ quantizer to convert continuous HuBERT features into discrete integer codebook tokens:
```python
from moyoyo_tts.module.models import SynthesizerTrn

# Load pretrained SoVITS model
sovits_model = SynthesizerTrn(...)
sovits_model.load_state_dict(checkpoint["weight"])

# Quantize: continuous features -> discrete tokens
ssl_content = ssl_model.model(input_values).last_hidden_state.transpose(1, 2)
codes = sovits_model.extract_latent(ssl_content)  # returns integer indices
semantic_tokens = codes[0, 0, :].tolist()  # list of ints
```

**File:** `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/training_service.py`

---

## Error 14a: SoVITS pretrained model path wrong (Error 14 fix was incomplete)

**Error message:**
```
FileNotFoundError: No SoVITS weights found in ~/.dora/models/primespeech/moyoyo/SoVITS_weights
```
(or silently fell back to old code path producing float tokens)

**Cause:**
The Error 14 fix loaded the SoVITS VQ model from `SoVITS_weights/` directory, which is the *output* directory for trained models. The pretrained SoVITS model needed for quantization is actually at `gsv-v2final-pretrained/s2G2333k.pth` — the same pretrained model referenced elsewhere in the code (line 246).

**Solution:**
Changed the SoVITS model path from:
```python
sovits_weights_dir = os.path.join(models_dir, "SoVITS_weights")
sovits_files = [f for f in os.listdir(sovits_weights_dir) if f.endswith('.pth')]
sovits_path = os.path.join(sovits_weights_dir, sovits_files[0])
```
to:
```python
sovits_path = os.path.join(models_dir, "gsv-v2final-pretrained", "s2G2333k.pth")
```

**File:** `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/training_service.py`

---

## Error 15: `cannot import name 'DictToAttrRecursive' from 'moyoyo_tts.utils'`

**Error message:**
```
ImportError: cannot import name 'DictToAttrRecursive' from 'moyoyo_tts.utils'
```

**Cause:**
`DictToAttrRecursive` was never defined in `moyoyo_tts/utils.py`. It's defined locally in `inference_webui.py`, `onnx_export.py`, and `export_torch_script.py`, but never in a shared module.

**Solution:**
Defined `DictToAttrRecursive` class directly in `training_service.py` at module level, avoiding importing from `inference_webui.py` which would pull in `gradio` and other heavy dependencies.

**File:** `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/training_service.py`

---

## Error 16: `ZeroDivisionError: division by zero` in dataset init_batch

**Error message:**
```
ZeroDivisionError: division by zero
  File "...dataset.py", line 190, in init_batch
    for _ in range(max(2, int(min_num / leng))):
```

**Cause (two issues):**

1. **phoneme.txt wrong column order**: We wrote `name\tlanguage\ttext\tphones` but `dataset.py` expects `name\tphones\tword2ph\ttext`. This caused `phoneme` variable to contain "ZH" (the language code), which failed `cleaned_text_to_sequence()` → every item was skipped → `leng = 0`.

2. **semantic.tsv missing header**: `pd.read_csv()` treats the first line as column headers by default. Without a header row, the first data sample is consumed as column names and lost. With few-shot training (1-2 segments), this can mean 0 data rows.

**Solution:**
1. Fixed phoneme.txt format to `name\tphones\tword2ph\ttext` (matching what `dataset.py` unpacks as `phoneme, word2ph, text`).
2. Added header line `item_name\tsemantic_ids` to semantic.tsv output.

**File:** `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/training_service.py`

---

## Summary

| # | Error | Root Cause Category | File |
|---|-------|-------------------|------|
| 1 | `no matching field: visible` | Makepad framework API | voice_clone_modal.rs |
| 2 | 180s minimum still enforced | Incomplete change propagation | training_service.py |
| 3 | `slice()` missing arguments | Missing `__main__` guard | slice_audio.py |
| 4 | `ALL_ALLOWED_EXTENSIONS` import | Dependency version conflict | pip dependencies |
| 5 | `No module named 'simplejson'` | Missing dependency | pip dependencies |
| 6 | `No module named 'sortedcontainers'` | Missing dependency | pip dependencies |
| 7 | `cnhubert_base_path` is None | Uninitialized global variable | training_service.py |
| 8 | Relative model path not found | Wrong path resolution | training_service.py |
| 9 | No valid training data | Wrong HuBERT API usage | training_service.py |
| 10 | BERT model path not found | Wrong path resolution | chinese2.py |
| 11 | Wrong function signature | API confusion | training_service.py |
| 12 | Tuple treated as string | Redundant function call | training_service.py |
| 13 | Wrong config field names | GPT-SoVITS config mismatch | training_service.py |
| 14 | Float tokens instead of int | Missing VQ quantization step | training_service.py |
| 14a | SoVITS pretrained path wrong | Wrong path (output vs pretrained) | training_service.py |
| 15 | `DictToAttrRecursive` import | Class not in shared module | training_service.py |
| 16 | Division by zero in dataset | Wrong phoneme format + missing TSV header | training_service.py |
| 17 | `KeyError: 'optimizer'` | Missing config section (proactive audit) | training_service.py |
| 17b | SoVITS 2-name2text.txt format | Wrong column order (same as #16) | training_service.py |
| 17c | SoVITS wav files wrong name | `.wav` extension breaks name matching | training_service.py |
| 17d | Missing `save_weight_dir` | SoVITS `savee()` would crash | training_service.py |
| 17e | Missing `logs_s2` directory | SoVITS checkpoint save would fail | training_service.py |
| 17f | `version` env var not set | v2 text processing not activated | training_service.py |
| 17g | SoVITS checkpoint finder | Wrong format (G_*.pth vs savee output) | training_service.py |

## Error 20: `No module named 'matplotlib'`

**Error message:**
```
ModuleNotFoundError: No module named 'matplotlib'
```

**Cause:**
SoVITS training requires matplotlib for plotting spectrograms to TensorBoard visualizations. The `utils.py:128` in `plot_spectrogram_to_numpy()` imports matplotlib lazily, but it wasn't installed in the conda environment.

**Solution:**
```bash
conda activate mofa-studio
conda install matplotlib
```

**File:** conda environment

---

## Error 21: `AttributeError: 'FigureCanvasAgg' object has no attribute 'tostring_rgb'`

**Error message:**
```
AttributeError: 'FigureCanvasAgg' object has no attribute 'tostring_rgb'. Did you mean: 'tostring_argb'?
```

**Cause:**
Matplotlib API breaking change. The `tostring_rgb()` method was deprecated and removed in matplotlib 3.8+. The code was also using deprecated `np.fromstring()`.

Old code:
```python
data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep="")
data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
```

**Solution:**
Updated to modern matplotlib API using `buffer_rgba()` and `np.frombuffer()`:
```python
fig.canvas.draw()
buf = fig.canvas.buffer_rgba()
data = np.frombuffer(buf, dtype=np.uint8)
width, height = fig.canvas.get_width_height()
data = data.reshape((height, width, 4))
# Drop alpha channel to get RGB
data = data[:, :, :3]
```

**Files:**
- `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/utils.py:145` (plot_spectrogram_to_numpy)
- `node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/utils.py:176` (plot_alignment_to_numpy)

---

## Error 22: Trained custom voice sounds identical to doubao (not loading custom models)

**Error:** No error message, but trained custom voice (Pro Mode few-shot training) produces identical output to the doubao pre-built voice, indicating custom GPT and SoVITS models are not being loaded.

**Cause (2 bugs):**

1. **Rust code bug** (`apps/mofa-tts/src/screen_moyoyo.rs:2724`):
   - Only checked for `VoiceSource::Custom` (Express Mode zero-shot cloning)
   - Did NOT check for `VoiceSource::Trained` (Pro Mode few-shot trained models)
   - Trained voices were treated as built-in voices, using format `VOICE:name|text`

2. **Python code missing feature** (`node-hub/dora-primespeech/dora_primespeech/main.py:311-312`):
   - `VOICE:CUSTOM` format hardcoded default model weights:
     ```python
     "gpt_weights": "GPT_weights/doubao-mixed.ckpt",  # Always uses default
     "sovits_weights": "SoVITS_weights/doubao-mixed.pth",  # Always uses default
     ```
   - No format existed to pass custom model paths for trained voices

**Solution:**

1. **Added new `VOICE:TRAINED` format**:
   ```
   VOICE:TRAINED|<gpt_weights>|<sovits_weights>|<ref_audio>|<prompt_text>|<language>|<text>
   ```

2. **Updated Rust code** to detect `VoiceSource::Trained` and use new format:
   ```rust
   if voice.source == crate::voice_data::VoiceSource::Trained {
       if let (Some(gpt_weights), Some(sovits_weights), Some(ref_audio), Some(prompt_text)) = ... {
           format!("VOICE:TRAINED|{}|{}|{}|{}|{}|{}", 
                   gpt_weights, sovits_weights, ref_audio, prompt_text, voice.language, text)
       }
   }
   ```

3. **Updated Python parsing** to handle `VOICE:TRAINED` format and use custom model weights:
   ```python
   if raw_text.startswith(VOICE_TRAINED_PREFIX):
       parts = raw_text[len(VOICE_TRAINED_PREFIX):].split("|", 5)
       if len(parts) == 6:
           gpt_weights_path, sovits_weights_path, ref_audio_path, prompt_text, lang, text = parts
           custom_voice_config = {
               "gpt_weights": gpt_weights_path,  # Custom trained weights
               "sovits_weights": sovits_weights_path,  # Custom trained weights
               ...
           }
   ```

**Files:**
- `apps/mofa-tts/src/screen_moyoyo.rs:2720-2754`
- `node-hub/dora-primespeech/dora_primespeech/main.py:28` (add VOICE_TRAINED_PREFIX constant)
- `node-hub/dora-primespeech/dora_primespeech/main.py:296-354` (add parsing logic)

---
