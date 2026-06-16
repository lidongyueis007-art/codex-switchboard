import ctypes
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from ctypes import wintypes
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import END, Entry, Frame, Listbox, Scrollbar, StringVar, Text, Tk, filedialog, messagebox, simpledialog, ttk


APP_NAME = "Codex Switchboard"
APP_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "CodexSwitchboard"
PROFILE_DIR = APP_DIR / "profiles"
INSTANCE_DIR = APP_DIR / "instances"
SETTINGS_FILE = APP_DIR / "settings.json"
DEFAULT_CODEX_HOME = Path.home() / ".codex"
DEFAULT_AUTH_FILE = DEFAULT_CODEX_HOME / "auth.json"

PROFILE_CHATGPT = "chatgpt"
PROFILE_API = "api"
OPENAI_ENV_VARS = (
    "OPENAI_API_KEY",
    "CODEX_API_KEY",
    "OPENAI_ORG_ID",
    "OPENAI_ORGANIZATION",
    "OPENAI_PROJECT_ID",
    "OPENAI_BASE_URL",
)

TEXT = {
    "en": {
        "refresh": "Refresh",
        "language": "中文",
        "subtitle": "Multi-account launcher + inheritance console. Supports ChatGPT auth and API key accounts.",
        "account_launcher": "Account Launcher",
        "launcher_help": "Select an account and launch an isolated Codex window.",
        "launch_selected": "Launch Selected",
        "set_default": "Set As Default",
        "open_instance": "Open Instance Folder",
        "sync_login": "Sync Refreshed Login",
        "account_manager": "Account Manager",
        "name": "Name",
        "type": "Type",
        "api_key": "API Key (only for API accounts)",
        "org_project": "Org ID / Project ID (optional)",
        "base_url": "Base URL (optional, OpenAI-compatible endpoint)",
        "save_account": "Save Account",
        "import_auth": "Import auth.json",
        "export_selected": "Export Selected",
        "rename_selected": "Rename Selected",
        "delete_selected": "Delete Selected",
        "detect_codex": "Detect Codex Path",
        "inheritance": "Account Inheritance",
        "inherit_help": "Copy local state from A to B, while preserving B's identity: auth.json for ChatGPT, API key for API accounts.",
        "source_a": "Source A",
        "target_b": "Target B",
        "inherit": "Inherit",
        "no_accounts": "No accounts yet. Save current login, import auth.json, or add an API key.",
        "loaded_accounts": "Loaded {count} account(s)",
        "select_account": "Select an account first.",
        "select_source_target": "Select source and target accounts.",
        "same_account": "Source and target cannot be the same account.",
        "account_name": "Account name:",
        "new_account_name": "New account name:",
        "choose_export": "Choose export folder",
        "delete_confirm": "Delete selected account snapshot?\n\nThe instance folder will be kept.",
        "inherit_confirm": "Inherit local state?\n\n{source} -> {target}\n\nThe target identity will be preserved.",
        "saved": "Saved account: {name} ({kind})",
        "imported": "Imported account: {name}",
        "exported": "Exported: {path}",
        "renamed": "Renamed account: {name}",
        "deleted": "Deleted selected account snapshot",
        "default_switched": "Default Codex auth switched to: {name}",
        "launched": "Launched {name} ({kind}) with CODEX_HOME={home}",
        "launch_warning": "Launch may have been swallowed by Codex single-instance behavior. No new live Codex process was detected.",
        "synced_login": "Synced refreshed ChatGPT login back to snapshot: {name}",
        "inherited": "Inherited {count} item(s): {source} -> {target}",
        "skipped": "Skipped: {items}",
        "detected": "Detected Codex.exe: {path}",
        "library": "Project Library",
        "library_help": "Browse projects and conversations from the default Codex home, then move one project or one conversation into any account.",
        "library_source": "All Projects / Conversations",
        "library_target": "Target Account",
        "transfer_selected": "Transfer Selected",
        "transfer_confirm": "Transfer selected item?\n\n{item}\n-> {target}",
        "transfer_done": "Transferred {count} conversation(s) to {target}",
        "select_library_item": "Select a project or conversation first.",
    },
    "zh": {
        "refresh": "刷新",
        "language": "English",
        "subtitle": "多账号启动器 + 账号状态继承控制台，支持 ChatGPT 登录和 API Key 账号。",
        "account_launcher": "账号启动",
        "launcher_help": "选择一个账号，启动独立的 Codex 窗口。",
        "launch_selected": "启动选中账号",
        "set_default": "设为默认账号",
        "open_instance": "打开实例目录",
        "sync_login": "同步刷新登录态",
        "account_manager": "账号管理",
        "name": "名称",
        "type": "类型",
        "api_key": "API Key（仅 API 账号使用）",
        "org_project": "Org ID / Project ID（可选）",
        "base_url": "Base URL（可选，OpenAI 兼容接口）",
        "save_account": "保存账号",
        "import_auth": "导入 auth.json",
        "export_selected": "导出选中账号",
        "rename_selected": "重命名选中账号",
        "delete_selected": "删除选中账号",
        "detect_codex": "检测 Codex 路径",
        "inheritance": "账号继承",
        "inherit_help": "把 A 的本地状态复制到 B，同时保留 B 的身份：ChatGPT 保留 auth.json，API 保留密钥。",
        "source_a": "来源 A",
        "target_b": "目标 B",
        "inherit": "执行继承",
        "no_accounts": "还没有账号。可以保存当前登录、导入 auth.json，或添加 API Key。",
        "loaded_accounts": "已载入 {count} 个账号",
        "select_account": "请先选择一个账号。",
        "select_source_target": "请选择来源账号和目标账号。",
        "same_account": "来源和目标不能是同一个账号。",
        "account_name": "账号名称：",
        "new_account_name": "新的账号名称：",
        "choose_export": "选择导出目录",
        "delete_confirm": "删除选中的账号快照？\n\n实例目录会保留，避免误删运行数据。",
        "inherit_confirm": "确认继承本地状态？\n\n{source} -> {target}\n\n目标账号身份会被保留。",
        "saved": "已保存账号：{name}（{kind}）",
        "imported": "已导入账号：{name}",
        "exported": "已导出：{path}",
        "renamed": "已重命名账号：{name}",
        "deleted": "已删除选中的账号快照",
        "default_switched": "默认 Codex 登录已切换到：{name}",
        "launched": "已启动 {name}（{kind}），CODEX_HOME={home}",
        "launch_warning": "这次启动可能被 Codex 单实例机制吞掉了：没有检测到新的存活 Codex 进程。",
        "synced_login": "已把刷新的 ChatGPT 登录态同步回快照：{name}",
        "inherited": "已继承 {count} 项：{source} -> {target}",
        "skipped": "已跳过：{items}",
        "detected": "已检测到 Codex.exe：{path}",
        "library": "项目大全",
        "library_help": "从默认 Codex 读取所有项目和对话，把某个项目或某个对话放到任意账号下面。",
        "library_source": "全部项目 / 对话",
        "library_target": "目标账号",
        "transfer_selected": "迁移选中项",
        "transfer_confirm": "确认迁移选中项？\n\n{item}\n-> {target}",
        "transfer_done": "已迁移 {count} 个对话到 {target}",
        "select_library_item": "请先选择一个项目或对话。",
    },
}

EXCLUDED_INHERIT_NAMES = {
    "auth.json",
    "auth.json.backup",
    "auth.json.bak",
    ".sandbox-secrets",
    ".tmp",
    "tmp",
    "node_repl",
    "logs_2.sqlite",
}


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def ensure_dirs():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return fallback


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def set_toml_root_string(path: Path, key: str, value: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines() if path.exists() else []
    replacement = f'{key} = "{value}"'
    updated = []
    replaced = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key} ") or stripped.startswith(f"{key}="):
            updated.append(replacement)
            replaced = True
        else:
            updated.append(line)
    if not replaced:
        updated.append(replacement)
    path.write_text("\n".join(updated).rstrip() + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    cleaned = []
    for ch in value.strip().lower():
        if ch.isalnum():
            cleaned.append(ch)
        elif ch in (" ", "-", "_", ".", "@"):
            cleaned.append("-")
    slug = "".join(cleaned).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "account"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def current_auth_digest():
    if not DEFAULT_AUTH_FILE.exists():
        return None
    return sha256(DEFAULT_AUTH_FILE.read_bytes())


def detect_auth_label(auth_data: bytes) -> str:
    try:
        data = json.loads(auth_data.decode("utf-8"))
    except Exception:
        return "Unknown account"
    candidates = []
    for key in ("email", "account_email", "user_email"):
        if isinstance(data.get(key), str):
            candidates.append(data[key])
    for value in data.values():
        if isinstance(value, dict):
            for key in ("email", "account_email", "user_email"):
                if isinstance(value.get(key), str):
                    candidates.append(value[key])
    return candidates[0] if candidates else "Codex account"


def masked_key(value: str) -> str:
    value = value.strip()
    if len(value) <= 12:
        return "*" * len(value)
    return f"{value[:7]}...{value[-4:]}"


class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def _blob_from_bytes(data: bytes):
    buffer = ctypes.create_string_buffer(data)
    return DATA_BLOB(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte))), buffer


def protect_bytes(data: bytes) -> bytes:
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    in_blob, _ = _blob_from_bytes(data)
    out_blob = DATA_BLOB()
    if not crypt32.CryptProtectData(ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(out_blob.pbData, out_blob.cbData)
    finally:
        kernel32.LocalFree(out_blob.pbData)


def unprotect_bytes(data: bytes) -> bytes:
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    in_blob, _ = _blob_from_bytes(data)
    out_blob = DATA_BLOB()
    if not crypt32.CryptUnprotectData(ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(out_blob.pbData, out_blob.cbData)
    finally:
        kernel32.LocalFree(out_blob.pbData)


@dataclass
class Profile:
    key: str
    name: str
    label: str
    kind: str
    created_at: str
    updated_at: str
    sha256: str


@dataclass
class ConversationItem:
    id: str
    title: str
    updated_at: str
    project: str
    session_files: list
    index_lines: list


@dataclass
class LibraryRow:
    kind: str
    label: str
    project: str
    conversation_id: str = ""


def profile_from_dict(data) -> Profile:
    return Profile(
        key=data["key"],
        name=data["name"],
        label=data.get("label", "Codex account"),
        kind=data.get("kind", PROFILE_CHATGPT),
        created_at=data.get("created_at", now_iso()),
        updated_at=data.get("updated_at", now_iso()),
        sha256=data.get("sha256", ""),
    )


class Store:
    def __init__(self):
        ensure_dirs()
        self.settings = read_json(SETTINGS_FILE, {"last_profile": None, "language": "zh"})
        if self.settings.get("language") not in TEXT:
            self.settings["language"] = "zh"

    def set_language(self, language: str):
        self.settings["language"] = language
        write_json(SETTINGS_FILE, self.settings)

    def profile_dir(self, key: str) -> Path:
        return PROFILE_DIR / key

    def profile_meta_path(self, key: str) -> Path:
        return self.profile_dir(key) / "profile.json"

    def profile_secret_path(self, key: str) -> Path:
        return self.profile_dir(key) / "auth.dpapi"

    def api_secret_path(self, key: str) -> Path:
        return self.profile_dir(key) / "api.dpapi"

    def instance_dir(self, key: str) -> Path:
        return INSTANCE_DIR / key

    def codex_home(self, key: str) -> Path:
        return self.instance_dir(key) / "home"

    def browser_profile(self, key: str) -> Path:
        return self.instance_dir(key) / "browser"

    def list_profiles(self):
        profiles = []
        for meta_path in PROFILE_DIR.glob("*/profile.json"):
            data = read_json(meta_path, None)
            if data:
                profiles.append(profile_from_dict(data))
        profiles.sort(key=lambda item: item.updated_at, reverse=True)
        return profiles

    def get_profile(self, key: str):
        data = read_json(self.profile_meta_path(key), None)
        return profile_from_dict(data) if data else None

    def _next_key(self, name: str) -> str:
        base = slugify(name)
        key = base
        index = 2
        while self.profile_meta_path(key).exists():
            existing = read_json(self.profile_meta_path(key), {})
            if existing.get("name") == name:
                break
            key = f"{base}-{index}"
            index += 1
        return key

    def save_chatgpt_from_current_auth(self, name: str):
        if not DEFAULT_AUTH_FILE.exists():
            raise FileNotFoundError(f"Codex auth file not found: {DEFAULT_AUTH_FILE}")
        return self.save_chatgpt_from_bytes(name, DEFAULT_AUTH_FILE.read_bytes())

    def import_auth_file(self, path: str, name: str):
        return self.save_chatgpt_from_bytes(name, Path(path).read_bytes())

    def save_chatgpt_from_bytes(self, name: str, auth_data: bytes):
        json.loads(auth_data.decode("utf-8"))
        digest = sha256(auth_data)
        label = detect_auth_label(auth_data)
        key = self._next_key(name)
        old = read_json(self.profile_meta_path(key), {})
        profile = {
            "key": key,
            "name": name,
            "label": label,
            "kind": PROFILE_CHATGPT,
            "created_at": old.get("created_at", now_iso()),
            "updated_at": now_iso(),
            "sha256": digest,
        }
        self.profile_dir(key).mkdir(parents=True, exist_ok=True)
        self.profile_secret_path(key).write_bytes(protect_bytes(auth_data))
        write_json(self.profile_meta_path(key), profile)
        self.prepare_instance(key)
        self.settings["last_profile"] = key
        write_json(SETTINGS_FILE, self.settings)
        return profile_from_dict(profile)

    def save_api_profile(self, name: str, api_key: str, org_id: str = "", project_id: str = "", base_url: str = ""):
        api_key = api_key.strip()
        base_url = base_url.strip()
        if not api_key:
            raise ValueError("API key is required.")
        if base_url and not base_url.lower().startswith(("http://", "https://")):
            raise ValueError("Base URL must start with http:// or https://.")
        key = self._next_key(name)
        payload = {
            "api_key": api_key,
            "org_id": org_id.strip(),
            "project_id": project_id.strip(),
            "base_url": base_url,
            "saved_at": now_iso(),
        }
        old = read_json(self.profile_meta_path(key), {})
        profile = {
            "key": key,
            "name": name,
            "label": f"API {masked_key(api_key)}",
            "kind": PROFILE_API,
            "created_at": old.get("created_at", now_iso()),
            "updated_at": now_iso(),
            "sha256": sha256(api_key.encode("utf-8")),
        }
        self.profile_dir(key).mkdir(parents=True, exist_ok=True)
        self.api_secret_path(key).write_bytes(protect_bytes(json.dumps(payload).encode("utf-8")))
        write_json(self.profile_meta_path(key), profile)
        self.prepare_instance(key)
        self.settings["last_profile"] = key
        write_json(SETTINGS_FILE, self.settings)
        return profile_from_dict(profile)

    def auth_bytes(self, key: str) -> bytes:
        path = self.profile_secret_path(key)
        if not path.exists():
            raise FileNotFoundError("Selected ChatGPT account secret was not found.")
        return unprotect_bytes(path.read_bytes())

    def api_credentials(self, key: str):
        path = self.api_secret_path(key)
        if not path.exists():
            raise FileNotFoundError("Selected API account secret was not found.")
        return json.loads(unprotect_bytes(path.read_bytes()).decode("utf-8"))

    def sync_chatgpt_from_instance(self, key: str):
        profile = self.get_profile(key)
        if not profile:
            raise FileNotFoundError("Selected account metadata was not found.")
        if profile.kind != PROFILE_CHATGPT:
            raise ValueError("Only ChatGPT account snapshots can sync refreshed auth.json.")
        auth = self.codex_home(key) / "auth.json"
        if not auth.exists():
            raise FileNotFoundError("Instance auth.json was not found. Launch this account once first.")
        auth_data = auth.read_bytes()
        json.loads(auth_data.decode("utf-8"))
        self.profile_secret_path(key).write_bytes(protect_bytes(auth_data))
        data = read_json(self.profile_meta_path(key), {})
        data["label"] = detect_auth_label(auth_data)
        data["sha256"] = sha256(auth_data)
        data["updated_at"] = now_iso()
        write_json(self.profile_meta_path(key), data)
        return profile_from_dict(data)

    def prepare_instance(self, key: str):
        profile = self.get_profile(key)
        if not profile:
            raise FileNotFoundError("Selected account metadata was not found.")
        home = self.codex_home(key)
        browser = self.browser_profile(key)
        home.mkdir(parents=True, exist_ok=True)
        browser.mkdir(parents=True, exist_ok=True)
        if profile.kind == PROFILE_CHATGPT:
            auth = home / "auth.json"
            if not auth.exists():
                auth.write_bytes(self.auth_bytes(key))
        else:
            auth = home / "auth.json"
            if auth.exists():
                auth.unlink()
        config = home / "config.toml"
        if not config.exists() and (DEFAULT_CODEX_HOME / "config.toml").exists():
            shutil.copy2(DEFAULT_CODEX_HOME / "config.toml", config)
        set_toml_root_string(config, "preferred_auth_method", "chatgpt" if profile.kind == PROFILE_CHATGPT else "apikey")
        write_json(self.instance_dir(key) / "instance.json", {
            "profile_key": key,
            "profile_name": profile.name,
            "profile_kind": profile.kind,
            "codex_home": str(home),
            "browser_profile": str(browser),
            "prepared_at": now_iso(),
        })
        return home, browser

    def instance_meta(self, key: str):
        return read_json(self.instance_dir(key) / "instance.json", {})

    def record_launch(self, key: str, pid: int, detected_pids):
        data = self.instance_meta(key)
        data["last_launch_at"] = now_iso()
        data["last_launch_pid"] = pid
        data["last_detected_pids"] = sorted(int(item) for item in detected_pids)
        write_json(self.instance_dir(key) / "instance.json", data)

    def recorded_running_status(self, key: str):
        data = self.instance_meta(key)
        pids = set(data.get("last_detected_pids") or [])
        if data.get("last_launch_pid"):
            pids.add(data["last_launch_pid"])
        live = sorted(pid for pid in pids if process_is_alive(pid))
        if live:
            return f"running:{','.join(str(pid) for pid in live[:3])}"
        if data.get("last_launch_at"):
            return "last-launch-stopped"
        return "not-launched"

    def launch_env(self, key: str):
        profile = self.get_profile(key)
        env = os.environ.copy()
        env["CODEX_HOME"] = str(self.codex_home(key))
        env["CODEX_DISABLE_UPDATE_CHECK"] = "1"
        for name in OPENAI_ENV_VARS:
            env.pop(name, None)
        if profile and profile.kind == PROFILE_API:
            creds = self.api_credentials(key)
            env["OPENAI_API_KEY"] = creds["api_key"]
            if creds.get("org_id"):
                env["OPENAI_ORG_ID"] = creds["org_id"]
                env["OPENAI_ORGANIZATION"] = creds["org_id"]
            if creds.get("project_id"):
                env["OPENAI_PROJECT_ID"] = creds["project_id"]
            if creds.get("base_url"):
                env["OPENAI_BASE_URL"] = creds["base_url"]
        return env

    def rename_profile(self, key: str, new_name: str):
        data = read_json(self.profile_meta_path(key), None)
        if not data:
            raise FileNotFoundError("Selected account metadata was not found.")
        data["name"] = new_name.strip()
        data["updated_at"] = now_iso()
        write_json(self.profile_meta_path(key), data)
        return profile_from_dict(data)

    def delete_profile(self, key: str, delete_instance=False):
        if self.profile_dir(key).exists():
            shutil.rmtree(self.profile_dir(key))
        if delete_instance and self.instance_dir(key).exists():
            shutil.rmtree(self.instance_dir(key))

    def export_profile(self, key: str, directory: str):
        profile = self.get_profile(key)
        if not profile:
            raise FileNotFoundError("Selected account metadata was not found.")
        out_dir = Path(directory)
        out_dir.mkdir(parents=True, exist_ok=True)
        if profile.kind == PROFILE_CHATGPT:
            out = out_dir / f"{slugify(profile.name)}.auth.json"
            out.write_bytes(self.auth_bytes(key))
            return out
        creds = self.api_credentials(key)
        out = out_dir / f"{slugify(profile.name)}.api-account.json"
        out.write_text(json.dumps({
            "name": profile.name,
            "kind": profile.kind,
            "api_key": creds["api_key"],
            "org_id": creds.get("org_id", ""),
            "project_id": creds.get("project_id", ""),
            "base_url": creds.get("base_url", ""),
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        return out

    def switch_default_auth(self, key: str):
        profile = self.get_profile(key)
        if not profile:
            raise FileNotFoundError("Selected account metadata was not found.")
        if profile.kind != PROFILE_CHATGPT:
            raise ValueError("Only ChatGPT auth snapshots can be switched into the default auth.json.")
        DEFAULT_CODEX_HOME.mkdir(parents=True, exist_ok=True)
        if DEFAULT_AUTH_FILE.exists():
            backup = APP_DIR / "backups"
            backup.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            shutil.copy2(DEFAULT_AUTH_FILE, backup / f"auth-before-switch-{stamp}.json")
        DEFAULT_AUTH_FILE.write_bytes(self.auth_bytes(key))
        return profile

    def inherit_state(self, source_key: str, target_key: str):
        if source_key == target_key:
            raise ValueError("Source and target cannot be the same account.")
        source_home, _ = self.prepare_instance(source_key)
        target_home, _ = self.prepare_instance(target_key)
        copied = 0
        skipped = []
        for item in source_home.iterdir():
            if item.name in EXCLUDED_INHERIT_NAMES or item.name.endswith(".lock"):
                skipped.append(item.name)
                continue
            destination = target_home / item.name
            try:
                if destination.exists():
                    if destination.is_dir():
                        shutil.rmtree(destination)
                    else:
                        destination.unlink()
                if item.is_dir():
                    shutil.copytree(item, destination, ignore=shutil.ignore_patterns("*.lock", "*.tmp", "Crashpad"))
                else:
                    shutil.copy2(item, destination)
                copied += 1
            except Exception as exc:
                skipped.append(f"{item.name} ({exc})")
        target = self.get_profile(target_key)
        if target and target.kind == PROFILE_CHATGPT:
            (target_home / "auth.json").write_bytes(self.auth_bytes(target_key))
        elif (target_home / "auth.json").exists():
            (target_home / "auth.json").unlink()
        write_json(self.instance_dir(target_key) / "inheritance.json", {
            "source": source_key,
            "target": target_key,
            "copied_items": copied,
            "skipped": skipped,
            "updated_at": now_iso(),
        })
        return copied, skipped

    def scan_library(self):
        index_path = DEFAULT_CODEX_HOME / "session_index.jsonl"
        index_by_id = {}
        if index_path.exists():
            for line in index_path.read_text(encoding="utf-8", errors="replace").splitlines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except Exception:
                    continue
                session_id = data.get("id")
                if not session_id:
                    continue
                index_by_id.setdefault(session_id, []).append(line)

        files_by_id = {}
        for root_name in ("sessions", "archived_sessions"):
            root = DEFAULT_CODEX_HOME / root_name
            if not root.exists():
                continue
            for path in root.rglob("*.jsonl"):
                session_id = self.session_id_from_file(path)
                if session_id:
                    files_by_id.setdefault(session_id, []).append(path)

        items = []
        all_ids = set(index_by_id) | set(files_by_id)
        for session_id in all_ids:
            index_lines = index_by_id.get(session_id, [])
            title = session_id
            updated_at = ""
            if index_lines:
                try:
                    data = json.loads(index_lines[-1])
                    title = data.get("thread_name") or title
                    updated_at = data.get("updated_at") or ""
                except Exception:
                    pass
            files = files_by_id.get(session_id, [])
            project = ""
            for file_path in files:
                meta = self.session_meta_from_file(file_path)
                project = meta.get("cwd") or project
                title = meta.get("thread_name") or title
                if project:
                    break
            if not project:
                project = "(unknown project)"
            items.append(ConversationItem(session_id, title, updated_at, project, files, index_lines))
        items.sort(key=lambda item: item.updated_at or "", reverse=True)
        return items

    def session_id_from_file(self, path: Path):
        stem = path.stem
        marker = "rollout-"
        if not stem.startswith(marker):
            return ""
        parts = stem.split("-")
        if len(parts) < 7:
            return ""
        return "-".join(parts[-5:])

    def session_meta_from_file(self, path: Path):
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                for _ in range(20):
                    line = handle.readline()
                    if not line:
                        break
                    try:
                        data = json.loads(line)
                    except Exception:
                        continue
                    if data.get("type") == "session_meta":
                        return data.get("payload", {})
        except Exception:
            return {}
        return {}

    def transfer_library_item(self, row: LibraryRow, target_key: str):
        self.prepare_instance(target_key)
        target_home = self.codex_home(target_key)
        all_items = self.scan_library()
        if row.kind == "project":
            selected = [item for item in all_items if item.project == row.project]
        else:
            selected = [item for item in all_items if item.id == row.conversation_id]
        if not selected:
            raise FileNotFoundError("Selected project/conversation was not found.")

        copied_ids = set()
        for item in selected:
            for source in item.session_files:
                try:
                    relative = source.relative_to(DEFAULT_CODEX_HOME)
                except ValueError:
                    relative = Path("sessions") / source.name
                destination = target_home / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            copied_ids.add(item.id)

        target_index = target_home / "session_index.jsonl"
        existing_ids = set()
        existing_lines = []
        if target_index.exists():
            for line in target_index.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.strip():
                    existing_lines.append(line)
                    try:
                        existing_ids.add(json.loads(line).get("id"))
                    except Exception:
                        pass
        add_lines = []
        for item in selected:
            if item.id in existing_ids:
                continue
            add_lines.extend(item.index_lines)
            if not item.index_lines:
                add_lines.append(json.dumps({
                    "id": item.id,
                    "thread_name": item.title,
                    "updated_at": item.updated_at or now_iso(),
                }, ensure_ascii=False))
        if add_lines:
            target_index.parent.mkdir(parents=True, exist_ok=True)
            target_index.write_text("\n".join(existing_lines + add_lines) + "\n", encoding="utf-8")

        write_json(self.instance_dir(target_key) / "last-transfer.json", {
            "item": row.__dict__,
            "target": target_key,
            "conversation_ids": sorted(copied_ids),
            "updated_at": now_iso(),
        })
        self.prepare_instance(target_key)
        return len(copied_ids)


def run_cmd(args, timeout=8):
    try:
        completed = subprocess.run(args, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, shell=False)
        return completed.returncode, completed.stdout.strip(), completed.stderr.strip()
    except Exception as exc:
        return 1, "", str(exc)


def codex_process_ids(codex_exe: str = ""):
    path_filter = ""
    if codex_exe:
        escaped = codex_exe.replace("'", "''")
        path_filter = f" | Where-Object {{ $_.Path -eq '{escaped}' }}"
    command = f"Get-Process Codex -ErrorAction SilentlyContinue{path_filter} | Select-Object -ExpandProperty Id"
    code, out, _ = run_cmd(["powershell", "-NoProfile", "-Command", command], timeout=6)
    if code != 0 or not out:
        return set()
    ids = set()
    for line in out.splitlines():
        try:
            ids.add(int(line.strip()))
        except ValueError:
            pass
    return ids


def process_is_alive(pid: int):
    if not pid:
        return False
    code, _, _ = run_cmd(["powershell", "-NoProfile", "-Command", f"Get-Process -Id {int(pid)} -ErrorAction SilentlyContinue | Out-Null"], timeout=4)
    return code == 0


def find_codex_exe() -> str:
    code, out, _ = run_cmd(["powershell", "-NoProfile", "-Command", "Get-Process Codex -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Path"], timeout=6)
    if code == 0 and out and Path(out.splitlines()[0]).exists():
        return out.splitlines()[0]
    code, out, _ = run_cmd(["powershell", "-NoProfile", "-Command", "(Get-AppxPackage OpenAI.Codex).InstallLocation"], timeout=8)
    if code == 0 and out:
        candidate = Path(out.splitlines()[0]) / "app" / "Codex.exe"
        if candidate.exists():
            return str(candidate)
    fallback = Path("C:/Program Files/WindowsApps")
    if fallback.exists():
        matches = sorted(fallback.glob("OpenAI.Codex_*_x64__*/app/Codex.exe"), reverse=True)
        if matches:
            return str(matches[0])
    raise FileNotFoundError("Could not locate Codex.exe. Start Codex once, then try again.")


def launch_codex_instance(codex_exe: str, browser_profile: Path, env):
    args = [codex_exe, f"--user-data-dir={browser_profile}"]
    return subprocess.Popen(args, cwd=str(Path.home()), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class SwitchboardApp:
    def __init__(self, root: Tk):
        self.root = root
        self.store = Store()
        self.lang = self.store.settings.get("language", "zh")
        self.profile_keys = []
        self.source_keys = []
        self.target_keys = []
        self.library_rows = []
        self.library_target_keys = []
        self.status = StringVar(value="")
        self.new_name = StringVar()
        self.account_type = StringVar(value="ChatGPT")
        self.api_key = StringVar()
        self.api_org = StringVar()
        self.api_project = StringVar()
        self.api_base_url = StringVar()
        self.codex_path = StringVar(value="")
        self.source_choice = StringVar()
        self.target_choice = StringVar()
        self.library_target_choice = StringVar()
        self._build_style()
        self._build_ui()
        self.refresh()

    def t(self, key: str, **kwargs) -> str:
        value = TEXT[self.lang].get(key, TEXT["en"].get(key, key))
        return value.format(**kwargs) if kwargs else value

    def _build_style(self):
        self.root.title(APP_NAME)
        self.root.geometry("1120x860")
        self.root.minsize(980, 760)
        self.root.configure(bg="#eef1f4")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#eef1f4")
        style.configure("Panel.TFrame", background="#ffffff", relief="flat")
        style.configure("Title.TLabel", background="#eef1f4", foreground="#20252b", font=("Segoe UI", 18, "bold"))
        style.configure("Sub.TLabel", background="#eef1f4", foreground="#68717c", font=("Segoe UI", 9))
        style.configure("PanelTitle.TLabel", background="#ffffff", foreground="#222831", font=("Segoe UI", 12, "bold"))
        style.configure("Body.TLabel", background="#ffffff", foreground="#59616b", font=("Segoe UI", 9))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.configure("TButton", font=("Segoe UI", 9), padding=(10, 6))

    def _panel(self, parent, row, column, **grid):
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        panel.grid(row=row, column=column, sticky="nsew", **grid)
        return panel

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=18)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        header = ttk.Frame(outer)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Codex Switchboard", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text=self.t("subtitle"), style="Sub.TLabel").grid(row=1, column=0, sticky="w", pady=(3, 0))
        ttk.Button(header, text=self.t("language"), command=self.toggle_language).grid(row=0, column=1, rowspan=2, sticky="e", padx=(0, 8))
        ttk.Button(header, text=self.t("refresh"), command=self.refresh).grid(row=0, column=2, rowspan=2, sticky="e")

        main = ttk.Frame(outer)
        main.grid(row=1, column=0, sticky="nsew")
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=2)
        main.rowconfigure(1, weight=1)
        main.rowconfigure(2, weight=2)

        accounts = self._panel(main, 0, 0, padx=(0, 12), pady=(0, 12))
        accounts.rowconfigure(2, weight=1)
        accounts.columnconfigure(0, weight=1)
        ttk.Label(accounts, text=self.t("account_launcher"), style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(accounts, text=self.t("launcher_help"), style="Body.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 12))
        list_frame = Frame(accounts, bg="#ffffff")
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.account_list = Listbox(list_frame, activestyle="none", borderwidth=0, highlightthickness=1, highlightbackground="#d6dbe1", font=("Segoe UI", 10), selectbackground="#1d4ed8", selectforeground="#ffffff")
        self.account_list.grid(row=0, column=0, sticky="nsew")
        scroll = Scrollbar(list_frame, orient="vertical", command=self.account_list.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.account_list.configure(yscrollcommand=scroll.set)

        account_buttons = ttk.Frame(accounts, style="Panel.TFrame")
        account_buttons.grid(row=3, column=0, sticky="ew", pady=(14, 0))
        account_buttons.columnconfigure((0, 1, 2, 3), weight=1)
        ttk.Button(account_buttons, text=self.t("launch_selected"), style="Primary.TButton", command=self.launch_selected).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(account_buttons, text=self.t("set_default"), command=self.switch_default).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(account_buttons, text=self.t("sync_login"), command=self.sync_selected_login).grid(row=0, column=2, sticky="ew", padx=4)
        ttk.Button(account_buttons, text=self.t("open_instance"), command=self.open_instance_folder).grid(row=0, column=3, sticky="ew", padx=(8, 0))

        manage = self._panel(main, 0, 1, pady=(0, 12))
        manage.columnconfigure(0, weight=1)
        ttk.Label(manage, text=self.t("account_manager"), style="PanelTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(manage, text=self.t("name"), style="Body.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 2))
        Entry(manage, textvariable=self.new_name, font=("Segoe UI", 10), relief="solid", borderwidth=1).grid(row=2, column=0, sticky="ew", ipady=5)
        ttk.Label(manage, text=self.t("type"), style="Body.TLabel").grid(row=3, column=0, sticky="w", pady=(8, 2))
        self.type_box = ttk.Combobox(manage, textvariable=self.account_type, state="readonly", values=["ChatGPT", "API"])
        self.type_box.grid(row=4, column=0, sticky="ew", ipady=3)
        ttk.Label(manage, text=self.t("api_key"), style="Body.TLabel").grid(row=5, column=0, sticky="w", pady=(8, 2))
        Entry(manage, textvariable=self.api_key, show="*", font=("Consolas", 9), relief="solid", borderwidth=1).grid(row=6, column=0, sticky="ew", ipady=5)
        ttk.Label(manage, text=self.t("org_project"), style="Body.TLabel").grid(row=7, column=0, sticky="w", pady=(8, 2))
        Entry(manage, textvariable=self.api_org, font=("Consolas", 9), relief="solid", borderwidth=1).grid(row=8, column=0, sticky="ew", ipady=4)
        Entry(manage, textvariable=self.api_project, font=("Consolas", 9), relief="solid", borderwidth=1).grid(row=9, column=0, sticky="ew", pady=(5, 0), ipady=4)
        ttk.Label(manage, text=self.t("base_url"), style="Body.TLabel").grid(row=10, column=0, sticky="w", pady=(8, 2))
        Entry(manage, textvariable=self.api_base_url, font=("Consolas", 9), relief="solid", borderwidth=1).grid(row=11, column=0, sticky="ew", ipady=4)
        ttk.Button(manage, text=self.t("save_account"), command=self.save_account).grid(row=12, column=0, sticky="ew", pady=(12, 4))
        ttk.Button(manage, text=self.t("import_auth"), command=self.import_auth).grid(row=13, column=0, sticky="ew", pady=4)
        ttk.Button(manage, text=self.t("export_selected"), command=self.export_selected).grid(row=14, column=0, sticky="ew", pady=4)
        ttk.Button(manage, text=self.t("rename_selected"), command=self.rename_selected).grid(row=15, column=0, sticky="ew", pady=4)
        ttk.Button(manage, text=self.t("delete_selected"), command=self.delete_selected).grid(row=16, column=0, sticky="ew", pady=4)
        ttk.Label(manage, text="Codex.exe", style="Body.TLabel").grid(row=17, column=0, sticky="w", pady=(12, 2))
        Entry(manage, textvariable=self.codex_path, font=("Consolas", 8), relief="solid", borderwidth=1).grid(row=18, column=0, sticky="ew", ipady=4)
        ttk.Button(manage, text=self.t("detect_codex"), command=self.detect_codex_path).grid(row=19, column=0, sticky="ew", pady=(7, 0))

        inherit = self._panel(main, 1, 0, columnspan=2)
        inherit.columnconfigure((0, 2), weight=1)
        ttk.Label(inherit, text=self.t("inheritance"), style="PanelTitle.TLabel").grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(inherit, text=self.t("inherit_help"), style="Body.TLabel").grid(row=1, column=0, columnspan=4, sticky="w", pady=(4, 14))
        ttk.Label(inherit, text=self.t("source_a"), style="Body.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Label(inherit, text=self.t("target_b"), style="Body.TLabel").grid(row=2, column=2, sticky="w")
        self.source_box = ttk.Combobox(inherit, textvariable=self.source_choice, state="readonly")
        self.source_box.grid(row=3, column=0, sticky="ew", padx=(0, 12), ipady=4)
        ttk.Label(inherit, text="->", style="PanelTitle.TLabel").grid(row=3, column=1, padx=10)
        self.target_box = ttk.Combobox(inherit, textvariable=self.target_choice, state="readonly")
        self.target_box.grid(row=3, column=2, sticky="ew", padx=(12, 12), ipady=4)
        ttk.Button(inherit, text=self.t("inherit"), style="Primary.TButton", command=self.inherit_clicked).grid(row=3, column=3, sticky="ew")
        log_panel = ttk.Frame(inherit, style="Panel.TFrame")
        log_panel.grid(row=4, column=0, columnspan=4, sticky="nsew", pady=(14, 0))
        log_panel.columnconfigure(0, weight=1)
        self.log = Text(log_panel, height=5, relief="solid", borderwidth=1, font=("Consolas", 9), wrap="word")
        self.log.grid(row=0, column=0, sticky="nsew")

        library = self._panel(main, 2, 0, columnspan=2, pady=(12, 0))
        library.columnconfigure(0, weight=3)
        library.columnconfigure(1, weight=0)
        library.columnconfigure(2, weight=2)
        library.rowconfigure(3, weight=1)
        ttk.Label(library, text=self.t("library"), style="PanelTitle.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Label(library, text=self.t("library_help"), style="Body.TLabel").grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 14))
        ttk.Label(library, text=self.t("library_source"), style="Body.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Label(library, text=self.t("library_target"), style="Body.TLabel").grid(row=2, column=2, sticky="w")
        lib_frame = Frame(library, bg="#ffffff")
        lib_frame.grid(row=3, column=0, sticky="nsew", padx=(0, 12))
        lib_frame.columnconfigure(0, weight=1)
        lib_frame.rowconfigure(0, weight=1)
        self.library_list = Listbox(lib_frame, activestyle="none", borderwidth=0, highlightthickness=1, highlightbackground="#d6dbe1", font=("Segoe UI", 10), selectbackground="#0f766e", selectforeground="#ffffff")
        self.library_list.grid(row=0, column=0, sticky="nsew")
        lib_scroll = Scrollbar(lib_frame, orient="vertical", command=self.library_list.yview)
        lib_scroll.grid(row=0, column=1, sticky="ns")
        self.library_list.configure(yscrollcommand=lib_scroll.set)
        ttk.Label(library, text="->", style="PanelTitle.TLabel").grid(row=3, column=1, padx=10)
        target_panel = ttk.Frame(library, style="Panel.TFrame")
        target_panel.grid(row=3, column=2, sticky="new")
        target_panel.columnconfigure(0, weight=1)
        self.library_target_box = ttk.Combobox(target_panel, textvariable=self.library_target_choice, state="readonly")
        self.library_target_box.grid(row=0, column=0, sticky="ew", ipady=4)
        ttk.Button(target_panel, text=self.t("transfer_selected"), style="Primary.TButton", command=self.transfer_selected_library).grid(row=1, column=0, sticky="ew", pady=(12, 0))

        footer = ttk.Frame(outer)
        footer.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self.status, style="Sub.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(footer, text=f"Data: {APP_DIR}", style="Sub.TLabel").grid(row=0, column=1, sticky="e")

    def log_line(self, message: str):
        stamp = datetime.now().strftime("%H:%M:%S")
        self.log.insert(END, f"[{stamp}] {message}\n")
        self.log.see(END)
        self.status.set(message)

    def toggle_language(self):
        log_text = self.log.get("1.0", END) if hasattr(self, "log") else ""
        self.lang = "en" if self.lang == "zh" else "zh"
        self.store.set_language(self.lang)
        for child in self.root.winfo_children():
            child.destroy()
        self._build_ui()
        if log_text.strip():
            self.log.insert("1.0", log_text)
        self.refresh()

    def detect_codex_path(self):
        try:
            path = find_codex_exe()
            self.codex_path.set(path)
            self.log_line(self.t("detected", path=path))
        except Exception as exc:
            self.log_line(str(exc))
            messagebox.showerror(APP_NAME, str(exc))

    def refresh(self):
        profiles = self.store.list_profiles()
        digest = current_auth_digest()
        self.profile_keys = []
        self.account_list.delete(0, END)
        if not profiles:
            self.account_list.insert(END, self.t("no_accounts"))
        for profile in profiles:
            if profile.kind == PROFILE_CHATGPT:
                active = "default" if digest and profile.sha256 == digest else "saved"
            else:
                active = "api-key"
            prepared = "ready" if (self.store.instance_dir(profile.key) / "instance.json").exists() else "new"
            running = self.store.recorded_running_status(profile.key)
            self.account_list.insert(END, f"{profile.name}    {profile.kind.upper()}    {profile.label}    [{active} / {prepared} / {running}]")
            self.profile_keys.append(profile.key)
        names = [f"{p.name} [{p.kind}] ({p.key})" for p in profiles]
        self.source_keys = [p.key for p in profiles]
        self.target_keys = [p.key for p in profiles]
        self.source_box.configure(values=names)
        self.target_box.configure(values=names)
        self.library_target_box.configure(values=names)
        if names and not self.source_choice.get():
            self.source_choice.set(names[0])
        if len(names) > 1 and not self.target_choice.get():
            self.target_choice.set(names[1])
        elif names and not self.target_choice.get():
            self.target_choice.set(names[0])
        if names and not self.library_target_choice.get():
            self.library_target_choice.set(names[0])
        if not self.codex_path.get():
            try:
                self.codex_path.set(find_codex_exe())
            except Exception:
                pass
        self.refresh_library()
        self.status.set(self.t("loaded_accounts", count=len(profiles)))

    def refresh_library(self):
        self.library_list.delete(0, END)
        self.library_rows = []
        items = self.store.scan_library()
        projects = {}
        for item in items:
            projects.setdefault(item.project, []).append(item)
        for project, conversations in sorted(projects.items(), key=lambda pair: max((c.updated_at or "" for c in pair[1]), default=""), reverse=True):
            label = f"[Project] {project}  ({len(conversations)})"
            self.library_rows.append(LibraryRow("project", label, project))
            self.library_list.insert(END, label)
            for conversation in conversations:
                title = conversation.title.replace("\n", " ")[:90]
                row_label = f"    - {title}"
                self.library_rows.append(LibraryRow("conversation", row_label, project, conversation.id))
                self.library_list.insert(END, row_label)

    def selected_key(self):
        selection = self.account_list.curselection()
        if not selection or selection[0] >= len(self.profile_keys):
            return None
        return self.profile_keys[selection[0]]

    def selected_combo_key(self, box: ttk.Combobox, keys):
        index = box.current()
        if index < 0 or index >= len(keys):
            return None
        return keys[index]

    def selected_library_row(self):
        selection = self.library_list.curselection()
        if not selection or selection[0] >= len(self.library_rows):
            return None
        return self.library_rows[selection[0]]

    def account_name_or_prompt(self):
        name = self.new_name.get().strip()
        if not name:
            name = simpledialog.askstring(APP_NAME, self.t("account_name"))
        return name.strip() if name else ""

    def save_account(self):
        name = self.account_name_or_prompt()
        if not name:
            return
        try:
            if self.account_type.get() == "API":
                profile = self.store.save_api_profile(name, self.api_key.get(), self.api_org.get(), self.api_project.get(), self.api_base_url.get())
                self.api_key.set("")
                self.api_org.set("")
                self.api_project.set("")
                self.api_base_url.set("")
            else:
                profile = self.store.save_chatgpt_from_current_auth(name)
            self.new_name.set("")
            self.log_line(self.t("saved", name=profile.name, kind=profile.kind))
            self.refresh()
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def import_auth(self):
        path = filedialog.askopenfilename(title=self.t("import_auth"), filetypes=[("auth.json", "auth.json"), ("JSON", "*.json"), ("All files", "*.*")])
        if not path:
            return
        default = Path(path).stem.replace(".auth", "")
        name = self.new_name.get().strip() or simpledialog.askstring(APP_NAME, self.t("account_name"), initialvalue=default)
        if not name:
            return
        try:
            profile = self.store.import_auth_file(path, name)
            self.new_name.set("")
            self.log_line(self.t("imported", name=profile.name))
            self.refresh()
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def export_selected(self):
        key = self.selected_key()
        if not key:
            messagebox.showwarning(APP_NAME, self.t("select_account"))
            return
        directory = filedialog.askdirectory(title=self.t("choose_export"))
        if not directory:
            return
        try:
            path = self.store.export_profile(key, directory)
            self.log_line(self.t("exported", path=path))
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def rename_selected(self):
        key = self.selected_key()
        if not key:
            messagebox.showwarning(APP_NAME, self.t("select_account"))
            return
        profile = self.store.get_profile(key)
        name = simpledialog.askstring(APP_NAME, self.t("new_account_name"), initialvalue=profile.name if profile else "")
        if not name:
            return
        try:
            self.store.rename_profile(key, name)
            self.log_line(self.t("renamed", name=name))
            self.refresh()
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def delete_selected(self):
        key = self.selected_key()
        if not key:
            messagebox.showwarning(APP_NAME, self.t("select_account"))
            return
        if not messagebox.askyesno(APP_NAME, self.t("delete_confirm")):
            return
        try:
            self.store.delete_profile(key, delete_instance=False)
            self.log_line(self.t("deleted"))
            self.refresh()
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def switch_default(self):
        key = self.selected_key()
        if not key:
            messagebox.showwarning(APP_NAME, self.t("select_account"))
            return
        try:
            profile = self.store.switch_default_auth(key)
            self.log_line(self.t("default_switched", name=profile.name))
            self.refresh()
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def sync_selected_login(self):
        key = self.selected_key()
        if not key:
            messagebox.showwarning(APP_NAME, self.t("select_account"))
            return
        try:
            profile = self.store.sync_chatgpt_from_instance(key)
            self.log_line(self.t("synced_login", name=profile.name))
            self.refresh()
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def launch_selected(self):
        key = self.selected_key()
        if not key:
            messagebox.showwarning(APP_NAME, self.t("select_account"))
            return
        try:
            codex_exe = self.codex_path.get().strip() or find_codex_exe()
            _, browser = self.store.prepare_instance(key)
            env = self.store.launch_env(key)
            profile = self.store.get_profile(key)
            before = codex_process_ids(codex_exe)
            proc = launch_codex_instance(codex_exe, browser, env)
            time.sleep(1.2)
            after = codex_process_ids(codex_exe)
            detected = after - before
            if process_is_alive(proc.pid):
                detected.add(proc.pid)
            self.store.record_launch(key, proc.pid, detected)
            self.log_line(self.t("launched", name=profile.name, kind=profile.kind, home=env["CODEX_HOME"]))
            if not detected:
                self.log_line(self.t("launch_warning"))
            self.refresh()
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def open_instance_folder(self):
        key = self.selected_key()
        if not key:
            messagebox.showwarning(APP_NAME, self.t("select_account"))
            return
        path = self.store.instance_dir(key)
        path.mkdir(parents=True, exist_ok=True)
        os.startfile(path)

    def inherit_clicked(self):
        source = self.selected_combo_key(self.source_box, self.source_keys)
        target = self.selected_combo_key(self.target_box, self.target_keys)
        if not source or not target:
            messagebox.showwarning(APP_NAME, self.t("select_source_target"))
            return
        s = self.store.get_profile(source)
        t = self.store.get_profile(target)
        if source == target:
            messagebox.showwarning(APP_NAME, self.t("same_account"))
            return
        if not messagebox.askyesno(APP_NAME, self.t("inherit_confirm", source=s.name, target=t.name)):
            return
        try:
            copied, skipped = self.store.inherit_state(source, target)
            self.log_line(self.t("inherited", count=copied, source=s.name, target=t.name))
            if skipped:
                self.log_line(self.t("skipped", items=", ".join(skipped[:8])))
            self.refresh()
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def transfer_selected_library(self):
        row = self.selected_library_row()
        if not row:
            messagebox.showwarning(APP_NAME, self.t("select_library_item"))
            return
        target = self.selected_combo_key(self.library_target_box, self.target_keys)
        if not target:
            messagebox.showwarning(APP_NAME, self.t("select_account"))
            return
        target_profile = self.store.get_profile(target)
        if not messagebox.askyesno(APP_NAME, self.t("transfer_confirm", item=row.label.strip(), target=target_profile.name if target_profile else target)):
            return
        try:
            count = self.store.transfer_library_item(row, target)
            self.log_line(self.t("transfer_done", count=count, target=target_profile.name if target_profile else target))
            self.refresh()
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))


def main():
    if sys.platform != "win32":
        print("Codex Switchboard currently supports Windows only.")
        sys.exit(1)
    root = Tk()
    SwitchboardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
