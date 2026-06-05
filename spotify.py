import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# -----------------------------
# SPOTIFY AUTH SETUP
# -----------------------------
scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri="http://127.0.0.1:8888/callback",
    scope=scope
))


# -----------------------------
# PLAY TRACK BY SEARCH
# -----------------------------
def play_song(query: str):
    if not query:
        return "No song given"

    results = sp.search(q=query, limit=1, type="track")

    items = results.get("tracks", {}).get("items", [])

    if not items:
        return "No song found"

    track = items[0]
    uri = track["uri"]

    try:
        sp.start_playback(uris=[uri])
        return f"Playing {track['name']} by {track['artists'][0]['name']}"
    except Exception as e:
        return f"Spotify error: {str(e)}"


# -----------------------------
# SEARCH + PLAY (alias)
# -----------------------------
def search_and_play(query: str):
    return play_song(query)


# -----------------------------
# PLAY LATEST / DEFAULT
# -----------------------------
def play_default():
    return play_song("top hits")