"""
ocr_service.py
Multi-tier OCR service with EasyOCR → Tesseract → Gemini Vision fallback.
Handles printed text, handwriting, and math equations.
"""
import base64
import io
import time
from typing import Optional

from app.models.schemas import OCRResult, TextBlock


# Lazy module-level singletons to avoid heavy model loading at startup
_easyocr_reader = None
_pytesseract = None


def _get_easyocr():
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        # English + Urdu (Arabic-script) support
        _easyocr_reader = easyocr.Reader(["en", "ur"], gpu=False)
    return _easyocr_reader


def _get_tesseract():
    global _pytesseract
    if _pytesseract is None:
        import pytesseract
        _pytesseract = pytesseract
    return _pytesseract


class OCRService:
    def __init__(self, llm_service=None):
        # llm_service is optional — used only for Gemini handwriting fallback
        self.llm_service = llm_service

    # ─── Public API ──────────────────────────────────────────────────────────

    def extract_text_from_base64(
        self,
        image_base64: str,
        mode: str = "auto",  # "printed" | "handwriting" | "math" | "auto"
    ) -> OCRResult:
        """
        Main entry point. Selects the best OCR tier based on the requested mode.

        Tier 1 (default): EasyOCR — printed English/Urdu text, bilingual
        Tier 2 (fallback): Tesseract — fast, English-only, already in codebase
        Tier 3 (handwriting / last resort): Gemini Vision via llm_service
        """
        start = time.time()

        # Handwriting always goes straight to Gemini
        if mode == "handwriting":
            try:
                return self._gemini_ocr(image_base64, start)
            except Exception as hw_err:
                print(f"[OCRService] Handwriting OCR (Gemini) failed ({hw_err}), returning empty result.")
                return OCRResult(
                    raw_text="",
                    confidence=0.0,
                    blocks=[],
                    language_detected="unknown",
                    processing_time_ms=round((time.time() - start) * 1000, 1),
                )

        # Printed / auto / math: try EasyOCR first
        try:
            result = self._easyocr_extract(image_base64, start)
            # If EasyOCR confidence is too low, escalate
            if result.confidence < 0.3 and self.llm_service:
                try:
                    return self._gemini_ocr(image_base64, start)
                except Exception:
                    pass  # Keep EasyOCR result if Gemini also fails
            return result
        except Exception as easyocr_err:
            print(f"[OCRService] EasyOCR failed ({easyocr_err}), trying Tesseract…")

        try:
            return self._tesseract_extract(image_base64, start)
        except Exception as tess_err:
            print(f"[OCRService] Tesseract failed ({tess_err}), trying Gemini…")

        if self.llm_service:
            try:
                return self._gemini_ocr(image_base64, start)
            except Exception as gemini_err:
                print(f"[OCRService] Gemini OCR tier failed ({gemini_err}), returning empty result.")

        # All tiers exhausted — return empty result (never raise to caller)
        return OCRResult(
            raw_text="",
            confidence=0.0,
            blocks=[],
            language_detected="unknown",
            processing_time_ms=round((time.time() - start) * 1000, 1),
        )

    # ─── OCR Tiers ────────────────────────────────────────────────────────────

    def _easyocr_extract(self, image_base64: str, start: float) -> OCRResult:
        """Tier 1 — EasyOCR with English + Urdu support."""
        from PIL import Image

        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        reader = _get_easyocr()
        # detail=1 returns (bbox, text, confidence) tuples
        results = reader.readtext(image)

        blocks: list[TextBlock] = []
        texts: list[str] = []
        confidences: list[float] = []

        for bbox, text, conf in results:
            text = text.strip()
            if not text:
                continue
            blocks.append(TextBlock(text=text, confidence=round(conf, 3), bbox=bbox))
            texts.append(text)
            confidences.append(conf)

        raw_text = "\n".join(texts)
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        return OCRResult(
            raw_text=raw_text,
            confidence=round(avg_conf, 3),
            blocks=blocks,
            language_detected=self._detect_language(raw_text),
            processing_time_ms=round((time.time() - start) * 1000, 1),
        )

    def _tesseract_extract(self, image_base64: str, start: float) -> OCRResult:
        """Tier 2 — Tesseract (already imported in math_service.py)."""
        from PIL import Image

        tess = _get_tesseract()
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))

        # --oem 3: LSTM + legacy engine; --psm 6: single uniform block (best for exam papers)
        raw_text = tess.image_to_string(image, config="--oem 3 --psm 6")

        # Extract word-level confidence data
        data = tess.image_to_data(image, output_type=tess.Output.DICT)
        blocks: list[TextBlock] = []
        conf_values: list[float] = []

        for i, word in enumerate(data["text"]):
            word = word.strip()
            conf_raw = int(data["conf"][i])
            if word and conf_raw > 0:
                conf = conf_raw / 100.0
                blocks.append(TextBlock(text=word, confidence=conf))
                conf_values.append(conf)

        avg_conf = sum(conf_values) / len(conf_values) if conf_values else 0.0

        return OCRResult(
            raw_text=raw_text.strip(),
            confidence=round(avg_conf, 3),
            blocks=blocks,
            language_detected="en",
            processing_time_ms=round((time.time() - start) * 1000, 1),
        )

    def _gemini_ocr(self, image_base64: str, start: float) -> OCRResult:
        """Tier 3 — Gemini Vision (handwriting, complex layouts, last resort)."""
        if not self.llm_service:
            raise ValueError("No LLM service configured for Gemini OCR tier.")

        system_prompt = (
            "You are a precision OCR engine for Cambridge O-Level exam papers.\n"
            "Extract ALL text from the image exactly as written.\n"
            "Rules:\n"
            "- Preserve question numbers, sub-parts (a)(b)(i)(ii), and line breaks.\n"
            "- Do NOT interpret, answer, or add commentary — only transcribe.\n"
            "- Mark illegible characters with [?].\n"
            "- Return ONLY the raw transcribed text, nothing else."
        )
        user_prompt = "Transcribe every piece of text visible in this image."

        raw_text = self.llm_service.generate_vision_response(
            system_prompt, user_prompt, image_base64
        )
        if raw_text is None:
            raw_text = ""

        # If vision providers all failed, raw_text contains an error string — don't use it as OCR output
        _VISION_FAILURE_MARKERS = (
            "vision engines offline",
            "failed at runtime",
            "no provider is configured",
            "intelligence engines offline",
        )
        if any(marker in raw_text.lower() for marker in _VISION_FAILURE_MARKERS):
            raise RuntimeError(f"Vision OCR tier unavailable: {raw_text[:120]}")

        return OCRResult(
            raw_text=raw_text.strip(),
            confidence=0.85,  # Estimated — Gemini doesn't return per-token confidence
            blocks=[TextBlock(text=raw_text.strip(), confidence=0.85)],
            language_detected=self._detect_language(raw_text),
            processing_time_ms=round((time.time() - start) * 1000, 1),
        )

    # ─── Helpers ─────────────────────────────────────────────────────────────

    @staticmethod
    def _detect_language(text: str) -> str:
        """Heuristic language detection based on Unicode ranges."""
        # Arabic/Urdu block: U+0600–U+06FF
        urdu_chars = sum(1 for c in text if "\u0600" <= c <= "\u06ff")
        alpha_chars = sum(1 for c in text if c.isalpha())
        if alpha_chars == 0:
            return "en"
        ratio = urdu_chars / alpha_chars
        if ratio > 0.5:
            return "ur"
        if ratio > 0.1:
            return "mixed"
        return "en"

