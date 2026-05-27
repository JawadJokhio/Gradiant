from fastapi import APIRouter, Form, File, UploadFile
from typing import Optional
from app.services.economics_service import explain_mcq_text, explain_mcq_image
from app.utils.helpers import extract_base64_from_file

router = APIRouter(tags=["Economics Examiner"])


@router.post("/economics/explain-mcq")
async def explain_economics_mcq(
    query: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    """
    Explain a Cambridge O-Level Economics MCQ (2281).
    Accepts either a text query, an image upload, or both.
    Always returns structured JSON with the correct answer, rationale, and examiner tip.
    """
    if image:
        content = await image.read()
        image_b64 = extract_base64_from_file(content)
        result = explain_mcq_image(image_b64, query or "")
    elif query:
        result = explain_mcq_text(query)
    else:
        return {"error": "Please provide an MCQ question text or upload an image."}

    return result
