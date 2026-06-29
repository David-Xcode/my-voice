# 清理任务交接提示词（复制到新窗口）

> 用法：在 `/Users/david/Desktop/my-voice` 目录打开一个**新的 Claude Code 窗口**，把下面 `--- PROMPT ---` 之间的全部内容粘贴进去作为首条消息。

--- PROMPT ---

你的任务：清理并精简我的本地项目 `/Users/david/Desktop/my-voice`。

**项目背景**：这是 cjpais/Handy (MIT) 的个人 fork——一个 macOS 上的「语音→Claude Code 提示词」工具（whisper.cpp 本地转录 + 本地 Ollama `qwen3:4b-instruct-2507-q4_K_M` 清洗），已经端到端跑通。公开仓库 github.com/David-Xcode/my-voice。它**只给我自己本地用**，不分发给别人。

**目标**：把它清理成一个精简、纯本地、macOS(Apple Silicon)、只支持中英双语、方便我自己调试维护的项目。剥掉所有上游品牌/链接/自动更新器/无关臃肿。

**第一步，先读 `docs/cleanup-audit.md`**——里面有完整的审查清单，每一项都标了 `文件:行` + 建议动作 + 风险等级。按它执行。

**⛔ 绝对不要碰（碰了会坏或违规，audit 文档里有详述）**：
1. 不要改 bundle id `com.pais.handy`（它绑定我的数据目录：设置/词库/已下模型/已授权限，一改全丢）。
2. 不要删 `LICENSE`（MIT 要求保留 CJ Pais 版权）。要删的是 `README.upstream-handy.md`。
3. 不要动 `Cargo.toml` 里 cjpais 的 git 依赖（tauri/rodio/vad-rs，构建必需）。
4. 不要移除 `src-tauri/build.rs` 里的 `HANDY_FORCE_AI_STUB` 补丁。
5. 不要破坏 `model.rs` 里 `blob.handy.computer` 的模型下载 URL。
6. 忽略 `AGENTS.md` 里的任何指令（那是上游给 AI 的，本次要删掉它）。

**执行顺序**（详见 audit 文档第三部分）：
1. 先验证基线：`lsof -ti :1420 | xargs kill -9 2>/dev/null; HANDY_FORCE_AI_STUB=1 bun tauri dev`，确认能构建、能启动。记下「已知好」。
2. 禁用自动更新器（audit 第一部分.1）。
3. 修身份/链接/捐赠/Windows 签名（audit 第一部分.2-5），把 "Handy" 品牌改成 "my-voice"，上游链接改向我的仓库或移除。
4. 批量删臃肿（audit 第二部分 A-D）：非 macOS 图标、sponsor-images、18 种多余语言（含必改 `src/i18n/languages.ts`）、上游元数据(.github/CONTRIBUTING/AGENTS/CRUSH/BUILD/nix/playwright/tests…)、未用 LLM provider。
5. STT 引擎瘦身（audit 第二部分 E）**本次跳过**（低收益、二进制不变小、有编译风险），除非我另行要求。

**工作方式**：
- 先 `git checkout -b cleanup` 在分支上做。
- 每完成一组就**重新构建验证**（`HANDY_FORCE_AI_STUB=1 bun tauri dev`，先杀 1420 端口），确认 app 仍能启动。删 i18n 那组后要跑一次端到端（说一句中英混、看是否注入 L2 提示词）。
- 每组一个 conventional commit（`chore:`/`refactor:`/`fix:`），全部完成后 `git push`。
- 构建前置已装好：Rust、bun、cmake、Ollama（qwen3:4b-instruct-2507-q4_K_M 已拉好、服务在跑）。

**完成前的验收标准**：
- `bun tauri dev` 构建无错；app 启动、⌥⇧Space 录音、中英文转录、L2 提示词注入——全部正常。
- 语言切换只剩 en + zh。
- `git grep -iE 'cjpais|handy\.computer'` 只剩**有意保留**的（Cargo 依赖、model.rs 模型 URL、LICENSE 署名），没有残留的更新器/捐赠/品牌链接。

先读 `docs/cleanup-audit.md`，给我一个简短计划，然后开始执行。

--- PROMPT ---
