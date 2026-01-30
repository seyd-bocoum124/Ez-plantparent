from fastapi import UploadFile, File, HTTPException, APIRouter
from fastapi.responses import JSONResponse
import requests
import os
from fastapi import Depends, APIRouter, HTTPException, Response, status
from usecases.ManageUsers.AuthUser.guard import get_current_user_from_bearer

PLANT_NET_API_KEY = os.getenv("PLANT_NET_API_KEY")

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/plant-identifications", status_code=201)
async def identify(files: list[UploadFile] = File(...), current = Depends(get_current_user_from_bearer)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    # Préparer les fichiers pour PlantNet
    plantnet_files = []
    for f in files:
        content = await f.read()
        plantnet_files.append(("images", (f.filename, content, f.content_type)))


    response = requests.post(
        "https://my-api.plantnet.org/v2/identify/all",
        files=plantnet_files,
        params={
            "api-key": PLANT_NET_API_KEY,
            "include-related-images": "true",
            "lang": "fr"
        }
    )

    if response.status_code != 200:
        raise HTTPException(status_code=422, detail="Identification failed")

    return JSONResponse(content=response.json(), status_code=201)



