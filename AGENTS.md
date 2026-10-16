# Project Guidance

## Project shape

- This is a Python 3.12 Streamlit app. The UI entry point is the root `app.py`.
- Keep Spotify API and OAuth helpers in `src/spotify_stats/spotify/`; analytics code belongs in `src/spotify_stats/analytics/`.
- `pages/`, `components/`, `assets/`, and `tests/` are currently scaffolding; inspect before assuming they contain features or test conventions.

## Setup and run

- Install dependencies with `pip install -r requirements.txt`.
- Set `SPOTIFY_CLIENT_ID` in the process environment, then run locally with `streamlit run app.py`.
- `SPOTIFY_REDIRECT_URI` optionally overrides the callback URI. The default is `http://127.0.0.1:8501` (or the port in `PORT`). Register the exact URI in the Spotify Developer Dashboard.
- Spotify allows HTTP only for explicit loopback IP addresses. Do not use `localhost`; use HTTPS for non-loopback deployments.
- The Docker image sets `PORT=8080` and binds Streamlit to `0.0.0.0`. For local Docker callbacks, use the host-published loopback URI, such as `http://127.0.0.1:8080`.

## Spotify integration

- OAuth uses Authorization Code with PKCE; do not add a client secret. `SPOTIFY_CLIENT_ID` is read from the environment.
- The callback is handled by Streamlit at the app root. OAuth `state` and PKCE verifier are held in Streamlit's process-level cached resource for the callback and expire after 10 minutes.
- Spotify API requests go through `src/spotify_stats/spotify/client.py`, using `urllib` and certifi's CA bundle. Keep TLS certificate verification enabled; do not work around certificate errors by disabling verification.
- Access tokens currently live only in Streamlit session state. Avoid logging or committing tokens or credentials.

## Validation

- Run `python -m compileall -q app.py src/spotify_stats` for a quick syntax check.
- There is no populated test suite yet. Add focused tests when adding reusable OAuth or API behavior; keep external Spotify calls mocked in automated tests.
