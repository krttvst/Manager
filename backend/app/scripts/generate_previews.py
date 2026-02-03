from pathlib import Path
from PIL import Image

MEDIA_DIR = Path("/app/media")
PREVIEWS_DIR = MEDIA_DIR / "previews"
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

MAX_SIZE = 1280
PREVIEW_SIZE = 400
JPEG_QUALITY = 70


def is_image_file(path: Path) -> bool:
    return path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def main() -> None:
    for file_path in MEDIA_DIR.iterdir():
        if not file_path.is_file():
            continue
        if file_path.parent == PREVIEWS_DIR:
            continue
        if not is_image_file(file_path):
            continue
        preview_path = PREVIEWS_DIR / f"{file_path.stem}.jpg"
        if preview_path.exists():
            continue
        try:
            image = Image.open(file_path)
            image = image.convert("RGB")
            image.thumbnail((PREVIEW_SIZE, PREVIEW_SIZE))
            image.save(preview_path, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        except Exception:
            continue


if __name__ == "__main__":
    main()
