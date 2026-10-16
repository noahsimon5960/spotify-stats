import os
import secrets
import sys
import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from spotify_stats.spotify.client import (
    SpotifyAPIError,
    build_authorization_url,
    create_pkce_pair,
    exchange_code,
    get_current_user,
)


DEFAULT_REDIRECT_URI = f"http://127.0.0.1:{os.getenv('PORT', '8501')}"


@st.cache_resource
def pending_authorizations() -> dict[str, tuple[str, float]]:
    return {}


pending = pending_authorizations()
st.set_page_config(page_title="Spotify Stats", page_icon="♫")
st.title("Spotify connection")

client_id = os.getenv("SPOTIFY_CLIENT_ID", "")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", DEFAULT_REDIRECT_URI)

if not client_id:
    st.error("Set the SPOTIFY_CLIENT_ID environment variable to connect Spotify.")
    st.stop()

if "spotify_access_token" not in st.session_state:
    callback_code = st.query_params.get("code")
    callback_state = st.query_params.get("state")

    if callback_code:
        pending_auth = pending.pop(callback_state, None) if callback_state else None
        if not pending_auth or time.time() - pending_auth[1] > 600:
            st.error("Spotify authorization state did not match. Please try again.")
            st.stop()

        try:
            token = exchange_code(callback_code, pending_auth[0], client_id, redirect_uri)
            st.session_state.spotify_access_token = token["access_token"]
            st.query_params.clear()
            st.rerun()
        except (SpotifyAPIError, KeyError) as error:
            st.error(f"Could not complete Spotify authorization: {error}")
            st.stop()

    callback_error = st.query_params.get("error")
    if callback_error:
        st.error(f"Spotify authorization failed: {callback_error}")
    else:
        verifier, challenge = create_pkce_pair()
        state = secrets.token_urlsafe(32)
        now = time.time()
        pending.update(
            {
                key: value
                for key, value in pending.items()
                if now - value[1] <= 600
            }
        )
        pending[state] = (verifier, now)
        authorization_url = build_authorization_url(
            client_id, redirect_uri, state, challenge
        )
        st.link_button("Connect with Spotify", authorization_url)
else:
    try:
        profile = get_current_user(st.session_state.spotify_access_token)
        st.success(f"Connected as {profile.get('display_name') or profile['id']}.")
        st.write(f"Spotify user ID: `{profile['id']}`")
    except SpotifyAPIError as error:
        st.error(str(error))