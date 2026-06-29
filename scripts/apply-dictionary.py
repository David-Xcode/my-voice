#!/usr/bin/env python3
"""把 dictionary.json + prompts/*.txt 同步进 Handy 的 settings_store.json。

加词流程：编辑 dictionary.json → 跑本脚本 → 重启 app（设置只在启动时加载）。
- hotwords  → settings.custom_words（Whisper initial_prompt，听对拼写）
- replacements → 注入清洗 prompt 的 <dictionary> 槽（写对术语形式）
两档 prompt（L2 专业精炼 = 默认；L1 忠实 = 备选）都会 upsert，其它已有 prompt 保留。

用法: python3 scripts/apply-dictionary.py [--model MODEL] [--settings PATH]
"""
import argparse, json, os, sys, tempfile, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SETTINGS = os.path.expanduser(
    "~/Library/Application Support/com.pais.handy/settings_store.json")
DEFAULT_MODEL = "qwen3:4b-instruct-2507-q4_K_M"

# 仓库内的 prompt 模板 -> 设置里的 prompt 记录（id 固定，幂等 upsert）
PROMPTS = [
    ("claude_code_prompt",   "Claude Code Prompt",       "prompts/claude-code-l2.txt"),
    ("claude_code_faithful", "Claude Code (Faithful)",   "prompts/claude-code-l1-faithful.txt"),
]
SELECTED = "claude_code_prompt"  # 默认选 L2


def render_replacements(repl: dict) -> str:
    # "use state → useState, console log → console.log, ..."
    return ", ".join(f"{k} → {v}" for k, v in repl.items())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--settings", default=DEFAULT_SETTINGS)
    args = ap.parse_args()

    dictionary = json.load(open(os.path.join(REPO, "dictionary.json"), encoding="utf-8"))
    hotwords = list(dict.fromkeys(dictionary.get("hotwords", [])))  # 去重保序
    repl_block = render_replacements(dictionary.get("replacements", {}))

    if not os.path.exists(args.settings):
        sys.exit(f"找不到设置文件：{args.settings}（先启动一次 Handy 让它生成）")
    data = json.load(open(args.settings, encoding="utf-8"))
    s = data["settings"]

    # 1) 后处理后端：本地 Ollama custom provider + instruct 模型
    s["post_process_enabled"] = True
    s["post_process_provider_id"] = "custom"
    s["post_process_models"]["custom"] = args.model

    # 2) Whisper hotwords
    s["custom_words"] = hotwords

    # 3) upsert 两档 prompt（保留其它已有 prompt），注入 replacements
    others = [p for p in s.get("post_process_prompts", [])
              if p.get("id") not in {pid for pid, _, _ in PROMPTS}]
    ours = []
    for pid, name, rel in PROMPTS:
        tmpl = open(os.path.join(REPO, rel), encoding="utf-8").read()
        ours.append({"id": pid, "name": name,
                     "prompt": tmpl.replace("{{REPLACEMENTS}}", repl_block)})
    s["post_process_prompts"] = others + ours
    s["post_process_selected_prompt_id"] = SELECTED

    # 原子写回 + 备份
    shutil.copy(args.settings, args.settings + ".bak")
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(args.settings))
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, args.settings)

    print(f"✓ custom_words: {len(hotwords)} 个 hotword")
    print(f"✓ replacements: {len(dictionary.get('replacements', {}))} 条")
    print(f"✓ prompts: {[p['name'] for p in s['post_process_prompts']]}  (selected: {SELECTED})")
    print(f"✓ model: {args.model}")
    print("⚠ 重启 Handy 生效（设置只在启动时加载）。")


if __name__ == "__main__":
    main()
