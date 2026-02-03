from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from PIL import Image
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/media", tags=["media"])
MAX_SIZE = 1280
PREVIEW_SIZE = 400
JPEG_QUALITY = 85


@router.post("/upload")
def upload_media(
    file: UploadFile = File(...),
    _user=Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty filename")
    media_dir = Path(settings.media_dir)
    media_dir.mkdir(parents=True, exist_ok=True)
    previews_dir = media_dir / "previews"
    previews_dir.mkdir(parents=True, exist_ok=True)

    try:
        image = Image.open(file.file)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")

    image = image.convert("RGB")
    image.thumbnail((MAX_SIZE, MAX_SIZE))
    base_name = uuid4().hex
    filename = f"{base_name}.jpg"
    target = media_dir / filename
    image.save(target, format="JPEG", quality=JPEG_QUALITY, optimize=True)

    preview = image.copy()
    preview.thumbnail((PREVIEW_SIZE, PREVIEW_SIZE))
    preview_filename = f"{base_name}.jpg"
    preview_target = previews_dir / preview_filename
    preview.save(preview_target, format="JPEG", quality=70, optimize=True)

    return {"url": f"/media/{filename}", "preview_url": f"/media/previews/{preview_filename}"}
