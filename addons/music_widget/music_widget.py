import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
import os
import httpx
import urllib.parse

from app_paths import get_base_dir

app = FastAPI()


@app.get("/music", response_class=HTMLResponse)
async def get_html():
    html_path = os.path.join(get_base_dir(), "assets", "music_widget", "widget.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


def obtener_credenciales_lastfm():
    config_path = os.path.join(get_base_dir(), "config.json")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("lastfm_user", ""), data.get("lastfm_api", "")
    except Exception:
        return "", ""


async def get_lastfm_track():
    LASTFM_USERNAME, LASTFM_API_KEY = obtener_credenciales_lastfm()

    if not LASTFM_USERNAME or not LASTFM_API_KEY:
        return None

    url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={LASTFM_USERNAME}&api_key={LASTFM_API_KEY}&format=json&limit=1"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            data = response.json()
            track = data["recenttracks"]["track"][0]

            is_playing = False
            if "@attr" in track and track["@attr"].get("nowplaying") == "true":
                is_playing = True

            cover_url = ""
            if "image" in track and isinstance(track["image"], list):
                for img in reversed(track["image"]):
                    if img.get("#text"):
                        cover_url = img["#text"]
                        break
            if cover_url == "https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png":
                itunes_cover = await get_itunes_cover(track["artist"]["#text"], track["name"])
                if itunes_cover:
                    cover_url = itunes_cover

            return {
                "title": track["name"],
                "artist": track["artist"]["#text"],
                "is_playing": is_playing,
                "cover_url": cover_url
            }
        except Exception:
            return None


async def get_itunes_cover(artist, title):
    query = urllib.parse.quote(f"{artist} {title}")
    url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=1"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            data = response.json()

            if data["resultCount"] > 0:
                cover_url = data["results"][0].get("artworkUrl100", "")
                return cover_url.replace("100x100bb", "500x500bb")
        except Exception:
            pass

    return None


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            track_data = await get_lastfm_track()

            if track_data:
                await websocket.send_json(track_data)

            await asyncio.sleep(2)

    except Exception:
        print("OBS se desconectó del WebSocket.")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=6767)