# Handy Architecture & Hook-Point Map

> Produced 2026-06-29 by a read-only exploration of the vendored `cjpais/Handy` source under `src-tauri/src/`. Purpose: know exactly what Handy already does before adding a Claude-Code-prompt cleanup mode, so we reuse instead of rebuild.

## End-to-end flow (hotkey → injection)

1. `shortcut/handler.rs:29` `handle_shortcut_event()` — receives key event, delegates to coordinator.
2. `transcription_coordinator.rs:121` `send_input()` — serializes events on a single-thread channel.
3. `transcription_coordinator.rs:161` `start()` — looks up binding in `ACTION_MAP`, calls `action.start()`.
4. `actions.rs:404` `TranscribeAction::start()` — preloads model, opens CPAL mic, start feedback.
5. `managers/audio.rs:386` `try_start_recording()` — `SileroVad` (resources/models/silero_vad_v4.onnx, thr 0.3) + `SmoothedVad`, records 16 kHz f32.
6. release/re-press → `transcription_coordinator.rs:177` `stop()` → `actions.rs:506` `TranscribeAction::stop()`.
7. `managers/audio.rs:427` `stop_recording()` — returns VAD-filtered 16 kHz PCM; saves WAV to history.
8. `managers/transcription.rs:473` `transcribe()` — runs STT. Whisper gets `initial_prompt = settings.custom_words.join(", ")` (transcription.rs:586). Post: fuzzy custom-word correction (non-Whisper) + `filter_transcription_output` (hallucination/filler strip).
9. `actions.rs:363` `process_transcription_output()` — (a) optional OpenCC zh-Hans↔zh-Hant via `maybe_convert_chinese_variant()`; (b) optional LLM cleanup via `post_process_transcription()` (actions.rs:378) when `post_process=true`.
10. **HOOK POINT — `actions.rs:619-627`**: `let final_text = processed.final_text;` then `utils::paste(final_text, ...)`. Last mutation point before injection.
11. `clipboard.rs:591` `paste()` — save clipboard → write text → Cmd+V via `enigo` (keycode 9 = physical V) → restore clipboard. Optional `auto_submit` (Enter). No AX injection.

## LLM cleanup layer — ALREADY EXISTS (the key finding)

- `llm_client.rs` — OpenAI-compatible client: `POST {base_url}/chat/completions`, supports `response_format` json_schema (structured output) and `reasoning_effort`.
- Providers (`settings.rs:524-613`): `openai`, `zai`, `openrouter`, `anthropic`, `groq`, `cerebras`, `bedrock_mantle`, **`apple_intelligence`** (macOS arm64, on-device Foundation Models via Swift FFI in `apple_intelligence.rs`), **`custom` (defaults to `http://localhost:11434/v1` = Ollama, base-url editable)**.
- For the `custom`/Ollama provider, `reasoning_effort:"none"` is already sent (`actions.rs:146-150`) to suppress chain-of-thought.
- Prompts: `settings.rs:90-94` `LLMPrompt{id,name,prompt}`; `post_process_prompts: Vec<LLMPrompt>`; `post_process_selected_prompt_id`. Default prompt "Improve Transcriptions" (settings.rs:641). Full CRUD via Tauri commands in `shortcut/mod.rs` (`add/update/delete/set_post_process_selected_prompt`).
- Wired & active via two bindings (`settings.rs:725-755`): `transcribe` (raw, default ⌥Space) and `transcribe_with_post_process` (cleanup, default ⌥⇧Space). `post_process_enabled` gates the second.
- `apple_intelligence.rs:13-30` — FFI to Swift `process_text_with_system_prompt_apple` → macOS 26 `SystemLanguageModel` (Foundation Models), on-device, arm64-gated, availability checked on first use (avoids beta SIGABRT).

## STT engine

- Crate `transcribe-rs = 0.3.8` features `["whisper-cpp","onnx"]`, Metal on macOS.
- Engines (`managers/transcription.rs:39-48`): Whisper (whisper.cpp), Parakeet, Moonshine(+Streaming), SenseVoice, GigaAM, Canary, Cohere — all selectable; model chosen by `settings.selected_model` ID, downloadable in-app. large-v3-turbo multilingual = pick the right model ID.
- Hotwords: `settings.custom_words: Vec<String>` → Whisper `initial_prompt` (transcription.rs:586). Non-Whisper: Levenshtein+Soundex fuzzy correction.

## Modes / per-app — DOES NOT EXIST

- No profiles, no modes, no frontmost-app detection anywhere. Settings are global+flat (`AppSettings`, settings.rs:338-433).
- Per-app behavior (auto-pick prompt by frontmost bundle id) = NEW Rust code: `NSWorkspace.shared.frontmostApplication?.bundleIdentifier` → prompt id.

## Build & test

- Frontend: Vite+React+TS; dev = `npm run tauri dev`; some scripts use `bun` (`postinstall` → `bun scripts/check-nix-deps.ts`).
- Cargo: `reqwest 0.12` (json,stream) already present; `transcribe-rs`, `vad-rs` (git).
- Tests: inline `#[cfg(test)]` modules (no `tests/` dir); dev-dep `tempfile`.

## What we ADD vs REUSE

REUSE (already done): llm_client, post_process chain, settings/prompt CRUD UI, Ollama (`custom`) + Apple Intelligence providers, raw/cleanup dual hotkeys, `custom_words`→initial_prompt, history (raw+processed) storage, OpenCC.

ADD (the real new work):
1. **Claude-Code prompt template** — a new `LLMPrompt` data record (Goal/Location/Constraints/Verification + isolation guard + "先给出方案" footer). No Rust code; configuration/data.
2. **Per-app auto-mode** — frontmost bundle id → prompt id mapping. NEW Rust + settings concept. (Biggest new piece.)
3. **Structured dictionary** — spoken→written JSON with replacement rules (beyond the flat `custom_words`).
4. **Raw-revert hotkey** — re-inject the stored raw transcript (history already stores it; no revert action exists).
