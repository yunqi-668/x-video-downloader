from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from urllib.parse import urlparse
import yt_dlp, tempfile, os, uuid, shutil
from pathlib import Path

app = FastAPI(title="X Video Downloader")
BASE = Path(tempfile.gettempdir()) / "x-video-downloader"
BASE.mkdir(exist_ok=True)

class ParseRequest(BaseModel):
    url: HttpUrl

def validate_url(url: str):
    host = (urlparse(url).hostname or "").lower()
    allowed = {"x.com", "www.x.com", "twitter.com", "www.twitter.com", "mobile.twitter.com"}
    if host not in allowed:
        raise HTTPException(400, "请粘贴 x.com 或 twitter.com 的视频链接。")

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.post("/api/info")
def info(req: ParseRequest):
    url = str(req.url)
    validate_url(url)
    opts = {"quiet": True, "no_warnings": True, "skip_download": True, "noplaylist": True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=False)
        formats = []
        seen = set()
        for f in data.get("formats", []):
            if f.get("vcodec") in (None, "none"):
                continue
            h = f.get("height")
            if not h:
                continue
            key = (h, f.get("ext") or "mp4")
            if key in seen:
                continue
            seen.add(key)
            formats.append({"height": h, "ext": f.get("ext") or "mp4"})
        formats.sort(key=lambda x: x["height"], reverse=True)
        return {"title": data.get("title") or "X 视频", "thumbnail": data.get("thumbnail"), "formats": formats}
    except Exception as e:
        raise HTTPException(422, "无法解析该视频。请确认它是可公开访问的视频链接，且没有地区或账号访问限制。")

@app.get("/api/download")
def download(url: str, height: int = 0):
    validate_url(url)
    job = uuid.uuid4().hex
    out = BASE / job
    out.mkdir()
    template = str(out / "%(title).80s.%(ext)s")
    opts = {
        "quiet": True, "no_warnings": True, "noplaylist": True,
        "outtmpl": template, "merge_output_format": "mp4",
        "format": (f"bestvideo[height<={height}]+bestaudio/best[height<={height}]" if height else "bestvideo+bestaudio/best"),
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        candidates = [p for p in out.iterdir() if p.is_file()]
        if not candidates:
            raise RuntimeError("下载文件未生成")
        path = max(candidates, key=lambda p: p.stat().st_size)
        return FileResponse(path, media_type="video/mp4", filename=path.name, background=None)
    except Exception:
        shutil.rmtree(out, ignore_errors=True)
        raise HTTPException(422, "下载失败。该视频可能不可公开访问，或平台已调整其视频格式。")

app.mount("/static", StaticFiles(directory="static"), name="static")
