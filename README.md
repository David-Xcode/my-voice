# my-voice

**Local-first push-to-talk that turns your speech (Chinese + English) into high-quality, structured prompts for [Claude Code](https://claude.com/claude-code) — and pastes them at your cursor. 100% on-device, no audio or text leaves your machine.**

Think Typeless / Wispr Flow, but local and tuned for prompting a coding agent: instead of just transcribing, it restructures rambling speech into a clean `Goal / Location / Constraints / Verification` prompt.

> **This is a fork of [cjpais/Handy](https://github.com/cjpais/Handy) (MIT).** Handy provides the hard parts — global hotkey, microphone capture, Silero VAD, local whisper.cpp transcription, and clipboard-paste injection. my-voice adds a tuned local-LLM cleanup mode for Claude Code. Huge credit to CJ Pais and the Handy project. The original Handy README is kept as [`README.upstream-handy.md`](./README.upstream-handy.md).

## How it works

```
⌥⇧Space (hold) → mic capture → Silero VAD → whisper.cpp (large-v3, multilingual)
   → raw transcript → local LLM cleanup (Ollama · Qwen3-4B-Instruct)
   → structured Claude Code prompt → clipboard paste at cursor
```

Everything runs locally. The only network call is optional (you sending the finished prompt to Claude). Permissions requested: **Microphone + Accessibility only**.

## Status

v1 works end-to-end on macOS (Apple Silicon). See [`docs/`](./docs) for the full story:
- [`docs/superpowers/plans/2026-06-29-voice-to-prompt-claude-code.md`](./docs/superpowers/plans/2026-06-29-voice-to-prompt-claude-code.md) — the implementation plan
- [`docs/handy-file-map.md`](./docs/handy-file-map.md) — where Handy's hook points are
- [`docs/prompts/claude-code-prompt.md`](./docs/prompts/claude-code-prompt.md) — the cleanup prompt + validation results
- [`docs/v1-runbook.md`](./docs/v1-runbook.md) — in-app configuration steps

## Setup (macOS, Apple Silicon)

Prerequisites:
```bash
# Rust, bun, cmake, Xcode Command Line Tools
xcode-select --install
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
brew install bun cmake ollama

# cleanup model (non-thinking instruct — the hybrid qwen3:4b "thinks" and is too slow)
brew services start ollama
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

Build & run:
```bash
bun install
# HANDY_FORCE_AI_STUB=1 skips the Apple Intelligence Swift bridge, which needs FULL Xcode
# (the @Generable macro plugin is absent in Command Line Tools). Omit it if you have full
# Xcode and want the on-device Apple Intelligence cleanup backend instead of Ollama.
HANDY_FORCE_AI_STUB=1 bun tauri dev
```

Configure cleanup (Settings → Post-processing):
- Provider **Custom** → `http://localhost:11434/v1` (Ollama)
- Model `qwen3:4b-instruct-2507-q4_K_M`
- Add the prompt from [`docs/prompts/claude-code-prompt.md`](./docs/prompts/claude-code-prompt.md), select it
- STT: download a **multilingual** Whisper model (`large` / `large-v3`) — not an `.en` model
- Hotkey: **⌥⇧Space** = cleanup, **⌥Space** = raw dictation

## What this fork adds over Handy

- A tuned **"Claude Code Prompt"** post-process mode (Goal/Location/Constraints/Verification + isolation guard, faithfulness rules, `先给出方案，确认后再写代码。` footer).
- `HANDY_FORCE_AI_STUB` build flag so it compiles on Command-Line-Tools-only Macs (no full Xcode).
- Documentation of the local-first Ollama + Qwen3 cleanup path and validated latency/quality.

## Personal dictionary & prompt modes

Your professional vocabulary lives in [`dictionary.json`](./dictionary.json) — the single source of truth:
- `hotwords` → Whisper `initial_prompt`, so terms like `subagent`, `MCP`, `git rebase` transcribe correctly.
- `replacements` → injected into the cleanup prompt, so spoken forms become code (`use state` → `useState`).

Two cleanup modes are seeded (switch in Settings → Post-processing):
- **Claude Code Prompt** (default, "L2") — distills your speech into a *professional* prompt, parking unknowns under `## 待确认` instead of inventing them. ~15–20s.
- **Claude Code (Faithful)** ("L1") — literal restructuring only; faster (~5–8s), no elaboration.

Grow the dictionary — edit `dictionary.json`, then:
```bash
python3 scripts/apply-dictionary.py   # syncs hotwords + replacements into Handy settings
# then restart the app (settings load at startup)
```

## Roadmap

- Auto-learn dictionary terms by mining Handy's `history.db` (raw transcript vs your edits)
- Per-app auto-mode (frontmost bundle id → prompt)
- Raw-transcript one-tap revert
- Reduce small-model padding (faithfulness tuning); optional larger model for "L3" elaboration

## License

[MIT](./LICENSE). Retains the original Handy copyright (CJ Pais) as required, plus modifications © 2026 David-Xcode. Whisper weights are MIT; Qwen3 weights are Apache-2.0 (both downloaded at runtime, not bundled).
