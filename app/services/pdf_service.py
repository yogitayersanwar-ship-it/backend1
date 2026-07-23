import os

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFService:
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """
        Extract plain text from all pages of a PDF file using PyMuPDF.
        Falls back to empty string if PyMuPDF is unavailable or file is corrupt.
        """
        if not PYMUPDF_AVAILABLE:
            print("[PDF] PyMuPDF (fitz) not installed. Run: pip install PyMuPDF")
            return ""
        if not os.path.exists(pdf_path):
            return ""
        try:
            doc = fitz.open(pdf_path)
            all_text = []
            for page in doc:
                all_text.append(page.get_text())
            doc.close()
            return "\n".join(all_text).strip()
        except Exception as e:
            print(f"[PDF] Text extraction error: {e}")
            return ""

    @staticmethod
    def generate_complaint_pdf(
        complaint_id: int,
        title: str,
        description: str,
        status: str,
        output_dir: str = "uploads/pdf"
    ) -> str:
        """
        Generate a formatted PDF grievance report using ReportLab.
        Returns the file path of the generated PDF.
        """
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("reportlab is not installed. Run: pip install reportlab")

        os.makedirs(output_dir, exist_ok=True)
        filename = f"complaint_{complaint_id}.pdf"
        filepath = os.path.join(output_dir, filename)

        c = canvas.Canvas(filepath, pagesize=letter)
        page_width, page_height = letter

        # Header background bar
        c.setFillColorRGB(0.10, 0.25, 0.55)
        c.rect(0, page_height - 80, page_width, 80, fill=True, stroke=False)

        # Header text
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, page_height - 45, "Grievance Management System")
        c.setFont("Helvetica", 11)
        c.drawString(50, page_height - 65, f"Official Complaint Report — #{complaint_id}")

        # Status badge
        status_colors = {
            "pending": (0.95, 0.65, 0.10),
            "in_progress": (0.10, 0.50, 0.90),
            "resolved": (0.10, 0.70, 0.35),
            "rejected": (0.85, 0.20, 0.20),
        }
        color = status_colors.get(status.lower(), (0.5, 0.5, 0.5))
        c.setFillColorRGB(*color)
        c.roundRect(page_width - 150, page_height - 65, 100, 22, 5, fill=True, stroke=False)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(page_width - 100, page_height - 57, status.upper())

        # Divider
        c.setStrokeColorRGB(0.80, 0.80, 0.80)
        c.setLineWidth(0.5)
        c.line(50, page_height - 100, page_width - 50, page_height - 100)

        # Complaint title
        c.setFillColorRGB(0.10, 0.25, 0.55)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, page_height - 130, f"Title: {title}")

        # Description section
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, page_height - 165, "Description:")

        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 10)
        text_object = c.beginText(50, page_height - 185)
        text_object.setLeading(16)
        for line in description.split("\n"):
            # Wrap long lines at ~90 chars
            while len(line) > 90:
                text_object.textLine(line[:90])
                line = line[90:]
            text_object.textLine(line)
        c.drawText(text_object)

        # Footer
        c.setFillColorRGB(0.6, 0.6, 0.6)
        c.setFont("Helvetica", 8)
        c.drawString(50, 40, "This is an auto-generated document by the Grievance Management System.")
        c.drawRightString(page_width - 50, 40, f"Complaint ID: #{complaint_id}")

        c.save()
        return filepath