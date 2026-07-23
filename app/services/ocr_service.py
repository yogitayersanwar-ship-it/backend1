import os
import pytesseract
from PIL import Image
from app.services.pdf_service import PDFService


class OCRService:
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Unified text extraction dispatcher.
        - If the file is a PDF → uses PDFService (PyMuPDF)
        - Otherwise → uses Tesseract OCR on the image
        Returns empty string on any error or missing file.
        """
        if not file_path or not os.path.exists(file_path):
            return ""

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return PDFService.extract_text_from_pdf(file_path)
        else:
            return OCRService.extract_text_from_image(file_path)

    @staticmethod
    def extract_text_from_image(image_path: str) -> str:
        """Extracts text from an image file using Tesseract OCR."""
        if not os.path.exists(image_path):
            return ""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"[OCR] Image extraction error: {e}")
            return ""