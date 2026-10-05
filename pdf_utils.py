import base64
import html
import fitz  # PyMuPDF
from pypdf import PdfReader


# ============================================================
# EXTRACT PDF TEXT
# ============================================================

def extract_pdf_text(pdf_path):

    pages = []

    reader = PdfReader(pdf_path)

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text()

        if text and text.strip():

            pages.append({
                "page": page_number,
                "text": text.strip()
            })

    return pages


# ============================================================
# CREATE PDF PREVIEW
# ============================================================

def create_pdf_preview(pdf_path):

    # --------------------------------------------------------
    # No PDF selected
    # --------------------------------------------------------

    if not pdf_path:

        return """
        <div class="pdf-empty">

            <div class="pdf-empty-icon">
                📄
            </div>

            <div class="pdf-empty-title">
                PDF Preview
            </div>

            <div class="pdf-empty-text">
                Upload and process a PDF to preview it here.
            </div>

        </div>
        """

    try:

        # ----------------------------------------------------
        # Open PDF
        # ----------------------------------------------------

        pdf_document = fitz.open(pdf_path)

        preview_html = """
        <div class="pdf-container">
        """

        # ----------------------------------------------------
        # Render every page
        # ----------------------------------------------------

        for page_number in range(len(pdf_document)):

            page = pdf_document.load_page(page_number)

            # Higher resolution for clearer text
            matrix = fitz.Matrix(1.5, 1.5)

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            image_bytes = pixmap.tobytes("png")

            image_base64 = base64.b64encode(
                image_bytes
            ).decode("utf-8")

            preview_html += f"""
            <div class="pdf-page">

                <div class="pdf-page-number">
                    Page {page_number + 1}
                </div>

                <img
                    src="data:image/png;base64,{image_base64}"
                    class="pdf-page-image"
                />

            </div>
            """

        pdf_document.close()

        preview_html += """
        </div>
        """

        return preview_html

    except Exception as e:

        return f"""
        <div class="pdf-error">

            <div class="pdf-error-title">
                ❌ PDF Preview Error
            </div>

            <div class="pdf-error-text">
                {html.escape(str(e))}
            </div>

        </div>
        """
