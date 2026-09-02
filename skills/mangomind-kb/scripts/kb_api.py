#!/usr/bin/env python3
"""MangoMind knowledge-base CLI for agents.

Thin, dependency-free (stdlib only) client for the TagMango AI admin API that
backs the MangoMind dashboard. Every command prints JSON to stdout unless noted.

Exit codes:
  0  success
  1  API or usage error (message on stderr)
  2  not authenticated (no stored token, or the API answered 401)
  3  forbidden (the API answered 403 — the user lacks a permission)
  4  local validation failed (payload problems, printed as JSON on stdout)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import stat
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

CONFIG_DIR = Path(os.environ.get("MANGOMIND_CONFIG_DIR", Path.home() / ".config" / "mangomind"))
CONFIG_FILE = CONFIG_DIR / "config.json"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"

# Production MangoMind. Override per environment with `configure` or the env vars below.
DEFAULT_API_URL = "https://production.aiserver.tagmango.com"
DEFAULT_DASHBOARD_URL = "https://mangomind.tagmango.in"

# Fields of a knowledge-base document, in the order the dashboard renders them.
STRING_FIELDS = ("title", "description")
STRING_LIST_FIELDS = ("steps", "notes", "rules", "additionalGuide", "integrations", "plan")
SETTINGS_FIELD = "settings"
MEDIA_FIELD = "media"
CONTENT_FIELDS = (*STRING_FIELDS, *STRING_LIST_FIELDS, SETTINGS_FIELD, MEDIA_FIELD)
PAYLOAD_FIELDS = (*CONTENT_FIELDS, "productId")

# The backend re-chunks and re-embeds these when they appear in updatedFields.
# Mirrors TmKnowledgebaseChunkOfNodeType; the dashboard sends all of them on create.
CHUNK_FIELDS = ("title", "description", "steps", "notes", "rules", "integrations",
                "plan", "settings", "media", "additionalGuide")

OBJECT_ID_RE = re.compile(r"^[0-9a-fA-F]{24}$")
URL_RE = re.compile(r"^https?://[^\s]+$")
SYNONYM_TYPES = ("equivalent", "explicit")

EXIT_OK, EXIT_ERROR, EXIT_UNAUTH, EXIT_FORBIDDEN, EXIT_INVALID = 0, 1, 2, 3, 4


class CliError(Exception):
    def __init__(self, message: str, code: int = EXIT_ERROR):
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------- #
# Config and credentials
# --------------------------------------------------------------------------- #

def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        raise CliError(f"{path} is not valid JSON: {exc}")


def _write_private_json(path: Path, data: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def _normalize_origin(url: str) -> str:
    url = url.strip().rstrip("/")
    if url.endswith("/api"):
        url = url[: -len("/api")]
    if not url.startswith(("http://", "https://")):
        raise CliError(f"URL must start with http:// or https://: {url!r}")
    return url


def load_config() -> dict[str, str]:
    cfg = _read_json(CONFIG_FILE)
    api = os.environ.get("MANGOMIND_API_URL") or cfg.get("apiUrl") or DEFAULT_API_URL
    dash = os.environ.get("MANGOMIND_DASHBOARD_URL") or cfg.get("dashboardUrl") or DEFAULT_DASHBOARD_URL
    return {"apiUrl": api, "dashboardUrl": dash}


def require_api_url() -> str:
    api = load_config()["apiUrl"]
    if not api:
        raise CliError(
            "API URL not configured. Run: kb_api.py configure --api-url <origin> "
            "--dashboard-url <origin>  (or set MANGOMIND_API_URL)."
        )
    return api


def load_token() -> str | None:
    env = os.environ.get("MANGOMIND_TOKEN")
    if env:
        return env.strip()
    return _read_json(CREDENTIALS_FILE).get("token")


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #

def api_request(
    method: str,
    path: str,
    *,
    query: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    token: str | None = None,
    raw: bool = False,
    timeout: int = 60,
) -> Any:
    """Call the admin API. Returns the unwrapped `result` unless raw=True."""
    base = require_api_url() + "/api"
    url = base + path
    if query:
        clean = {k: v for k, v in query.items() if v not in (None, "", [])}
        if clean:
            url += "?" + urllib.parse.urlencode(clean, doseq=True)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        # Dev servers are often exposed through ngrok; harmless elsewhere.
        "ngrok-skip-browser-warning": "true",
    }
    auth = token if token is not None else load_token()
    if auth:
        headers["Authorization"] = f"Bearer {auth}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            payload = resp.read()
            if raw:
                return payload, content_type
            if not payload:
                return None
            parsed = json.loads(payload)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        message = detail
        try:
            parsed_err = json.loads(detail)
            message = parsed_err.get("message") or parsed_err.get("error") or detail
            if isinstance(message, list):
                message = "; ".join(str(m) for m in message)
        except json.JSONDecodeError:
            pass
        if exc.code == 401:
            raise CliError(
                f"Not authenticated ({message}). Run: kb_api.py login", EXIT_UNAUTH
            )
        if exc.code == 403:
            raise CliError(
                f"Forbidden ({message}). The signed-in user lacks a required permission; "
                "check `kb_api.py whoami`.",
                EXIT_FORBIDDEN,
            )
        raise CliError(f"HTTP {exc.code} {method} {path}: {message}")
    except urllib.error.URLError as exc:
        raise CliError(f"Could not reach {url}: {exc.reason}")
    if isinstance(parsed, dict) and "result" in parsed and "code" in parsed:
        return parsed["result"]
    return parsed


def emit(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


# --------------------------------------------------------------------------- #
# Auth commands
# --------------------------------------------------------------------------- #

def fetch_me(token: str | None = None) -> dict[str, Any]:
    me = api_request("GET", "/auth/me", token=token)
    if not isinstance(me, dict):
        raise CliError("Unexpected /auth/me response", EXIT_UNAUTH)
    return me


def summarize_user(me: dict[str, Any]) -> dict[str, Any]:
    access = me.get("mangoMindAccess") or {}
    perms = list(access.get("permissions") or [])
    is_admin = "admin" in perms
    return {
        "id": me.get("_id"),
        "name": me.get("name"),
        "email": me.get("email"),
        "permissions": perms,
        "isRestricted": bool(access.get("isRestricted") or me.get("isRestricted")),
        "can": {
            "viewFeatures": is_admin or "view:features" in perms,
            "writeFeatures": is_admin or "write:features" in perms,
        },
    }


def save_credentials(token: str, me: dict[str, Any]) -> dict[str, Any]:
    summary = summarize_user(me)
    _write_private_json(
        CREDENTIALS_FILE,
        {
            "token": token,
            "email": summary["email"],
            "name": summary["name"],
            "permissions": summary["permissions"],
            "apiUrl": load_config()["apiUrl"],
            "savedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        },
    )
    return summary


def cmd_configure(args: argparse.Namespace) -> int:
    cfg = _read_json(CONFIG_FILE)
    if args.api_url:
        cfg["apiUrl"] = _normalize_origin(args.api_url)
    if args.dashboard_url:
        cfg["dashboardUrl"] = _normalize_origin(args.dashboard_url)
    if args.api_url or args.dashboard_url:
        _write_private_json(CONFIG_FILE, cfg)
    effective = load_config()
    emit(
        {
            "configFile": str(CONFIG_FILE),
            "apiUrl": effective["apiUrl"],
            "dashboardUrl": effective["dashboardUrl"],
            "usingDefaults": effective["apiUrl"] == DEFAULT_API_URL
            and effective["dashboardUrl"] == DEFAULT_DASHBOARD_URL,
            "loggedIn": bool(load_token()),
        }
    )
    return EXIT_OK


def cmd_whoami(_: argparse.Namespace) -> int:
    if not load_token():
        raise CliError("No stored token. Run: kb_api.py login", EXIT_UNAUTH)
    emit(summarize_user(fetch_me()))
    return EXIT_OK


def cmd_logout(_: argparse.Namespace) -> int:
    existed = CREDENTIALS_FILE.exists()
    if existed:
        CREDENTIALS_FILE.unlink()
    emit({"loggedOut": existed})
    return EXIT_OK


LOGIN_PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>MangoMind CLI sign-in</title>
<style>
body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;max-width:640px;margin:48px auto;padding:0 20px;color:#111}
h1{font-size:22px}h2{font-size:16px;margin-top:32px}
code,pre{background:#f4f4f5;border-radius:6px;padding:2px 6px;font-size:13px}
pre{padding:12px;overflow:auto}
input,button,textarea{font:inherit;padding:10px;border:1px solid #ccc;border-radius:6px;width:100%%;box-sizing:border-box;margin-top:6px}
button{background:#111;color:#fff;border:0;cursor:pointer;margin-top:12px}
.muted{color:#666;font-size:14px}.ok{color:#15803d}.err{color:#b91c1c}
</style></head><body>
<h1>Sign in for the MangoMind CLI</h1>
<p class="muted">This page is served by <code>kb_api.py login</code> on your machine. Whatever you enter here goes only to this local script and then to <code>%(api)s</code>. It is never shown to the coding agent.</p>

<h2>Option A — sign in on the dashboard, then paste the token</h2>
<ol>
<li><a href="%(dashboard_login)s" target="_blank">Open the MangoMind dashboard</a> and sign in.</li>
<li>Open the browser console on the dashboard tab (Cmd/Ctrl+Shift+J) and run:<pre>copy(localStorage.getItem('authToken'))</pre>The token is now on your clipboard.</li>
<li>Paste it below.</li>
</ol>
<form method="post" action="/token">
<input type="hidden" name="state" value="%(state)s">
<textarea name="token" rows="4" placeholder="eyJhbGciOi..." required></textarea>
<button type="submit">Save token</button>
</form>

<h2>Option B — sign in here with your dashboard email and password</h2>
<form method="post" action="/login">
<input type="hidden" name="state" value="%(state)s">
<input type="email" name="email" placeholder="you@tagmango.com" required>
<input type="password" name="password" placeholder="Password" required>
<button type="submit">Sign in</button>
</form>
<p class="muted">The password is sent once to <code>%(api)s/api/auth/login</code> and discarded; only the resulting token is stored (<code>%(cred)s</code>).</p>
</body></html>"""

RESULT_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>MangoMind CLI</title>
<style>body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;max-width:640px;margin:48px auto;padding:0 20px}
.ok{color:#15803d}.err{color:#b91c1c}</style></head>
<body><h1 class="%(cls)s">%(title)s</h1><p>%(body)s</p>%(extra)s</body></html>"""


class LoginState:
    def __init__(self, state: str):
        self.state = state
        self.done = threading.Event()
        self.result: dict[str, Any] | None = None
        self.error: str | None = None


def _make_login_handler(login: LoginState, api_url: str, dashboard_login: str):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_: Any) -> None:  # silence request logs
            return

        def _send(self, status: int, html: str) -> None:
            data = html.encode()
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _finish(self, token: str) -> None:
            try:
                me = fetch_me(token)
                summary = save_credentials(token, me)
            except CliError as exc:
                self._send(
                    400,
                    RESULT_PAGE % {
                        "cls": "err",
                        "title": "Token rejected",
                        "body": str(exc),
                        "extra": '<p><a href="/">Try again</a></p>',
                    },
                )
                return
            login.result = summary
            self._send(
                200,
                RESULT_PAGE % {
                    "cls": "ok",
                    "title": "Signed in",
                    "body": f"Signed in as {summary['name']} ({summary['email']}). "
                            "You can close this tab and return to your agent.",
                    "extra": "",
                },
            )
            login.done.set()

        def _check_state(self, state: str | None) -> bool:
            if state != login.state:
                self._send(400, RESULT_PAGE % {
                    "cls": "err", "title": "Stale sign-in page",
                    "body": "This page belongs to an older login attempt. Re-run the login command.",
                    "extra": "",
                })
                return False
            return True

        def do_GET(self) -> None:  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/callback":
                q = urllib.parse.parse_qs(parsed.query)
                token = (q.get("token") or [""])[0]
                if not self._check_state((q.get("state") or [None])[0]):
                    return
                if not token:
                    self._send(400, RESULT_PAGE % {"cls": "err", "title": "Missing token",
                                                    "body": "No token in callback.", "extra": ""})
                    return
                self._finish(token)
                return
            self._send(200, LOGIN_PAGE % {
                "api": api_url,
                "dashboard_login": dashboard_login,
                "state": login.state,
                "cred": str(CREDENTIALS_FILE),
            })

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length") or 0)
            form = urllib.parse.parse_qs(self.rfile.read(length).decode())
            state = (form.get("state") or [None])[0]
            if not self._check_state(state):
                return
            if self.path == "/token":
                token = (form.get("token") or [""])[0].strip().strip('"')
                if token.lower().startswith("bearer "):
                    token = token[7:].strip()
                self._finish(token)
                return
            if self.path == "/login":
                email = (form.get("email") or [""])[0].strip()
                password = (form.get("password") or [""])[0]
                try:
                    result = api_request(
                        "POST", "/auth/login", body={"email": email, "password": password}, token=""
                    )
                except CliError as exc:
                    self._send(401, RESULT_PAGE % {
                        "cls": "err", "title": "Sign-in failed", "body": str(exc),
                        "extra": '<p><a href="/">Try again</a></p>',
                    })
                    return
                token = (result or {}).get("token") if isinstance(result, dict) else None
                if not token:
                    self._send(500, RESULT_PAGE % {"cls": "err", "title": "Sign-in failed",
                                                    "body": "No token in login response.", "extra": ""})
                    return
                self._finish(token)
                return
            self._send(404, RESULT_PAGE % {"cls": "err", "title": "Not found", "body": "", "extra": ""})

    return Handler


def cmd_login(args: argparse.Namespace) -> int:
    cfg = load_config()
    api_url = require_api_url()
    if args.token:
        summary = save_credentials(args.token.strip(), fetch_me(args.token.strip()))
        emit({"loggedIn": True, "user": summary, "credentialsFile": str(CREDENTIALS_FILE)})
        return EXIT_OK

    if not args.force and load_token():
        try:
            summary = summarize_user(fetch_me())
            emit({"loggedIn": True, "alreadyAuthenticated": True, "user": summary})
            return EXIT_OK
        except CliError:
            pass  # stored token is stale; continue with an interactive login

    login = LoginState(secrets.token_urlsafe(16))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), lambda *a: None)
    port = server.server_address[1]
    local_url = f"http://127.0.0.1:{port}/"
    callback = f"http://127.0.0.1:{port}/callback"
    dashboard_login = (
        f"{cfg['dashboardUrl']}/login?cli_callback={urllib.parse.quote(callback, safe='')}"
        f"&state={login.state}"
        if cfg["dashboardUrl"] else ""
    )
    server.RequestHandlerClass = _make_login_handler(login, api_url, dashboard_login)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    instructions = {
        "action": "USER_ACTION_REQUIRED",
        "message": "Open the local sign-in page, sign in on the dashboard, and paste the token "
                   "(or sign in with email and password on the local page).",
        "localSignInPage": local_url,
        "dashboardLogin": dashboard_login or None,
        "timeoutSeconds": args.timeout,
    }
    print(json.dumps(instructions, indent=2), file=sys.stderr, flush=True)
    if not args.no_browser:
        try:
            webbrowser.open(local_url)
        except Exception:  # pragma: no cover - headless environments
            pass

    finished = login.done.wait(timeout=args.timeout)
    server.shutdown()
    server.server_close()
    if not finished:
        raise CliError(
            f"Timed out after {args.timeout}s waiting for sign-in. Re-run `kb_api.py login` "
            "and complete the local sign-in page.",
            EXIT_UNAUTH,
        )
    emit({"loggedIn": True, "user": login.result, "credentialsFile": str(CREDENTIALS_FILE)})
    return EXIT_OK


# --------------------------------------------------------------------------- #
# Knowledge-base read commands
# --------------------------------------------------------------------------- #

def _slim(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "_id": doc.get("_id"),
        "title": doc.get("title"),
        "nodeType": doc.get("nodeType"),
        "product": doc.get("product"),
        "description": (doc.get("description") or "")[:160],
        "counts": {f: len(doc.get(f) or []) for f in (*STRING_LIST_FIELDS, SETTINGS_FIELD, MEDIA_FIELD)},
        "updatedAt": doc.get("updatedAt"),
    }


def cmd_products(args: argparse.Namespace) -> int:
    result = api_request("GET", "/features", query={
        "search": args.search, "page": args.page, "limit": args.limit, "searchWithId": args.id,
    })
    items = result.get("data", []) if isinstance(result, dict) else []
    emit({
        "total": result.get("total") if isinstance(result, dict) else None,
        "page": args.page, "limit": args.limit,
        "products": [d if args.full else _slim(d) for d in items],
    })
    return EXIT_OK


def cmd_features(args: argparse.Namespace) -> int:
    _require_object_id(args.product, "product id")
    result = api_request("GET", "/features", query={
        "productId": args.product, "search": args.search, "page": args.page, "limit": args.limit,
    })
    product = result.get("product") if isinstance(result, dict) else None
    items = result.get("data", []) if isinstance(result, dict) else []
    emit({
        "product": _slim(product) if product else None,
        "total": result.get("total") if isinstance(result, dict) else None,
        "page": args.page, "limit": args.limit,
        "features": [d if args.full else _slim(d) for d in items],
    })
    return EXIT_OK


def fetch_doc(doc_id: str) -> dict[str, Any]:
    _require_object_id(doc_id, "id")
    doc = api_request("GET", f"/features/info/{doc_id}")
    if not isinstance(doc, dict):
        raise CliError(f"Unexpected response for {doc_id}")
    return doc


def cmd_get(args: argparse.Namespace) -> int:
    emit(fetch_doc(args.id))
    return EXIT_OK


def cmd_search(args: argparse.Namespace) -> int:
    result = api_request("GET", "/features/search", query={
        "searchTerm": args.term, "page": args.page, "limit": args.limit,
    })
    items = result.get("data", []) if isinstance(result, dict) else []
    out = []
    for d in items:
        entry = _slim(d)
        entry["searchScore"] = d.get("searchScore")
        entry["matchedFields"] = [
            {"path": m.get("path"), "matchedText": m.get("matchedText"), "matchedWords": m.get("matchedWords")}
            for m in d.get("matchedFields") or []
        ]
        out.append(d if args.full else entry)
    emit({
        "total": result.get("total") if isinstance(result, dict) else None,
        "page": args.page, "limit": args.limit, "results": out,
    })
    return EXIT_OK


def cmd_export(args: argparse.Namespace) -> int:
    payload, _ = api_request("GET", "/features/export", query={"productId": args.product}, raw=True)
    out = Path(args.out)
    out.write_bytes(payload)
    emit({"written": str(out), "bytes": len(payload)})
    return EXIT_OK


# --------------------------------------------------------------------------- #
# Payload validation, rendering, diffing
# --------------------------------------------------------------------------- #

def _require_object_id(value: str | None, label: str) -> None:
    if not value or not OBJECT_ID_RE.match(value):
        raise CliError(f"{label} must be a 24-character hex ObjectId, got {value!r}")


def load_payload(path: str) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text())
    except FileNotFoundError:
        raise CliError(f"Payload file not found: {path}")
    except json.JSONDecodeError as exc:
        raise CliError(f"Payload file is not valid JSON: {exc}")
    if not isinstance(data, dict):
        raise CliError("Payload must be a JSON object")
    return data


def validate_payload(payload: dict[str, Any], *, creating: bool) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    unknown = sorted(set(payload) - set(PAYLOAD_FIELDS) - {"_id", "nodeType", "product"})
    if unknown:
        errors.append(f"Unknown field(s): {', '.join(unknown)}. Allowed: {', '.join(PAYLOAD_FIELDS)}")

    for field in STRING_FIELDS:
        value = payload.get(field)
        if creating or field in payload:
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{field} is required and must be a non-empty string")
            elif value != value.strip():
                warnings.append(f"{field} has leading/trailing whitespace")
    title = payload.get("title")
    if isinstance(title, str) and len(title) > 120:
        warnings.append("title is longer than 120 characters; titles should read like a feature name")

    for field in STRING_LIST_FIELDS:
        if field not in payload:
            continue
        value = payload[field]
        if not isinstance(value, list):
            errors.append(f"{field} must be an array of strings")
            continue
        seen: set[str] = set()
        for idx, item in enumerate(value):
            if not isinstance(item, str) or not item.strip():
                errors.append(f"{field}[{idx}] must be a non-empty string")
                continue
            if item != item.strip():
                warnings.append(f"{field}[{idx}] has leading/trailing whitespace")
            if len(item) > 400:
                warnings.append(f"{field}[{idx}] is over 400 characters; split it — each item becomes one retrieval chunk")
            key = item.strip().lower()
            if key in seen:
                warnings.append(f"{field}[{idx}] duplicates an earlier item")
            seen.add(key)
        if field == "steps" and len(value) > 25:
            warnings.append("steps has more than 25 items; consider splitting the feature")

    if SETTINGS_FIELD in payload:
        value = payload[SETTINGS_FIELD]
        if not isinstance(value, list):
            errors.append("settings must be an array of {label, description}")
        else:
            for idx, item in enumerate(value):
                if not isinstance(item, dict) or set(item) - {"label", "description"}:
                    errors.append(f"settings[{idx}] must be an object with only label and description")
                    continue
                for key in ("label", "description"):
                    if not isinstance(item.get(key), str) or not item[key].strip():
                        errors.append(f"settings[{idx}].{key} must be a non-empty string")

    if MEDIA_FIELD in payload:
        value = payload[MEDIA_FIELD]
        if not isinstance(value, list):
            errors.append("media must be an array of {label, url}")
        else:
            for idx, item in enumerate(value):
                if not isinstance(item, dict) or set(item) - {"label", "url"}:
                    errors.append(f"media[{idx}] must be an object with only label and url")
                    continue
                if not isinstance(item.get("label"), str) or not item["label"].strip():
                    errors.append(f"media[{idx}].label must be a non-empty string")
                url = item.get("url")
                if not isinstance(url, str) or not URL_RE.match(url.strip()):
                    errors.append(f"media[{idx}].url must be an absolute http(s) URL")

    product_id = payload.get("productId")
    if product_id is not None and (not isinstance(product_id, str) or not OBJECT_ID_RE.match(product_id)):
        errors.append("productId must be a 24-character hex ObjectId (omit it for a product)")

    return {"errors": errors, "warnings": warnings}


def _normalize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """Project a server document or payload onto the writable payload shape."""
    out: dict[str, Any] = {}
    for field in STRING_FIELDS:
        out[field] = (doc.get(field) or "")
    for field in STRING_LIST_FIELDS:
        out[field] = list(doc.get(field) or [])
    out[SETTINGS_FIELD] = [
        {"label": s.get("label", ""), "description": s.get("description", "")}
        for s in (doc.get(SETTINGS_FIELD) or [])
    ]
    out[MEDIA_FIELD] = [
        {"label": m.get("label", ""), "url": m.get("url", "")} for m in (doc.get(MEDIA_FIELD) or [])
    ]
    product = doc.get("productId") or doc.get("product")
    if isinstance(product, dict):
        product = product.get("_id")
    out["productId"] = str(product) if product else None
    return out


def render_markdown(doc: dict[str, Any]) -> str:
    """Markdown preview in the dashboard's structure (title, description, sections)."""
    norm = _normalize_doc(doc)
    kind = "Feature" if norm["productId"] else "Product"
    lines = [f"## {norm['title'] or '(untitled)'}", ""]
    meta = f"_{kind}_"
    if doc.get("_id"):
        meta += f" · id `{doc['_id']}`"
    if norm["productId"]:
        meta += f" · product `{norm['productId']}`"
    lines += [meta, ""]
    if norm["description"]:
        lines += [norm["description"], ""]

    def section(title: str, items: list[str], ordered: bool = False) -> None:
        if not items:
            return
        lines.extend([f"### {title}", "", "---", ""])
        for idx, item in enumerate(items, 1):
            lines.append(f"{idx}. {item}" if ordered else f"- {item}")
        lines.append("")

    section("Steps", norm["steps"], ordered=True)
    section("Notes", norm["notes"])
    section("Integrations", norm["integrations"])
    section("Rules", norm["rules"])
    section("Media", [f"[{m['label']}]({m['url']})" for m in norm["media"]])
    section("Settings", [f"{s['label']}: {s['description']}" for s in norm["settings"]])
    section("Additional Guide", norm["additionalGuide"])
    section("Plan", norm["plan"])
    return "\n".join(lines).rstrip() + "\n"


def cmd_render(args: argparse.Namespace) -> int:
    if args.file:
        doc = load_payload(args.file)
    elif args.id:
        doc = fetch_doc(args.id)
    else:
        raise CliError("render needs --file or --id")
    sys.stdout.write(render_markdown(doc))
    return EXIT_OK


def cmd_validate(args: argparse.Namespace) -> int:
    payload = load_payload(args.file)
    report = validate_payload(payload, creating=not args.id)
    emit(report)
    return EXIT_INVALID if report["errors"] else EXIT_OK


def _list_diff(old: list[Any], new: list[Any], key=lambda x: x) -> dict[str, Any]:
    old_keys = [key(x) for x in old]
    new_keys = [key(x) for x in new]
    removed = [x for x in old if key(x) not in new_keys]
    added = [x for x in new if key(x) not in old_keys]
    kept_old = [k for k in old_keys if k in new_keys]
    kept_new = [k for k in new_keys if k in old_keys]
    return {
        "changed": old != new,
        "added": added,
        "removed": removed,
        "reordered": kept_old != kept_new,
        "oldCount": len(old),
        "newCount": len(new),
    }


def compute_diff(current: dict[str, Any], desired: dict[str, Any]) -> dict[str, Any]:
    old = _normalize_doc(current)
    new = _normalize_doc(desired)
    fields: dict[str, Any] = {}
    for field in STRING_FIELDS:
        if old[field] != new[field]:
            fields[field] = {"changed": True, "old": old[field], "new": new[field]}
    for field in STRING_LIST_FIELDS:
        d = _list_diff(old[field], new[field])
        if d["changed"]:
            fields[field] = d
    d = _list_diff(old[SETTINGS_FIELD], new[SETTINGS_FIELD], key=lambda s: json.dumps(s, sort_keys=True))
    if d["changed"]:
        fields[SETTINGS_FIELD] = d
    d = _list_diff(old[MEDIA_FIELD], new[MEDIA_FIELD], key=lambda m: json.dumps(m, sort_keys=True))
    if d["changed"]:
        fields[MEDIA_FIELD] = d
    if old["productId"] != new["productId"]:
        fields["productId"] = {"changed": True, "old": old["productId"], "new": new["productId"]}
    updated_fields = [f for f in CHUNK_FIELDS if f in fields]
    return {"changedFields": fields, "updatedFields": updated_fields, "noChanges": not fields}


def diff_markdown(diff: dict[str, Any]) -> str:
    if diff["noChanges"]:
        return "No changes.\n"
    lines: list[str] = []
    for field, d in diff["changedFields"].items():
        lines.append(f"### {field}")
        if "old" in d and "new" in d:
            lines += [f"- old: {d['old']!r}", f"+ new: {d['new']!r}", ""]
            continue
        for item in d.get("removed", []):
            lines.append(f"- {json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else item}")
        for item in d.get("added", []):
            lines.append(f"+ {json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else item}")
        if d.get("reordered"):
            lines.append("~ order changed")
        lines.append(f"  ({d['oldCount']} → {d['newCount']} items)")
        lines.append("")
    lines.append(f"Re-embedded sections (updatedFields): {', '.join(diff['updatedFields']) or 'none'}")
    return "\n".join(lines) + "\n"


def merge_for_update(current: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """Start from the stored document; override only the keys present in the payload."""
    merged = _normalize_doc(current)
    for key, value in payload.items():
        if key in PAYLOAD_FIELDS:
            merged[key] = value
    return merged


def cmd_diff(args: argparse.Namespace) -> int:
    current = fetch_doc(args.id)
    desired = merge_for_update(current, load_payload(args.file))
    diff = compute_diff(current, desired)
    if args.json:
        emit(diff)
    else:
        sys.stdout.write(diff_markdown(diff))
    return EXIT_OK


# --------------------------------------------------------------------------- #
# Knowledge-base write commands
# --------------------------------------------------------------------------- #

def build_request_body(desired: dict[str, Any], updated_fields: list[str]) -> dict[str, Any]:
    norm = _normalize_doc(desired)
    body: dict[str, Any] = {
        # The server derives the real nodeType from productId; this is just DTO validation.
        "nodeType": "Feature" if norm["productId"] else "Product",
        "title": norm["title"],
        "description": norm["description"],
        "steps": norm["steps"],
        "notes": norm["notes"],
        "rules": norm["rules"],
        "additionalGuide": norm["additionalGuide"],
        "integrations": norm["integrations"],
        "plan": norm["plan"],
        "settings": norm["settings"],
        "media": norm["media"],
        "updatedFields": updated_fields,
    }
    if norm["productId"]:
        body["productId"] = norm["productId"]
    return body


def cmd_upsert(args: argparse.Namespace) -> int:
    payload = load_payload(args.file)
    creating = not args.id
    if creating:
        desired = _normalize_doc(payload)
        report = validate_payload(payload, creating=True)
        updated_fields = list(CHUNK_FIELDS)
        diff = None
    else:
        current = fetch_doc(args.id)
        desired = merge_for_update(current, payload)
        report = validate_payload(desired, creating=True)
        diff = compute_diff(current, desired)
        updated_fields = diff["updatedFields"]

    if report["errors"]:
        emit({"valid": False, **report})
        return EXIT_INVALID

    if desired.get("productId"):
        parent = fetch_doc(desired["productId"])
        if parent.get("product"):
            raise CliError(
                f"productId {desired['productId']} points at a feature ('{parent.get('title')}'), "
                "not a product. Features can only live under a product."
            )

    if diff is not None and diff["noChanges"]:
        emit({"skipped": True, "reason": "no changes", "id": args.id})
        return EXIT_OK

    body = build_request_body(desired, updated_fields)
    if args.dry_run:
        emit({
            "dryRun": True,
            "method": "PUT",
            "path": "/features" + (f"?featureId={args.id}" if args.id else ""),
            "body": body,
            "warnings": report["warnings"],
            "diff": diff,
        })
        return EXIT_OK

    result = api_request("PUT", "/features", query={"featureId": args.id}, body=body)
    emit({
        "ok": True,
        "action": "created" if creating else "updated",
        "id": result.get("_id") if isinstance(result, dict) else None,
        "title": result.get("title") if isinstance(result, dict) else None,
        "nodeType": result.get("nodeType") if isinstance(result, dict) else None,
        "product": result.get("product") if isinstance(result, dict) else None,
        "updatedFields": updated_fields,
        "warnings": report["warnings"],
    })
    return EXIT_OK


def cmd_delete(args: argparse.Namespace) -> int:
    doc = fetch_doc(args.id)
    is_product = not doc.get("product")
    children = 0
    if is_product:
        listing = api_request("GET", "/features", query={"productId": args.id, "limit": 1})
        children = listing.get("total", 0) if isinstance(listing, dict) else 0
    if not args.yes:
        emit({
            "wouldDelete": {"id": args.id, "title": doc.get("title"),
                            "kind": "product" if is_product else "feature",
                            "featuresUnderIt": children if is_product else None},
            "message": "Refusing to delete without --yes. Confirm with the user first.",
        })
        return EXIT_ERROR
    api_request("DELETE", f"/features/{args.id}")
    emit({"ok": True, "deleted": {"id": args.id, "title": doc.get("title"),
                                  "kind": "product" if is_product else "feature",
                                  "featuresDeletedWithIt": children if is_product else 0}})
    return EXIT_OK


# --------------------------------------------------------------------------- #
# Synonym mappings
# --------------------------------------------------------------------------- #

def cmd_syn_list(args: argparse.Namespace) -> int:
    result = api_request("GET", "/synonym-mappings", query={
        "search": args.search, "mappingType": args.type, "canonical": args.canonical,
        "page": args.page, "limit": args.limit,
    })
    emit(result)
    return EXIT_OK


def cmd_syn_get(args: argparse.Namespace) -> int:
    _require_object_id(args.id, "id")
    emit(api_request("GET", f"/synonym-mappings/{args.id}"))
    return EXIT_OK


def _validate_synonym_body(canonical: str | None, synonyms: list[str] | None, mapping_type: str | None) -> list[str]:
    problems = []
    if canonical is not None and not canonical.strip():
        problems.append("canonical must be non-empty")
    if synonyms is not None:
        cleaned = [s.strip() for s in synonyms]
        if not cleaned or any(not s for s in cleaned):
            problems.append("every synonym must be a non-empty string")
        if len({s.lower() for s in cleaned}) != len(cleaned):
            problems.append("synonyms contain duplicates")
        if canonical and canonical.strip().lower() not in {s.lower() for s in cleaned}:
            problems.append("canonical must also appear in the synonyms list (dashboard convention)")
    if mapping_type is not None and mapping_type not in SYNONYM_TYPES:
        problems.append(f"mapping type must be one of {SYNONYM_TYPES}")
    return problems


def cmd_syn_create(args: argparse.Namespace) -> int:
    problems = _validate_synonym_body(args.canonical, args.synonym, args.type)
    if problems:
        emit({"valid": False, "errors": problems})
        return EXIT_INVALID
    body = {
        "mappingType": args.type,
        "canonical": args.canonical.strip(),
        "synonyms": [s.strip() for s in args.synonym],
    }
    if args.description:
        body["description"] = args.description.strip()
    if args.dry_run:
        emit({"dryRun": True, "method": "POST", "path": "/synonym-mappings", "body": body})
        return EXIT_OK
    emit(api_request("POST", "/synonym-mappings", body=body))
    return EXIT_OK


def cmd_syn_update(args: argparse.Namespace) -> int:
    _require_object_id(args.id, "id")
    current = api_request("GET", f"/synonym-mappings/{args.id}")
    canonical = args.canonical if args.canonical is not None else current.get("canonical")
    synonyms = args.synonym if args.synonym else current.get("synonyms")
    problems = _validate_synonym_body(canonical, synonyms, args.type)
    if problems:
        emit({"valid": False, "errors": problems})
        return EXIT_INVALID
    body: dict[str, Any] = {}
    if args.canonical is not None:
        body["canonical"] = args.canonical.strip()
    if args.synonym:
        body["synonyms"] = [s.strip() for s in args.synonym]
    if args.description is not None:
        body["description"] = args.description.strip()
    if args.type:
        body["mappingType"] = args.type
    if not body:
        raise CliError("Nothing to update; pass --canonical, --synonym, --description, or --type")
    if args.dry_run:
        emit({"dryRun": True, "method": "PUT", "path": f"/synonym-mappings/{args.id}", "body": body,
              "current": current})
        return EXIT_OK
    emit(api_request("PUT", f"/synonym-mappings/{args.id}", body=body))
    return EXIT_OK


def cmd_syn_delete(args: argparse.Namespace) -> int:
    _require_object_id(args.id, "id")
    current = api_request("GET", f"/synonym-mappings/{args.id}")
    if not args.yes:
        emit({"wouldDelete": current, "message": "Refusing to delete without --yes. Confirm with the user first."})
        return EXIT_ERROR
    emit(api_request("DELETE", f"/synonym-mappings/{args.id}"))
    return EXIT_OK


# --------------------------------------------------------------------------- #
# CLI wiring
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kb_api.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("configure", help="Set or show the API and dashboard origins")
    p.add_argument("--api-url", help="API origin, e.g. https://ai-api.example.com (without /api)")
    p.add_argument("--dashboard-url", help="Dashboard origin, e.g. https://mangomind.example.com")
    p.set_defaults(func=cmd_configure)

    p = sub.add_parser("login", help="Sign in through a local browser page; stores the admin token")
    p.add_argument("--timeout", type=int, default=300, help="Seconds to wait for the user (default 300)")
    p.add_argument("--port", type=int, default=0, help="Local port (default: random free port)")
    p.add_argument("--no-browser", action="store_true", help="Do not auto-open the browser")
    p.add_argument("--force", action="store_true", help="Sign in again even if a valid token is stored")
    p.add_argument("--token", help="Store this token directly (avoid: it lands in shell history)")
    p.set_defaults(func=cmd_login)

    sub.add_parser("whoami", help="Show the signed-in user and permissions").set_defaults(func=cmd_whoami)
    sub.add_parser("logout", help="Delete the stored token").set_defaults(func=cmd_logout)

    p = sub.add_parser("products", help="List top-level products")
    p.add_argument("--search", help="Case-insensitive title filter")
    p.add_argument("--id", help="Return only this product id")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--full", action="store_true", help="Return full documents instead of summaries")
    p.set_defaults(func=cmd_products)

    p = sub.add_parser("features", help="List features under a product")
    p.add_argument("--product", required=True, help="Product id")
    p.add_argument("--search", help="Case-insensitive title filter")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--full", action="store_true")
    p.set_defaults(func=cmd_features)

    p = sub.add_parser("get", help="Fetch one product or feature by id")
    p.add_argument("id")
    p.set_defaults(func=cmd_get)

    p = sub.add_parser("search", help="Full-text search across products and features (Atlas Search)")
    p.add_argument("term")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--full", action="store_true")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("export", help="Download the knowledge base as a .docx file")
    p.add_argument("--product", help="Export only this product and its features")
    p.add_argument("--out", required=True, help="Output path, e.g. knowledge-base.docx")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("render", help="Markdown preview of a payload file or a stored document")
    p.add_argument("--file", help="Payload JSON file")
    p.add_argument("--id", help="Stored document id")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("validate", help="Validate a payload file locally (no network)")
    p.add_argument("--file", required=True)
    p.add_argument("--id", help="Treat as an update of this id (relaxes required fields)")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("diff", help="Show what an update payload would change on a stored document")
    p.add_argument("--id", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--json", action="store_true", help="Machine-readable diff")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("upsert", help="Create (no --id) or update (--id) a product or feature")
    p.add_argument("--file", required=True, help="Payload JSON file")
    p.add_argument("--id", help="Existing document id to update")
    p.add_argument("--dry-run", action="store_true", help="Print the exact request without sending it")
    p.set_defaults(func=cmd_upsert)

    p = sub.add_parser("delete", help="Delete a feature, or a product with every feature under it")
    p.add_argument("id")
    p.add_argument("--yes", action="store_true", help="Actually delete (otherwise only previews)")
    p.set_defaults(func=cmd_delete)

    syn = sub.add_parser("synonyms", help="Manage synonym mappings").add_subparsers(dest="syn_command", required=True)
    p = syn.add_parser("list")
    p.add_argument("--search")
    p.add_argument("--type", choices=SYNONYM_TYPES)
    p.add_argument("--canonical")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_syn_list)
    p = syn.add_parser("get")
    p.add_argument("id")
    p.set_defaults(func=cmd_syn_get)
    p = syn.add_parser("create")
    p.add_argument("--canonical", required=True, help="Preferred term; must also be in --synonym")
    p.add_argument("--synonym", action="append", required=True, help="Repeat for each synonym")
    p.add_argument("--description")
    p.add_argument("--type", choices=SYNONYM_TYPES, default="equivalent")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_syn_create)
    p = syn.add_parser("update")
    p.add_argument("id")
    p.add_argument("--canonical")
    p.add_argument("--synonym", action="append", help="Full replacement list; repeat for each synonym")
    p.add_argument("--description")
    p.add_argument("--type", choices=SYNONYM_TYPES)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_syn_update)
    p = syn.add_parser("delete")
    p.add_argument("id")
    p.add_argument("--yes", action="store_true")
    p.set_defaults(func=cmd_syn_delete)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except CliError as exc:
        print(json.dumps({"error": str(exc), "exitCode": exc.code}), file=sys.stderr)
        return exc.code
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
