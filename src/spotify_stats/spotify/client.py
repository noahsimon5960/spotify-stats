"""Minimal Spotify OAuth and Web API helpers."""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import ssl
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi


AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1"


class SpotifyAPIError(Exception):
    """Raised when a Spotify request fails."""


def create_pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)[:128]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


def build_authorization_url(
    client_id: str, redirect_uri: str, state: str, code_challenge: str
) -> str:
    parameters = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "user-read-private user-read-email",
        "state": state,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
    }
    return f"{AUTHORIZE_URL}?{urlencode(parameters)}"


def exchange_code(
    code: str, verifier: str, client_id: str, redirect_uri: str
) -> dict[str, Any]:
    body = urlencode(
        {
            "client_id": client_id,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": verifier,
        }
    ).encode("utf-8")
    return _request(TOKEN_URL, body=body)


def get_current_user(access_token: str) -> dict[str, Any]:
    return _request(
        f"{API_BASE_URL}/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )


def _request(
    url: str,
    *,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    request_headers = {"Accept": "application/json"}
    if body is not None:
        request_headers["Content-Type"] = "application/x-www-form-urlencoded"
    if headers:
        request_headers.update(headers)

    request = Request(url, data=body, headers=request_headers)
    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        with urlopen(request, timeout=15, context=ssl_context) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as error:
        details = error.read().decode("utf-8") if isinstance(error, HTTPError) else str(error)
        raise SpotifyAPIError(f"Spotify request failed: {details}") from error