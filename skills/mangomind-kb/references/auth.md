# Authentication

Every MangoMind API call carries an admin JWT minted by the dashboard's `POST /api/auth/login`. The token has **no expiry**; it stops working only when the admin's user record changes (password reset, permission change), which yields `401` and requires a fresh login.

## Where things live

| Item | Location | Override |
|---|---|---|
| API and dashboard origins | `~/.config/mangomind/config.json` | `MANGOMIND_API_URL`, `MANGOMIND_DASHBOARD_URL` |
| Token + signed-in identity | `~/.config/mangomind/credentials.json` (mode 0600) | `MANGOMIND_TOKEN` |
| Whole config directory | `~/.config/mangomind/` | `MANGOMIND_CONFIG_DIR` |

Never print, quote, or copy the contents of `credentials.json`. Never ask the user to paste a token into the chat.

## Step 1 — confirm the environment

The script defaults to production: API `https://production.aiserver.tagmango.com`, dashboard `https://mangomind.tagmango.in`. Run

```sh
python3 <skill-directory>/scripts/kb_api.py configure
```

and mention the environment to the user (`usingDefaults: true` means production). Only when the user wants a testing or local server, set both origins explicitly:

```sh
python3 <skill-directory>/scripts/kb_api.py configure --api-url <origin> --dashboard-url <origin>
```

The API origin is the server the dashboard calls, without the `/api` suffix (a trailing `/api` is stripped). Do not guess non-production origins; ask.

## Step 2 — check the session

```sh
python3 <skill-directory>/scripts/kb_api.py whoami
```

| Exit | Meaning | Do |
|---|---|---|
| 0 | Signed in; output lists `permissions` and `can.viewFeatures` / `can.writeFeatures` | Continue. Refuse write workflows early if `writeFeatures` is false. |
| 2 | No token, or the API rejected it | Run the login flow below. |
| 1 | Configuration or network problem | Fix the origin, or tell the user the API is unreachable. |

## Step 3 — sign in

```sh
python3 <skill-directory>/scripts/kb_api.py login
```

The command blocks for up to 5 minutes (`--timeout` to change), so run it with an extended command timeout or in the background. It:

1. starts a local page at `http://127.0.0.1:<port>/` (the port is printed on stderr as JSON, together with a dashboard login link) and opens it in the browser when possible;
2. waits for the user to either **(A)** sign in on the dashboard, run `copy(localStorage.getItem('authToken'))` in the dashboard's browser console, and paste the token on the local page, or **(B)** enter their dashboard email and password on the local page, which the script exchanges for a token directly with the API;
3. verifies the token against `GET /api/auth/me`, stores it, and exits `0` printing the signed-in user.

Tell the user in plain words what to do, including the local URL, and wait. Neither the token nor the password passes through the agent. Use `--no-browser` on headless machines and give the user the URL. Use `--force` to switch accounts. The `--token` flag exists for automation only; warn that a token passed as an argument lands in shell history.

## Permissions

| Permission | Grants |
|---|---|
| `view:features` | list, get, search, export, read synonyms |
| `write:features` | create, update, delete features and products, write synonyms |
| `admin` | everything |

A `403` (exit 3) means the signed-in user lacks the permission; do not retry, tell the user which permission is missing and who can grant it (a MangoMind admin).

## Optional dashboard enhancement (not implemented today)

The login command also listens on `GET /callback?token=<jwt>&state=<state>` and opens the dashboard as `/login?cli_callback=<url>&state=<state>`. If the dashboard's login page is taught to honor those two query params by redirecting to `cli_callback` after a successful sign-in, option (A) becomes a one-click flow with no copy-paste. Today the dashboard ignores the params, so the paste and email/password options are the working paths.
