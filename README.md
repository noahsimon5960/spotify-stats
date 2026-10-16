# Spotify Stats

## Local setup

1. Create an app in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. For local development, add `http://127.0.0.1:8501` as a Redirect URI in the app settings. Spotify permits HTTP only for explicit loopback IPs; `localhost` is not accepted.
3. Install dependencies with `pip install -r requirements.txt`.
4. Set `SPOTIFY_CLIENT_ID` and start the app:

	```sh
	export SPOTIFY_CLIENT_ID="your-client-id"
	streamlit run app.py
	```

	Set `SPOTIFY_REDIRECT_URI` when the app is served at a different URL. For a local Docker deployment, use the host-published port, for example `http://127.0.0.1:8080`. For any non-loopback deployment, use an HTTPS URI. In every case, the URI must exactly match one registered in the Spotify app settings.

The app uses Spotify's authorization-code flow with PKCE, handles the redirect at the Streamlit root URL, and requests the current user's profile from `/v1/me`.