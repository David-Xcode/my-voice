# v1 Runbook — get a working voice → Claude Code prompt

Do these once the Handy app window appears (after the first `bun tauri dev` build finishes). v1 needs ZERO new code — it's configuration on top of the vendored Handy.

## 0. Prerequisite: turn on Apple Intelligence (one-time, macOS)

The v1 cleanup backend is Apple's on-device model. If it's not enabled, the cleanup step will fail.
- System Settings → **Apple Intelligence & Siri** → turn ON, wait for the on-device models to download.
- If Apple Intelligence is unavailable on your account/region, that's the trigger to switch the backend to Ollama+Qwen3-4B (we deferred installing it).

## 1. Grant permissions (prompted at first launch)

- **Microphone** → Allow.
- **Accessibility** → Allow (System Settings → Privacy & Security → Accessibility, toggle Handy ON). Required for the global hotkey AND for paste injection.

## 2. Download a multilingual STT model (for Chinese)

- Settings → Models → download a **Whisper multilingual** model — `large-v3-turbo` (best quality/speed for CN+EN) or `large-v3`.
- Avoid `.en` (English-only) models — they garble Chinese.
- Set language to auto-detect (or `zh`/`en` as you prefer). Select the downloaded model as active.

## 3. Configure the cleanup (post-processing)

- Settings → Post-processing → **enable**.
- Provider: **Apple Intelligence** (on-device).
- Add a prompt named **"Claude Code Prompt"** → paste the SYSTEM PROMPT from `docs/prompts/claude-code-prompt.md` verbatim.
- Set it as the **selected** post-process prompt.

## 4. Hotkeys

- Confirm two bindings exist (Settings → Shortcuts):
  - **Raw dictation** = ⌥Space (`transcribe`) — plain transcript, no cleanup.
  - **Claude Code prompt** = ⌥⇧Space (`transcribe_with_post_process`) — runs the cleanup. This is the one you'll use for prompting Claude Code.
- Prefer **hold-to-talk** (push_to_talk = ON): hold the key while speaking, release to transcribe.

## 5. Optional: seed your code dictionary

- Settings → add **custom words** (these are fed to Whisper so identifiers transcribe right): e.g. `useState`, `Claude`, `Tauri`, your repo/module names.
- For spoken→written rewrites (`use state` → `useState`), put a dictionary list into the prompt's `{{DICTIONARY}}` slot.

## 6. Test the end-to-end flow

1. Open a terminal running `claude`, click into it so it's focused.
2. Hold **⌥⇧Space**, say (mixed CN/EN is fine):
   > 帮我把 user service 里的 login 方法改成 async，但别动返回类型，记得跑 npm test
3. Release. Expect a **structured prompt** pasted at the cursor (Goal/位置/约束/验证 + "先给出方案，确认后再写代码。") — NOT an answer to the request.
4. Review it, then hit Enter to send to Claude Code.

## Pass/fail judgment (decides Apple-vs-Ollama)

GOOD = fillers gone, every constraint kept ("don't change return type", "npm test"), no invented requirements, did not answer the request, Chinese preserved.

If the output invents constraints, drops what you said, answers instead of restructuring, or truncates → Apple's on-device model isn't strong enough for the structured task. That's the signal to install Ollama + Qwen3-4B (the deferred backend) and point Handy's `custom` provider at it.
