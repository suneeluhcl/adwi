"""
Gmail read-only helper for Adwi.
Uses OAuth2 with client credentials from secrets.local.env.
Token is stored in secrets/gmail-token.json (never printed).
Scope: read-only — no sending, deleting, or modifying.
"""
import json
import os
import base64
from pathlib import Path

SECRETS_DIR  = Path.home() / "SuneelWorkSpace" / "secrets"
CREDS_CACHE  = Path.home() / "Downloads" / "credentials.json"
TOKEN_FILE   = SECRETS_DIR / "gmail-token.json"
SCOPES       = ["https://www.googleapis.com/auth/gmail.readonly"]


def _load_secrets() -> dict:
    env_file = SECRETS_DIR / "secrets.local.env"
    d = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d


def get_service():
    """Return an authenticated Gmail service. Runs OAuth flow if needed."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Build a client config dict from secrets (avoids reading credentials.json directly)
            s = _load_secrets()
            client_config = {
                "installed": {
                    "client_id":     s.get("GOOGLE_CLIENT_ID", ""),
                    "client_secret": s.get("GOOGLE_CLIENT_SECRET", ""),
                    "project_id":    s.get("GOOGLE_PROJECT_ID", ""),
                    "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
                    "token_uri":     "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"],
                }
            }
            if not client_config["installed"]["client_id"]:
                raise RuntimeError("GOOGLE_CLIENT_ID not set in secrets.local.env")
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json())
        TOKEN_FILE.chmod(0o600)

    return build("gmail", "v1", credentials=creds)


def list_emails(max_results=10, query="", inbox_only=True):
    """List recent emails newest-first. Scoped to INBOX by default."""
    service = get_service()
    params = {"userId": "me", "maxResults": max_results * 2}  # fetch extra to allow date-sort trim
    if inbox_only and not query:
        params["labelIds"] = ["INBOX"]
    if query:
        # Scope search to INBOX unless the query already specifies a label
        if "label:" not in query and "in:" not in query:
            params["q"] = f"in:inbox {query}"
        else:
            params["q"] = query
    results = service.users().messages().list(**params).execute()
    messages = results.get("messages", [])

    emails = []
    for msg in messages:
        detail = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["Subject", "From", "Date"]
        ).execute()
        headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
        emails.append({
            "id":           msg["id"],
            "subject":      headers.get("Subject", "(no subject)"),
            "from":         headers.get("From", ""),
            "date":         headers.get("Date", ""),
            "snippet":      detail.get("snippet", "")[:200],
            "internalDate": int(detail.get("internalDate", 0)),
        })

    # Sort newest-first by Gmail's internalDate (milliseconds since epoch)
    emails.sort(key=lambda e: e["internalDate"], reverse=True)
    return emails[:max_results]


def read_email(msg_id: str) -> dict:
    """Read full text of an email by ID."""
    service = get_service()
    detail = service.users().messages().get(
        userId="me", id=msg_id, format="full"
    ).execute()
    headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}

    # Extract body text
    def get_body(payload):
        if payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        return detail.get("snippet", "")

    return {
        "id":      msg_id,
        "subject": headers.get("Subject", "(no subject)"),
        "from":    headers.get("From", ""),
        "date":    headers.get("Date", ""),
        "body":    get_body(detail.get("payload", {}))[:5000],
    }


def get_label_counts() -> dict:
    """Get unread count for INBOX and a few labels."""
    service = get_service()
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    counts = {}
    for label in labels:
        if label["name"] in ("INBOX", "UNREAD", "SENT", "SPAM"):
            detail = service.users().labels().get(userId="me", id=label["id"]).execute()
            counts[label["name"]] = {
                "total":  detail.get("messagesTotal", 0),
                "unread": detail.get("messagesUnread", 0),
            }
    return counts
