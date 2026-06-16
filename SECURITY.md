# Security / 安全

## English

Codex Switchboard is a local Windows utility. It does not run a hosted service and does not intentionally send saved account material anywhere.

Secrets are stored under `%APPDATA%\CodexSwitchboard` and encrypted with Windows DPAPI, which means they are intended to be decrypted only by the same Windows user profile.

Please do not share:

- `%APPDATA%\CodexSwitchboard`
- `.codex` folders
- `auth.json`
- `*.dpapi`
- API keys, screenshots containing keys, or copied browser profiles

If you discover a security issue, please open a private report if GitHub security advisories are enabled for the repository. Otherwise, contact the maintainer privately before publishing details.

## 中文

Codex 接力台是一个本地 Windows 工具。它不提供云端服务，也不会主动把保存的账号材料发送到第三方。

密钥保存在 `%APPDATA%\CodexSwitchboard` 下，并使用 Windows DPAPI 加密，通常只能由同一个 Windows 用户配置解密。

请不要分享：

- `%APPDATA%\CodexSwitchboard`
- `.codex` 文件夹
- `auth.json`
- `*.dpapi`
- API Key、包含密钥的截图、复制出来的浏览器配置目录

如果你发现安全问题，并且仓库启用了 GitHub Security Advisories，请优先私密报告。否则请先私下联系维护者，再公开细节。
