#!/usr/bin/env python3
"""
Precise TTS hang diagnosis - tests each component individually.
Run with: conda activate mofa-studio && python diagnose_tts.py
"""
import sys
import os
import signal
import time

# Ensure correct paths - mirror what the wrapper does
_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "node-hub/dora-primespeech/dora_primespeech")
sys.path.insert(0, _base)
# CRITICAL: Add moyoyo_tts subdirectory so "from text.chinese2 import ..." works
_moyoyo_dir = os.path.join(_base, "moyoyo_tts")
if os.path.isdir(_moyoyo_dir):
    sys.path.insert(0, _moyoyo_dir)
os.chdir(_base)

MODELS_PATH = os.path.expanduser("~/.dora/models/primespeech/moyoyo")

def timeout_handler(signum, frame):
    print("\n!!! TIMEOUT - HUNG AT THIS STEP !!!", flush=True)
    import traceback
    for tid, f in sys._current_frames().items():
        print(f"\nThread {tid}:")
        traceback.print_stack(f)
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)

def step(name, timeout_sec=30):
    """Context manager for timed steps"""
    class StepCtx:
        def __enter__(self):
            print(f"\n{'='*60}", flush=True)
            print(f"STEP: {name} (timeout={timeout_sec}s)", flush=True)
            print(f"{'='*60}", flush=True)
            signal.alarm(timeout_sec)
            self.t0 = time.time()
            return self
        def __exit__(self, *args):
            signal.alarm(0)
            dt = time.time() - self.t0
            if args[0] is None:
                print(f"  OK ({dt:.2f}s)", flush=True)
            else:
                print(f"  FAILED after {dt:.2f}s: {args[1]}", flush=True)
            return False
    return StepCtx()

# ============================================================
print("TTS Hang Diagnosis Tool", flush=True)
print(f"Models path: {MODELS_PATH}", flush=True)
print(f"Python: {sys.version}", flush=True)
# ============================================================

with step("1. Import torch", 30):
    import torch
    import numpy as np
    print(f"  PyTorch {torch.__version__}", flush=True)
    print(f"  Device: cpu", flush=True)
    print(f"  Threads: {torch.get_num_threads()}", flush=True)

with step("2. Basic tensor operation", 10):
    x = torch.randn(100, 100)
    y = x @ x.T
    print(f"  Result shape: {y.shape}", flush=True)

with step("3. F.scaled_dot_product_attention on CPU", 15):
    q = torch.randn(1, 8, 32, 64)
    k = torch.randn(1, 8, 32, 64)
    v = torch.randn(1, 8, 32, 64)
    mask = torch.zeros(32, 32, dtype=torch.bool)
    mask = torch.triu(mask, diagonal=1)
    mask = mask.unsqueeze(0).unsqueeze(0).expand(1, 8, -1, -1)
    out = torch.nn.functional.scaled_dot_product_attention(q, k, v, ~mask)
    print(f"  SDPA output shape: {out.shape}", flush=True)

with step("4. torch.jit.script class", 30):
    @torch.jit.script
    class TestJIT:
        def __init__(self, w: torch.Tensor):
            self.w = w
        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return x @ self.w
    w = torch.randn(64, 64)
    jit_obj = TestJIT(w)
    result = jit_obj.forward(torch.randn(1, 64))
    print(f"  JIT class works, output: {result.shape}", flush=True)

with step("5. Fix LangSegment compatibility + Import TTS", 30):
    # Apply the same LangSegment fix that the wrapper uses
    try:
        import LangSegment
    except ImportError as exc:
        if "setLangfilters" in str(exc):
            print(f"  LangSegment compatibility issue detected, patching...", flush=True)
            import importlib.util
            from pathlib import Path
            # Try the bundled fix first
            fix_path = Path(os.path.dirname(__file__)) / "node-hub/dora-primespeech/dora_primespeech/moyoyo_tts/LangSegment_fix.py"
            if fix_path.exists():
                spec = importlib.util.spec_from_file_location("LangSegment.LangSegment", str(fix_path))
                langseg_module = importlib.util.module_from_spec(spec)
                sys.modules['LangSegment'] = langseg_module
                sys.modules['LangSegment.LangSegment'] = langseg_module
                spec.loader.exec_module(langseg_module)
                print(f"  Patched with LangSegment_fix.py", flush=True)
            else:
                # Monkey-patch: add setLangfilters as alias for setfilters
                print(f"  No fix file, trying monkey-patch...", flush=True)
                import importlib
                ls_mod = importlib.import_module("LangSegment.LangSegment")
                if hasattr(ls_mod, "setfilters") and not hasattr(ls_mod, "setLangfilters"):
                    ls_mod.setLangfilters = ls_mod.setfilters
                if hasattr(ls_mod, "getfilters") and not hasattr(ls_mod, "getLangfilters"):
                    ls_mod.getLangfilters = ls_mod.getfilters
                # Patch __init__ imports
                sys.modules['LangSegment'] = type(sys)('LangSegment')
                sys.modules['LangSegment'].LangSegment = ls_mod.LangSegment if hasattr(ls_mod, 'LangSegment') else ls_mod
                sys.modules['LangSegment'].getTexts = ls_mod.getTexts
                sys.modules['LangSegment'].setfilters = ls_mod.setfilters
                sys.modules['LangSegment'].setLangfilters = ls_mod.setfilters
                sys.modules['LangSegment'].getfilters = ls_mod.getfilters
                sys.modules['LangSegment'].getLangfilters = ls_mod.getfilters
                sys.modules['LangSegment.LangSegment'] = ls_mod
                print(f"  Monkey-patched setLangfilters -> setfilters", flush=True)
        else:
            raise
    else:
        # LangSegment imported OK, but check if setLangfilters exists
        import LangSegment.LangSegment as ls_mod
        if not hasattr(ls_mod, "setLangfilters") and hasattr(ls_mod, "setfilters"):
            ls_mod.setLangfilters = ls_mod.setfilters
            print(f"  Added setLangfilters alias", flush=True)
        if hasattr(ls_mod, "LangSegment"):
            cls = ls_mod.LangSegment
            if not hasattr(cls, "setLangfilters") and hasattr(cls, "setfilters"):
                cls.setLangfilters = cls.setfilters

    from moyoyo_tts.TTS_infer_pack.TTS import TTS, TTS_Config
    # CRITICAL: Register moyoyo_tts.utils as top-level 'utils' for torch.load unpickling
    if "utils" not in sys.modules:
        import moyoyo_tts.utils as _moyoyo_utils
        sys.modules['utils'] = _moyoyo_utils
        print(f"  Registered moyoyo_tts.utils as top-level 'utils'", flush=True)
    print(f"  TTS imported successfully", flush=True)

with step("6. Load TTS config", 10):
    config_dict = {
        "version": "v2",
        "custom": {
            "device": "cpu",
            "is_half": False,
            "version": "v2",
            "t2s_weights_path": os.path.join(MODELS_PATH, "GPT_weights/doubao-mixed.ckpt"),
            "vits_weights_path": os.path.join(MODELS_PATH, "SoVITS_weights/doubao-mixed.pth"),
            "cnhuhbert_base_path": os.path.join(MODELS_PATH, "chinese-hubert-base"),
            "bert_base_path": os.path.join(MODELS_PATH, "chinese-roberta-wwm-ext-large"),
        }
    }
    # Check files exist
    for k, v in config_dict["custom"].items():
        if "path" in k:
            exists = os.path.exists(v)
            print(f"  {k}: {'EXISTS' if exists else 'MISSING'} - {v}", flush=True)

with step("7. Initialize TTS (loads all models)", 120):
    tts = TTS(config_dict)
    print(f"  TTS initialized", flush=True)
    print(f"  Device: {tts.configs.device}", flush=True)
    print(f"  is_half: {tts.configs.is_half}", flush=True)

with step("8. Load reference audio (HuBERT + spectrogram)", 60):
    ref_audio = os.path.join(MODELS_PATH, "ref_audios/doubao_ref_mix_new.wav")
    if os.path.exists(ref_audio):
        tts.set_ref_audio(ref_audio)
        print(f"  Reference audio loaded", flush=True)
        print(f"  prompt_semantic shape: {tts.prompt_cache['prompt_semantic'].shape}", flush=True)
    else:
        print(f"  MISSING: {ref_audio}", flush=True)
        sys.exit(1)

with step("9. Text preprocessing (BERT features)", 60):
    from moyoyo_tts.TTS_infer_pack.TextPreprocessor import TextPreprocessor
    prompt_text = "这家resturant的steak很有名，但是vegetable salad的price有点贵"
    phones, bert_features, norm_text = tts.text_preprocessor.segment_and_extract_feature_for_text(
        prompt_text, "zh", "v2"
    )
    print(f"  phones: {len(phones)}", flush=True)
    print(f"  bert_features shape: {bert_features.shape}", flush=True)
    tts.prompt_cache["phones"] = phones
    tts.prompt_cache["bert_features"] = bert_features
    tts.prompt_cache["norm_text"] = norm_text
    tts.prompt_cache["prompt_text"] = prompt_text
    tts.prompt_cache["prompt_lang"] = "zh"

with step("10. Target text preprocessing", 30):
    target_text = "你好"
    data = tts.text_preprocessor.preprocess(target_text, "zh", "cut0", "v2")
    print(f"  Preprocessed {len(data)} segments", flush=True)

with step("11. Batch preparation", 10):
    data, batch_index_list = tts.to_batch(
        data,
        prompt_data=tts.prompt_cache,
        batch_size=1,
        threshold=0.75,
        split_bucket=True,
        device=tts.configs.device,
        precision=tts.precision
    )
    print(f"  Batches: {len(data)}", flush=True)
    for i, item in enumerate(data):
        print(f"  Batch {i}: phones_len={item['all_phones_len']}", flush=True)

with step("12. AR model inference (t2s_model) - THIS IS WHERE IT LIKELY HANGS", 120):
    item = data[0]
    all_phoneme_ids = item["all_phones"]
    all_phoneme_lens = item["all_phones_len"]
    all_bert_features = item["all_bert_features"]
    prompt = tts.prompt_cache["prompt_semantic"].expand(len(all_phoneme_ids), -1).to(tts.configs.device)
    max_len = item["max_len"]

    print(f"  all_phoneme_ids type: {type(all_phoneme_ids)}, len={len(all_phoneme_ids) if isinstance(all_phoneme_ids, list) else all_phoneme_ids.shape}", flush=True)
    print(f"  prompt shape: {prompt.shape}", flush=True)
    print(f"  all_bert_features type: {type(all_bert_features)}, len={len(all_bert_features) if isinstance(all_bert_features, list) else all_bert_features.shape}", flush=True)
    print(f"  Calling infer_panel...", flush=True)

    # Use parallel infer (default)
    tts.t2s_model.model.infer_panel = tts.t2s_model.model.infer_panel_batch_infer
    pred_semantic_list, idx_list = tts.t2s_model.model.infer_panel(
        all_phoneme_ids,
        all_phoneme_lens,
        prompt,
        all_bert_features,
        top_k=5,
        top_p=1.0,
        temperature=1.0,
        early_stop_num=tts.configs.hz * tts.configs.max_sec,
        max_len=max_len,
        repetition_penalty=1.35,
    )
    print(f"  AR inference done! pred_semantic_list len={len(pred_semantic_list)}", flush=True)

with step("13. VITS decode (vocoder)", 60):
    refer_audio_spec = [item.to(dtype=tts.precision, device=tts.configs.device)
                        for item in tts.prompt_cache["refer_spec"]]
    pred_semantic_list_trimmed = [item[-idx:] for item, idx in zip(pred_semantic_list, idx_list)]
    import math
    all_pred_semantic = torch.cat(pred_semantic_list_trimmed).unsqueeze(0).unsqueeze(0).to(tts.configs.device)
    batch_phones_item = data[0]["phones"]
    _batch_phones = torch.cat(batch_phones_item).unsqueeze(0).to(tts.configs.device)
    audio = tts.vits_model.decode(
        all_pred_semantic, _batch_phones, refer_audio_spec, speed=1.0
    ).detach()[0, 0, :]
    print(f"  VITS decode done! audio shape: {audio.shape}", flush=True)
    print(f"  Duration: {len(audio)/tts.configs.sampling_rate:.2f}s", flush=True)

print("\n" + "="*60, flush=True)
print("ALL STEPS PASSED! TTS pipeline works correctly.", flush=True)
print("="*60, flush=True)
