@echo off
echo ============================================================
echo  Gradiant - Installing OCR + Backend Dependencies
echo ============================================================
echo.

REM Install core OCR libraries only (fast)
echo [1/3] Installing Pillow (image loading)...
python -m pip install Pillow --quiet
if %errorlevel% neq 0 ( echo ERROR: pip failed. Make sure Python is installed. & pause & exit /b 1 )

echo [2/3] Installing pytesseract (Tesseract wrapper)...
python -m pip install pytesseract --quiet

echo [3/3] Installing easyocr (bilingual EN+UR OCR, this may take a few minutes)...
python -m pip install easyocr --quiet

echo.
echo ============================================================
echo  Done! OCR libraries installed.
echo.
echo  NEXT STEP: Add your Gemini API key to backend\.env
echo    Line 4:  GEMINI_API_KEY=AIzaSy...your-key-here
echo    Get key: https://aistudio.google.com/app/apikey
echo.
echo  NOTE: For Tesseract (Tier 2 OCR) to work, also install:
echo    https://github.com/UB-Mannheim/tesseract/wiki
echo    (EasyOCR works without it)
echo ============================================================
pause

