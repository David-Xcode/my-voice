# my-voice 清理审查清单 (2026-06-29)

本项目是 cjpais/Handy (MIT) 的个人本地化 fork。目标：**精简、纯本地自用、macOS(Apple Silicon)、中英双语、好维护**。
本文档由两个只读审查 agent + grep 交叉验证产出，供「清理窗口」据此执行。**本窗只审查，不改动。**

---

## ⛔ 绝对不要碰（碰了会坏 / 违规）

| 项 | 位置 | 为什么 |
|---|---|---|
| **bundle id `com.pais.handy`** | `src-tauri/tauri.conf.json:5` | 它决定数据目录 `~/Library/Application Support/com.pais.handy/`。改了 → 你的 **L2 prompt、词库、已下载的 large 模型、已授麦克风/辅助功能权限全部孤立**，要重配重下重授权。**默认保持不变**；除非你愿意连带迁移整个数据目录。 |
| **LICENSE** | `LICENSE` | MIT 要求保留 CJ Pais 版权声明。删了 = 违反许可。**必须留。**（要删的是 `README.upstream-handy.md`，不是 LICENSE。） |
| **cjpais 的 git 依赖** | `Cargo.toml:58,60,111-113` | `vad-rs`/`rodio`/`tauri`(branch handy-2.10.2) 是**功能性 fork 依赖**，构建必需。删了直接编不过。 |
| **`HANDY_FORCE_AI_STUB` 补丁** | `src-tauri/build.rs` | 我们加的，没有它在只装 CLT 的机器上构建会炸。**留。** |
| **model.rs 的 blob.handy.computer 模型 URL** | `src-tauri/src/managers/model.rs` | 这是模型下载源（功能性）。你已下好 large，但**别破坏**这些 URL，否则将来换模型下不动。要去依赖 CJ 的 CDN 是单独的大工程，不在本次清理范围。 |

---

## 第一部分：Fork 残留 / 指回上游（「类似的 bug」）

### 1. 自动更新器（最高优先 — 就是触发本次审查的 bug）
| 文件:行 | 问题 | 建议动作 |
|---|---|---|
| `src-tauri/tauri.conf.json:71` | updater endpoint → `cjpais/Handy/releases/.../latest.json` | **禁用**（个人自用不需要 OTA 更新） |
| `src-tauri/tauri.conf.json:69` | pubkey 是 cjpais 的 minisign 公钥 `BAB72095206601F9` | 禁用更新即可；要自更新得自己生成密钥对（个人自用不值得） |
| `src-tauri/src/settings.rs:456` | `update_checks_enabled` 默认 `true`（启动即检查） | 改默认为 `false` |
| `src-tauri/src/lib.rs:221-223` | 启用时启动自动发更新检查事件 | 默认关掉后即无影响 |
| `src/components/update-checker/UpdateChecker.tsx:206` | 手动更新回退打开 `cjpais/Handy/releases/latest` | 改指向自己仓库 或 移除该 UI |
| `src-tauri/tauri.conf.json:28` | `createUpdaterArtifacts: true` | 禁用更新后可设 false |

> **推荐做法**：直接**禁用更新器**（个人自用、从源码跑、没有发布/签名流程）。最干净。

### 2. 身份 / 品牌
| 文件:行 | 问题 | 动作 |
|---|---|---|
| `src-tauri/tauri.conf.json:3` | `productName: "Handy"` | 改 `"my-voice"`（注意：改的是 .app 名，不是 bundle id，安全） |
| `src-tauri/src/lib.rs:752` | 窗口标题 `.title("Handy")` | 改 `"my-voice"` |
| `src-tauri/src/tray.rs:90,92` | 托盘 `Handy v{ver}` | 改 `my-voice v{ver}` |
| `src-tauri/Cargo.toml:5` | `authors = ["cjpais"]` | 加上 David-Xcode（可保留 cjpais 致谢） |
| `package.json:2` | `"name": "handy-app"` | 可选改 `"my-voice-app"` |

### 3. 网络请求头（隐私 — 调云端 LLM 时泄漏身份；本地 Ollama 无影响）
| 文件:行 | 问题 | 动作 |
|---|---|---|
| `src-tauri/src/llm_client.rs:70` | Referer = `github.com/cjpais/Handy` | 改自己仓库 或 移除 |
| `src-tauri/src/llm_client.rs:74` | User-Agent = `Handy/1.0 (+.../cjpais/Handy)` | 改 `my-voice/1.0` |
| `src-tauri/src/llm_client.rs:76` | `X-Title: "Handy"` | 改 `"my-voice"` |

### 4. 捐赠 / 赞助 / 上游链接
| 文件:行 | 问题 | 动作 |
|---|---|---|
| `.github/FUNDING.yml` | github:cjpais + handy.computer/donate + paypal.me/cjpais | **删整个文件** |
| `src/components/settings/about/AboutSettings.tsx:32` | "Support Development" → `handy.computer/donate` | 移除捐赠按钮 |
| `src/components/settings/about/AboutSettings.tsx:69` | "Source Code" → `cjpais/Handy` | 改指向 `David-Xcode/my-voice` |

### 5. Windows 签名（Mac 构建用不到，但是上游残留）
| 文件:行 | 问题 | 动作 |
|---|---|---|
| `src-tauri/tauri.conf.json:61` | `signCommand: trusted-signing-cli ... -c cjpais-dev -d Handy` | 移除该 signCommand（你只构建 macOS） |

---

## 第二部分：可删臃肿（精简化）

### A. 资源 / 图标（SAFE — 仅删非 macOS 平台资源）
保留：`src-tauri/icons/{icon.icns, 32x32.png, 128x128.png, 128x128@2x.png}`；`src-tauri/resources/tray_*.png`（6 个，深浅主题托盘图标，代码 `tray.rs:51-57` 引用）。
**删**（约 716KB，零影响）：`src-tauri/icons/{icon.ico, icon.png, logo.png, 64x64.png, Square*.png(×10), ios/, android/}`；`src-tauri/resources/{handy.png, recording.png, transcribing.png}`（Linux 专用，`tray.rs:59-61` 仅 Linux 命中）；`sponsor-images/`（484KB，仅被原版 README 引用）。

### B. i18n（删 18 种语言 + 1 处改 — 保留 en + zh）
- 删 `src/i18n/locales/{ar,bg,cs,de,es,fr,he,it,ja,ko,pl,pt,ru,sv,tr,uk,vi,zh-TW}/`（保留 `en/`、`zh/`）
- **必改** `src/i18n/languages.ts`：`LANGUAGE_METADATA` 只留 `en` + `zh` 两条
- 安全原因：`src/i18n/index.ts` 用 `import.meta.glob("./locales/*/translation.json")` 自动发现；`build.rs:14-44` 也自动扫描生成托盘翻译——**删文件夹后两边都自动收敛，无需其它改动**

### C. 上游项目元数据（SAFE 全删）
`.github/`（workflows/CI、FUNDING、ISSUE_TEMPLATE、PULL_REQUEST_TEMPLATE）、`CONTRIBUTING.md`、`CONTRIBUTING_TRANSLATIONS.md`、`AGENTS.md`（⚠ Handy 给 AI 的指令文档，留着会误导清理窗口）、`CLAUDE.md`（仅指向 AGENTS.md）、`CRUSH.md`、`BUILD.md`、`README.upstream-handy.md`、`playwright.config.ts`、`tests/`、`.vscode/extensions.json`（可选）、`.prettierignore`（不用 prettier 才删）。
`nix/`、`.nix/`、`flake.nix`、`flake.lock`：**不用 Nix 就删**（约 120KB）。

### D. 未用 LLM provider（SAFE — settings.rs 一处编辑）
`src-tauri/src/settings.rs` 的 `default_post_process_providers()`：删 `openai/zai/openrouter/anthropic/groq/cerebras/bedrock_mantle` 块，**保留 `custom`(Ollama) + `apple_intelligence`**（后者已 cfg 编译门控）。前端自动读取，无需改动。

### E. 未用 STT 引擎（可选 / 低收益 — 谨慎）
Parakeet/Moonshine/SenseVoice/GigaAM/Canary/Cohere 在 `model.rs`(枚举+注册 ~263-611 行)、`transcription.rs`(匹配臂 344-412 行 + 导入 17-26 行)。
**评估**：删了**二进制不会变小**（`transcribe-rs` crate 仍编译全部引擎），只是代码更干净。跨文件改动、有编译风险。**建议本次跳过**，除非你明确想要「仅 Whisper」的代码库。

---

## 第三部分：推荐执行顺序
1. **先验证基线**：`HANDY_FORCE_AI_STUB=1 bun tauri dev` 能跑、能转录、清洗正常 → 记下「已知好」。
2. **禁用更新器**（第一部分.1）→ 重新构建验证。
3. **身份/链接/捐赠/签名**（第一部分.2-5）→ 构建验证。
4. **批量删臃肿**（第二部分 A-D，含 i18n 的 languages.ts 改动）→ 构建 + 跑一次端到端（说一句、看注入）验证。
5. （可选）STT 引擎瘦身（第二部分 E）。
6. 全程：每完成一组就 `git commit`，最后 `git push`。每改完一组都重新构建确认没编坏。

> ⚠ 数据目录提醒：不改 bundle id，你的 L2 prompt/词库/模型/权限就都还在，清理过程不影响日常使用。
