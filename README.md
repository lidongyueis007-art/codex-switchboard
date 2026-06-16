# Codex Switchboard / Codex 接力台

Codex Switchboard is a local Windows desktop launcher for people who use more than one Codex identity. It can start isolated Codex App windows for different ChatGPT or API-key accounts, copy useful local state between accounts, and move individual projects or conversations into the account where you want to continue working.

Codex 接力台是一个本地 Windows 桌面工具，适合同时使用多个 Codex 身份的人。它可以为不同的 ChatGPT 账号或 API Key 账号启动隔离的 Codex App 窗口，也可以在账号之间继承本地状态，并把某个项目或某段对话转移到指定账号下继续工作。

## Features / 功能

- **Multi-account launch / 多账号启动**: save account profiles and launch each one with its own `CODEX_HOME` and Chromium `--user-data-dir`.
- **ChatGPT and API accounts / 支持 ChatGPT 与 API 账号**: capture an existing Codex App ChatGPT login, or save an API key profile with optional organization, project, and base URL settings.
- **Account inheritance / 账号继承**: copy local Codex state from account A to account B while preserving B's identity.
- **Project Library / 项目大全**: scan local Codex projects and conversations, then transfer a whole project or one conversation into any saved account.
- **Bilingual interface / 双语界面**: switch between English and Chinese in the top-right corner.
- **Local secret protection / 本地密钥保护**: secrets are encrypted with Windows DPAPI and never sent to a third-party service by this app.

## What It Does / 工作方式

Each saved account gets its own local sandbox under:

```text
%APPDATA%\CodexSwitchboard
```

For every account, Switchboard maintains:

```text
profiles\<account>\profile.json
profiles\<account>\auth.dpapi
profiles\<account>\api.dpapi
instances\<account>\home
instances\<account>\browser
```

When launching Codex App, Switchboard injects the right environment and browser profile:

```text
CODEX_HOME=<account isolated home>
OPENAI_API_KEY=<API account key, when applicable>
OPENAI_ORG_ID / OPENAI_ORGANIZATION=<optional>
OPENAI_PROJECT_ID=<optional>
OPENAI_BASE_URL=<optional OpenAI-compatible endpoint>
--user-data-dir=<account isolated browser profile>
```

## Install From Source / 从源码运行

Requirements:

- Windows
- Python 3.10 or newer
- Codex App installed

Run:

```powershell
git clone https://github.com/<your-name>/codex-switchboard.git
cd codex-switchboard
python -m pip install -r requirements.txt
python app.py
```

## Build EXE / 构建 EXE

```powershell
.\build.ps1
```

Output:

```text
dist\Codex Switchboard.exe
```

You can then copy the EXE anywhere, for example to the Windows desktop.

## Basic Usage / 基本用法

1. Open Codex App normally and sign in if you want to save a ChatGPT account.
2. Open Codex Switchboard.
3. For a ChatGPT account, choose `ChatGPT`, enter a profile name, then click `Save Account`.
4. For an API account, choose `API`, enter a profile name and API key, optionally set Org ID, Project ID, or Base URL, then click `Save Account`.
5. Select an account and click `Launch Selected`.
6. Use `Account Inheritance` to copy local state from one account to another.
7. Use `Project Library` to move one project or one conversation into a selected account.

## Safety Notes / 安全说明

- The app stores secrets only on your Windows machine.
- Saved secrets are encrypted with Windows DPAPI, which ties decryption to the current Windows user.
- Do not publish or share `%APPDATA%\CodexSwitchboard`.
- Do not commit local Codex state, API keys, `auth.json`, browser profiles, or generated `.dpapi` files.
- Project transfer copies local Codex session files. It does not transfer account identity unless you explicitly save or inherit local state.

## Limits / 限制

- Windows only for now.
- The tool depends on Codex App's local storage layout, so future Codex App updates may require adjustments.
- After transferring projects, restart or relaunch the target Codex account if the sidebar does not refresh immediately.
- API profiles rely on environment variables. If Codex App changes how API-key auth is read, the launcher may need an update.

## Development / 开发

Quick checks:

```powershell
python -m py_compile app.py
python app.py
```

Build:

```powershell
.\build.ps1
```

## License / 许可证

MIT. See [LICENSE](LICENSE).
