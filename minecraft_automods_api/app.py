from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from service import generate_modpack_and_zip
from minecraft_modpack_api import (
    get_avaliable_game_versions,
    get_avaliable_loader_versions
)


app = FastAPI(title="Minecraft Modpack AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ModpackRequest(BaseModel):
    game_version: str
    loader: str
    theme: str

@app.post("/generate_modpack")
def generate(request: ModpackRequest):
    if request.game_version not in get_avaliable_game_versions():
        return {"error": "Invalid game version"}

    if request.loader not in get_avaliable_loader_versions():
        return {"error": "Invalid loader version"}
    
    zip_path = generate_modpack_and_zip(
        game_version=request.game_version,
        loader=request.loader,
        theme=request.theme
    )

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="modpack.zip"
    )

@app.get("/game-versions")
def get_game_versions() -> list[str]:
    return get_avaliable_game_versions()

@app.get("/loader-versions")
def get_loader_versions() -> list[str]:
    return get_avaliable_loader_versions()