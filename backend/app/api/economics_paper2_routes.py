from fastapi import APIRouter, Form, File, UploadFile
from typing import Optional, List
from app.services.economics_paper2_service import answer_paper2_images, answer_paper2_text
from app.utils.helpers import extract_base64_from_file

router = APIRouter(tags=["Economics Paper 2 Examiner"])


@router.post("/economics/paper2/answer")
async def answer_economics_paper2(
    section: str = Form(...),
    query: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
):
    """
    Answer Cambridge O-Level Economics Paper 2 questions.
    Section A accepts 1-3 images and uses visible marks from the paper.
    Section B accepts typed text with command-word marks, or one image with visible marks.
    """
    section = section.upper().strip()
    if section not in {"A", "B"}:
        return {"error": "Please choose Section A or Section B."}

    uploaded_images = images or []

    if section == "A":
        if not uploaded_images:
            return {"error": "Section A requires at least one image."}
        if len(uploaded_images) > 3:
            return {"error": "Section A supports up to 3 images only."}
    else:
        if uploaded_images and len(uploaded_images) > 1:
            return {"error": "Section B image mode supports one image only."}
        if not uploaded_images and not (query or "").strip():
            return {"error": "Section B needs either typed text or one image."}

    if uploaded_images:
        image_b64_list = []
        for image in uploaded_images:
            content = await image.read()
            image_b64_list.append(extract_base64_from_file(content))
        return answer_paper2_images(section, image_b64_list, query or "")

    return answer_paper2_text(section, query or "")
