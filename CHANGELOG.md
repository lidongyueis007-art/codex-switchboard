# Changelog / 更新记录

## 0.1.0 - 2026-06-16

Initial public version.

初始公开版本。

- Added optional API account Base URL support through `OPENAI_BASE_URL`.
- Added auth isolation that removes inherited OpenAI environment variables before each launch.
- Added `preferred_auth_method` writing for each isolated instance.
- Stopped overwriting live ChatGPT instance `auth.json` on every launch.
- Added refreshed ChatGPT login sync from instance back to saved snapshot.
- Added launch PID tracking and a warning for possible Codex single-instance swallowing.
- Added isolated Codex App launching for multiple accounts.
- Added ChatGPT account snapshot saving.
- Added API-key account profiles.
- Added account inheritance with target identity preservation.
- Added Project Library for transferring one project or one conversation.
- Added Chinese and English UI switching.
- Added Windows DPAPI secret storage.

- 支持 API 账号配置可选 Base URL，并通过 `OPENAI_BASE_URL` 注入。
- 启动前会清理继承自系统的 OpenAI 环境变量，避免账号串味。
- 为每个隔离实例写入 `preferred_auth_method`。
- 不再每次启动都覆盖 ChatGPT 实例里的活 `auth.json`。
- 支持把实例里刷新后的 ChatGPT 登录态同步回保存快照。
- 增加启动 PID 追踪，并在疑似被 Codex 单实例机制吞掉时提示。
- 支持多账号隔离启动 Codex App。
- 支持保存 ChatGPT 账号快照。
- 支持 API Key 账号。
- 支持账号继承，并保留目标账号身份。
- 支持项目大全，可转移单个项目或单段对话。
- 支持中文和英文界面切换。
- 使用 Windows DPAPI 保存本地密钥。
