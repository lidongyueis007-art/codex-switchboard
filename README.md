# Codex Switchboard / Codex 接力台

Codex Switchboard is a Codex-only CCSwitch-style launcher for people who need multiple Codex API or ChatGPT configurations open at the same time. It keeps the product narrow: save API keys and API URLs, save ChatGPT account snapshots, launch multiple Codex windows, and relay projects between configurations.

Codex 接力台是一个只面向 Codex 的 CCSwitch 风格启动器，适合同时使用多个 Codex API 或 ChatGPT 配置的人。它刻意保持功能收窄：保存 API Key 和 API 地址、保存 ChatGPT 账号快照、多开 Codex 窗口，并把项目接力到另一个配置继续工作。

## Features / 功能

- **Codex-only configuration list / Codex 专用配置列表**: no provider marketplace, no generic AI gateway, only API and ChatGPT configurations for Codex.
- **API configuration / API 配置**: save a name, API key, API URL, and note.
- **ChatGPT configuration / ChatGPT 配置**: capture an existing Codex App ChatGPT login or import `auth.json`.
- **Codex multi-open / Codex 多开**: launch multiple Codex windows from different configurations.
- **Unified Projects / 统一项目**: relay one project or conversation into another configuration so work can continue after switching API or account.
- **Auth isolation / 鉴权隔离**: scrub global OpenAI environment variables before launch, then inject only the selected API profile's credentials.
- **Instance tracking / 实例追踪**: record launch PIDs and warn when Codex appears to swallow a launch through single-instance behavior.
- **Refreshed login sync / 刷新登录态同步**: keep live ChatGPT instance tokens from being overwritten, and sync refreshed `auth.json` back into the saved snapshot when needed.
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

Before each launch, Switchboard removes inherited OpenAI credential variables such as `OPENAI_API_KEY`, `CODEX_API_KEY`, `OPENAI_ORG_ID`, `OPENAI_PROJECT_ID`, and `OPENAI_BASE_URL`. This prevents a global API key on the Windows machine from silently taking over a ChatGPT account launch.

每次启动前，接力台都会先清理继承自系统环境的 OpenAI 凭证变量，例如 `OPENAI_API_KEY`、`CODEX_API_KEY`、`OPENAI_ORG_ID`、`OPENAI_PROJECT_ID` 和 `OPENAI_BASE_URL`。这样可以避免 Windows 机器上的全局 API Key 悄悄污染 ChatGPT 账号启动。

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
3. On `配置`, add an API configuration with name, API key, API URL, and note, or add a ChatGPT configuration from the current Codex login.
4. On `首页`, select a configuration and click `启动 Codex`.
5. Open another configuration the same way when you need multi-open.
6. On `统一项目`, relay a project or conversation into a target configuration when you want to continue with another API or account.

Do not use the model's own answer to decide whether a session is using ChatGPT login or API-key auth. The reliable signals are Codex App's account/status UI, the selected Switchboard profile type, the isolated instance folder, and the launch environment shown by this tool.

不要用模型自己的回答来判断当前到底走 ChatGPT 登录还是 API Key。可靠信号应该看 Codex App 的账号/状态界面、接力台里选中的账号类型、隔离实例目录，以及本工具生成的启动环境。

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
