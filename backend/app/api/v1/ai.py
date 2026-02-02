from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.deps import get_current_user
from app.schemas.ai import AiGenerateRequest, AiGenerateResponse
from datetime import datetime
from app.models.post import Post
from app.models.source_item import SourceItem
from app.models.enums import PostStatus
from app.services.parser import fetch_and_extract
from app.services.ai_stub import summarize_text, generate_title

router = APIRouter(prefix="", tags=["ai"])


@router.post("/posts/{post_id}/ai-generate", response_model=AiGenerateResponse)
def generate_from_url(
    post_id: int,
    payload: AiGenerateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.status not in {PostStatus.draft, PostStatus.rejected}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post is locked for AI generation")

    try:
        extracted = fetch_and_extract(payload.url)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    extracted_truncated = extracted[:10000]
    summary = summarize_text(extracted_truncated, max_chars=1200)
    title = generate_title(summary)
    body_text = summary

    post.title = title
    post.body_text = body_text
    post.updated_by = user.id
    post.updated_at = datetime.utcnow()
    db.add(
        SourceItem(
            post_id=post.id,
            source_url=payload.url,
            extracted_text=extracted_truncated,
            language_detected=None,
        )
    )
    db.commit()

    return AiGenerateResponse(title=title, body_text=body_text, source_url=payload.url)
