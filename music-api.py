import io
from fastapi import FastAPI
from fastapi.responses import StreamingResponse 
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(title="Music Downloader", description="API para dowload de musicas", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

class Video(BaseModel):
    url: str


@app.get("/")
def ler_raiz():
    return {"mensagem": "API No AR!"}

@app.get("/music/search")
def search_youtube(query, limit=5):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "forcejson": True,
        "default_search": "ytsearch",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)["entries"]

    buscas = [
        {"id": i+1, "title": v["title"], "link": v["url"]}
        for i, v in enumerate(results)
    ]
    return buscas

@app.post("/music/download")
def baixar_audio(video: Video):
    yt = YouTube(video.url, on_progress_callback=on_progress)
    ys = yt.streams.get_audio_only()
    ys.download()
    return {"titulo": yt.title, "mensagem": "Download iniciado!"}

@app.post("/music/streaming/download")
def baixar_audio(video: Video):
    yt = YouTube(video.url, on_progress_callback=on_progress)

    stream = yt.streams.get_audio_only()

    buffer = io.BytesIO()
    stream.stream_to_buffer(buffer)
    buffer.seek(0) 


    return StreamingResponse(
        buffer,
        media_type="audio/webm",  
        headers={"Content-Disposition": f"attachment; filename={yt.title}.mp4"}
    )