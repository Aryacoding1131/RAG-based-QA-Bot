import os
import html
import gradio as gr

from pdf_utils import (
    extract_pdf_text,
    create_pdf_preview
)

from vector_store import (
    create_chunks,
    create_vector_database,
    search_documents
)

from rag import generate_answer


# ============================================================
# GLOBAL VARIABLES
# ============================================================

vector_db = None
current_pdf_name = None


# ============================================================
# PROCESS PDF
# ============================================================

def process_pdf(pdf_file):

    global vector_db
    global current_pdf_name

    # --------------------------------------------------------
    # Check PDF
    # --------------------------------------------------------

    if pdf_file is None:

        return (
            """
            <div class="status error">

                <div class="status-title">
                    ⚠️ No PDF selected
                </div>

                <div class="status-text">
                    Please upload a PDF first.
                </div>

            </div>
            """,
            "",
            create_pdf_preview(None)
        )

    try:

        # ----------------------------------------------------
        # Get file name
        # ----------------------------------------------------

        current_pdf_name = os.path.basename(
            pdf_file
        )

        # ----------------------------------------------------
        # Extract text
        # ----------------------------------------------------

        pages = extract_pdf_text(
            pdf_file
        )

        if not pages:

            return (
                """
                <div class="status error">

                    <div class="status-title">
                        ❌ No readable text
                    </div>

                    <div class="status-text">
                        Text could not be extracted from this PDF.
                    </div>

                </div>
                """,
                "",
                create_pdf_preview(pdf_file)
            )

        # ----------------------------------------------------
        # Create chunks
        # ----------------------------------------------------

        chunks = create_chunks(
            pages
        )

        # ----------------------------------------------------
        # Create vector database
        # ----------------------------------------------------

        vector_db = create_vector_database(
            chunks
        )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        status = f"""
        <div class="status success">

            <div class="status-title">
                ✅ PDF processed successfully
            </div>

            <div class="status-text">

                <b>File:</b>
                {html.escape(current_pdf_name)}

                <br>

                <b>Pages:</b>
                {len(pages)}

                <br>

                <b>Chunks:</b>
                {len(chunks)}

                <br><br>

                You can now ask questions about this PDF.

            </div>

        </div>
        """

        pdf_info = (
            f"📄 {len(pages)} pages   |   "
            f"🧩 {len(chunks)} chunks"
        )

        # ----------------------------------------------------
        # Create preview
        # ----------------------------------------------------

        preview = create_pdf_preview(
            pdf_file
        )

        return (
            status,
            pdf_info,
            preview
        )

    except Exception as e:

        return (
            f"""
            <div class="status error">

                <div class="status-title">
                    ❌ Error
                </div>

                <div class="status-text">
                    {html.escape(str(e))}
                </div>

            </div>
            """,
            "",
            create_pdf_preview(pdf_file)
        )


# ============================================================
# ASK QUESTION
# ============================================================

def ask_question(question):

    global vector_db

    # --------------------------------------------------------
    # PDF not processed
    # --------------------------------------------------------

    if vector_db is None:

        return (
            """
            <div class="answer-empty">

                <div class="answer-empty-icon">
                    📄
                </div>

                <div class="answer-empty-title">
                    Upload a PDF first
                </div>

                <div class="answer-empty-text">
                    Upload and process a PDF before
                    asking questions.
                </div>

            </div>
            """,
            ""
        )

    # --------------------------------------------------------
    # Empty question
    # --------------------------------------------------------

    if not question or not question.strip():

        return (
            """
            <div class="status warning">

                <div class="status-title">
                    ⚠️ Question required
                </div>

                <div class="status-text">
                    Please enter a question.
                </div>

            </div>
            """,
            ""
        )

    try:

        # ----------------------------------------------------
        # Search vector database
        # ----------------------------------------------------

        documents = search_documents(
            vector_db,
            question,
            k=4
        )

        # ----------------------------------------------------
        # Generate answer
        # ----------------------------------------------------

        answer, pages = generate_answer(
            question,
            documents
        )

        # ----------------------------------------------------
        # Format answer
        # ----------------------------------------------------

        safe_answer = html.escape(
            answer
        )

        safe_answer = safe_answer.replace(
            "\n",
            "<br>"
        )

        answer_html = f"""
        <div class="answer-box">

            <div class="answer-header">

                <div class="answer-icon">
                    🤖
                </div>

                <div>

                    <div class="answer-title">
                        Answer
                    </div>

                    <div class="answer-subtitle">
                        Generated from your PDF
                    </div>

                </div>

            </div>

            <div class="answer-divider"></div>

            <div class="answer-text">
                {safe_answer}
            </div>

        </div>
        """

        # ----------------------------------------------------
        # Sources
        # ----------------------------------------------------

        source_html = """
        <div class="sources-box">

            <div class="sources-title">
                📚 Retrieved Sources
            </div>

            <div class="sources-subtitle">
                Relevant pages retrieved from your PDF
            </div>
        """

        # ----------------------------------------------------
        # Page badges
        # ----------------------------------------------------

        if pages:

            source_html += """
            <div class="page-list">
            """

            for page in pages:

                source_html += f"""
                <span class="page-badge">
                    Page {page}
                </span>
                """

            source_html += """
            </div>
            """

        # ----------------------------------------------------
        # Retrieved chunks
        # ----------------------------------------------------

        source_html += """
            <details class="retrieved-details">

                <summary>
                    🔎 View Retrieved PDF Content
                </summary>

                <div class="chunks-container">
        """

        for index, document in enumerate(
            documents,
            start=1
        ):

            page = document.metadata.get(
                "page",
                "Unknown"
            )

            content = html.escape(
                document.page_content
            )

            source_html += f"""
                    <div class="chunk-card">

                        <div class="chunk-header">

                            <span class="chunk-title">
                                Chunk {index}
                            </span>

                            <span class="chunk-page">
                                Page {page}
                            </span>

                        </div>

                        <div class="chunk-text">
                            {content}
                        </div>

                    </div>
            """

        source_html += """
                </div>

            </details>

        </div>
        """

        return (
            answer_html,
            source_html
        )

    except Exception as e:

        return (
            f"""
            <div class="status error">

                <div class="status-title">
                    ❌ Error
                </div>

                <div class="status-text">
                    {html.escape(str(e))}
                </div>

            </div>
            """,
            ""
        )


# ============================================================
# CLEAR
# ============================================================

def clear_app():

    global vector_db
    global current_pdf_name

    vector_db = None
    current_pdf_name = None

    return (
        "",
        "",
        """
        <div class="answer-empty">

            <div class="answer-empty-icon">
                🤖
            </div>

            <div class="answer-empty-title">
                Ready for your question
            </div>

            <div class="answer-empty-text">
                Upload a PDF and ask a question.
            </div>

        </div>
        """,
        create_pdf_preview(None)
    )


# ============================================================
# CSS
# ============================================================

css = """

/* ============================================================
   GLOBAL
============================================================ */

* {
    box-sizing: border-box;
}

body {
    background: #f5f7fb !important;
}

.gradio-container {
    max-width: 1250px !important;
    margin: auto !important;
    padding: 25px !important;
}


/* ============================================================
   TEXT COLORS
============================================================ */

.gradio-container .prose {
    color: #1e293b !important;
}

.gradio-container .prose h1,
.gradio-container .prose h2,
.gradio-container .prose h3,
.gradio-container .prose h4 {
    color: #1e293b !important;
    line-height: 1.5 !important;
}

.gradio-container .prose p {
    color: #475569 !important;
    line-height: 1.7 !important;
}


/* ============================================================
   CARDS
============================================================ */

.card {
    background: #ffffff !important;

    padding: 22px !important;

    border-radius: 18px !important;

    border: 1px solid #e2e8f0 !important;

    box-shadow:
        0 8px 25px
        rgba(15, 23, 42, 0.07) !important;
}


/* ============================================================
   HEADER
============================================================ */

.header {
    text-align: center;

    padding: 35px 20px;

    margin-bottom: 25px;

    border-radius: 20px;

    background:
        linear-gradient(
            135deg,
            #4f46e5,
            #7c3aed
        );

    color: white !important;

    box-shadow:
        0 12px 30px
        rgba(79, 70, 229, 0.25);
}

.header h1 {
    color: white !important;

    margin: 0 0 10px 0 !important;

    font-size: 36px !important;

    font-weight: 700 !important;

    line-height: 1.4 !important;
}

.header p {
    color: white !important;

    margin: 0 !important;

    font-size: 17px !important;

    line-height: 1.6 !important;
}


/* ============================================================
   INPUTS
============================================================ */

.gradio-container textarea,
.gradio-container input {
    color: #1e293b !important;

    background: #ffffff !important;

    border-color: #cbd5e1 !important;

    font-size: 15px !important;

    line-height: 1.6 !important;
}

.gradio-container textarea::placeholder,
.gradio-container input::placeholder {
    color: #94a3b8 !important;

    opacity: 1 !important;
}


/* ============================================================
   LABELS
============================================================ */

.gradio-container label {
    color: #1e293b !important;

    font-weight: 600 !important;

    line-height: 1.5 !important;
}


/* ============================================================
   BUTTONS
============================================================ */

.gradio-container button {
    font-weight: 600 !important;

    line-height: 1.5 !important;

    min-height: 45px !important;

    border-radius: 10px !important;
}


/* ============================================================
   STATUS
============================================================ */

.status {
    padding: 17px;

    margin-top: 10px;

    border-radius: 12px;

    line-height: 1.8;
}

.status-title {
    font-size: 16px;

    font-weight: 700;

    margin-bottom: 5px;
}

.status-text {
    font-size: 14px;

    line-height: 1.8;
}

.status.success {
    background: #ecfdf5 !important;

    border: 1px solid #a7f3d0 !important;

    color: #065f46 !important;
}

.status.success * {
    color: #065f46 !important;
}

.status.error {
    background: #fff1f2 !important;

    border: 1px solid #fecdd3 !important;

    color: #9f1239 !important;
}

.status.error * {
    color: #9f1239 !important;
}

.status.warning {
    background: #fffbeb !important;

    border: 1px solid #fde68a !important;

    color: #92400e !important;
}

.status.warning * {
    color: #92400e !important;
}


/* ============================================================
   PDF PREVIEW
============================================================ */

.pdf-container {
    width: 100%;

    height: 700px;

    overflow-y: auto;

    overflow-x: hidden;

    padding: 20px;

    background: #e2e8f0;

    border-radius: 14px;
}

.pdf-page {
    position: relative;

    width: 100%;

    margin-bottom: 25px;

    background: white;

    border-radius: 5px;

    overflow: hidden;

    box-shadow:
        0 4px 15px
        rgba(0, 0, 0, 0.15);
}

.pdf-page-number {
    position: absolute;

    top: 10px;

    right: 10px;

    z-index: 5;

    padding: 5px 10px;

    border-radius: 15px;

    background: rgba(15, 23, 42, 0.85);

    color: white !important;

    font-size: 12px;

    font-weight: 600;
}

.pdf-page-image {
    display: block;

    width: 100%;

    height: auto;

    margin: 0;

    padding: 0;

    border: none;
}


/* ============================================================
   EMPTY PDF PREVIEW
============================================================ */

.pdf-empty {
    height: 500px;

    display: flex;

    flex-direction: column;

    justify-content: center;

    align-items: center;

    text-align: center;

    background: #f8fafc;

    border: 2px dashed #cbd5e1;

    border-radius: 15px;

    padding: 30px;
}

.pdf-empty-icon {
    font-size: 50px;

    margin-bottom: 12px;
}

.pdf-empty-title {
    color: #1e293b !important;

    font-size: 20px;

    font-weight: 700;

    margin-bottom: 8px;
}

.pdf-empty-text {
    color: #64748b !important;

    font-size: 14px;

    line-height: 1.7;
}


/* ============================================================
   PDF ERROR
============================================================ */

.pdf-error {
    padding: 25px;

    background: #fff1f2;

    border: 1px solid #fecdd3;

    border-radius: 12px;
}

.pdf-error-title {
    color: #9f1239 !important;

    font-size: 18px;

    font-weight: 700;

    margin-bottom: 10px;
}

.pdf-error-text {
    color: #9f1239 !important;

    font-size: 14px;

    line-height: 1.7;
}


/* ============================================================
   ANSWER
============================================================ */

.answer-box {
    background: white !important;

    padding: 22px;

    border-radius: 15px;

    border: 1px solid #e2e8f0;

    box-shadow:
        0 5px 18px
        rgba(15, 23, 42, 0.05);
}

.answer-header {
    display: flex;

    align-items: center;

    gap: 12px;

    margin-bottom: 15px;
}

.answer-icon {
    width: 45px;

    height: 45px;

    display: flex;

    justify-content: center;

    align-items: center;

    border-radius: 12px;

    background: #eef2ff;

    font-size: 22px;
}

.answer-title {
    color: #1e293b !important;

    font-size: 20px;

    font-weight: 700;
}

.answer-subtitle {
    color: #64748b !important;

    font-size: 13px;

    margin-top: 2px;
}

.answer-divider {
    height: 1px;

    background: #e5e7eb;

    margin-bottom: 18px;
}

.answer-text {
    color: #334155 !important;

    font-size: 16px;

    line-height: 1.9;

    word-break: normal;

    overflow-wrap: break-word;
}


/* ============================================================
   EMPTY ANSWER
============================================================ */

.answer-empty {
    text-align: center;

    padding: 50px 20px;

    background: #f8fafc;

    border: 1px dashed #cbd5e1;

    border-radius: 15px;
}

.answer-empty-icon {
    font-size: 42px;

    margin-bottom: 10px;
}

.answer-empty-title {
    color: #334155 !important;

    font-size: 19px;

    font-weight: 700;

    margin-bottom: 8px;
}

.answer-empty-text {
    color: #64748b !important;

    font-size: 14px;

    line-height: 1.7;
}


/* ============================================================
   SOURCES
============================================================ */

.sources-box {
    padding: 22px;

    background: white !important;

    border: 1px solid #e2e8f0;

    border-radius: 15px;

    box-shadow:
        0 5px 18px
        rgba(15, 23, 42, 0.05);
}

.sources-title {
    color: #1e293b !important;

    font-size: 19px;

    font-weight: 700;
}

.sources-subtitle {
    color: #64748b !important;

    font-size: 13px;

    margin-top: 4px;

    margin-bottom: 18px;
}


/* ============================================================
   PAGE BADGES
============================================================ */

.page-list {
    display: flex;

    flex-wrap: wrap;

    gap: 8px;

    margin-bottom: 18px;
}

.page-badge {
    display: inline-block;

    padding: 6px 12px;

    border-radius: 20px;

    background: #eef2ff !important;

    border: 1px solid #c7d2fe;

    color: #3730a3 !important;

    font-size: 13px;

    font-weight: 600;
}


/* ============================================================
   RETRIEVED CONTENT
============================================================ */

.retrieved-details {
    border-top: 1px solid #e5e7eb;

    padding-top: 15px;
}

.retrieved-details summary {
    color: #4338ca !important;

    cursor: pointer;

    font-size: 15px;

    font-weight: 600;

    line-height: 1.6;
}

.chunks-container {
    margin-top: 15px;
}

.chunk-card {
    padding: 16px;

    margin-bottom: 12px;

    background: #f8fafc;

    border-left: 4px solid #6366f1;

    border-radius: 8px;
}

.chunk-header {
    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 10px;
}

.chunk-title {
    color: #334155 !important;

    font-weight: 700;
}

.chunk-page {
    padding: 4px 9px;

    border-radius: 15px;

    background: #e0e7ff;

    color: #3730a3 !important;

    font-size: 12px;

    font-weight: 600;
}

.chunk-text {
    color: #475569 !important;

    font-size: 14px;

    line-height: 1.9;

    white-space: normal;

    word-break: normal;

    overflow-wrap: break-word;
}


/* ============================================================
   MOBILE
============================================================ */

@media (max-width: 768px) {

    .gradio-container {
        padding: 12px !important;
    }

    .header {
        padding: 25px 15px;
    }

    .header h1 {
        font-size: 28px !important;
    }

    .header p {
        font-size: 14px !important;
    }

    .card {
        padding: 16px !important;
    }

    .pdf-container {
        height: 550px;
        padding: 10px;
    }
}
"""


# ============================================================
# GRADIO APPLICATION
# ============================================================

with gr.Blocks(
    title="PDF RAG Assistant",
    css=css,
    theme=gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="purple"
    )
) as demo:

    # ========================================================
    # HEADER
    # ========================================================

    gr.HTML(
        """
        <div class="header">

            <h1>
                📚 PDF RAG Assistant
            </h1>

            <p>
                Upload → Preview → Process → Ask Questions
            </p>

        </div>
        """
    )


    # ========================================================
    # PDF SECTION
    # ========================================================

    with gr.Row():

        # ----------------------------------------------------
        # UPLOAD
        # ----------------------------------------------------

        with gr.Column(
            scale=1,
            elem_classes="card"
        ):

            gr.Markdown(
                """
                ## 📤 Upload PDF

                Select a PDF and click **Process PDF**.
                """
            )

            pdf_file = gr.File(
                label="Choose PDF",
                file_types=[".pdf"],
                type="filepath"
            )

            with gr.Row():

                process_button = gr.Button(
                    "⚙️ Process PDF",
                    variant="primary"
                )

                clear_button = gr.Button(
                    "🗑️ Clear"
                )

            status = gr.HTML(
                """
                <div class="status">

                    <div class="status-title">
                        📄 Ready
                    </div>

                    <div class="status-text">
                        Upload a PDF to get started.
                    </div>

                </div>
                """
            )

            pdf_info = gr.Textbox(
                label="PDF Information",
                interactive=False
            )


        # ----------------------------------------------------
        # PREVIEW
        # ----------------------------------------------------

        with gr.Column(
            scale=2,
            elem_classes="card"
        ):

            gr.Markdown(
                """
                ## 👀 PDF Preview
                """
            )

            pdf_preview = gr.HTML(
                create_pdf_preview(None)
            )


    # ========================================================
    # QUESTION SECTION
    # ========================================================

    gr.Markdown(
        """
        ## 💬 Ask Questions
        """
    )

    with gr.Row():

        with gr.Column(
            scale=2,
            elem_classes="card"
        ):

            question = gr.Textbox(
                label="Your Question",

                placeholder=(
                    "Example: What is the main topic "
                    "of this document?"
                ),

                lines=4
            )

            ask_button = gr.Button(
                "🚀 Ask Question",
                variant="primary"
            )


        with gr.Column(
            scale=3,
            elem_classes="card"
        ):

            answer = gr.HTML(
                """
                <div class="answer-empty">

                    <div class="answer-empty-icon">
                        🤖
                    </div>

                    <div class="answer-empty-title">
                        Ready for your question
                    </div>

                    <div class="answer-empty-text">
                        Upload a PDF and ask a question.
                    </div>

                </div>
                """
            )


    # ========================================================
    # SOURCES
    # ========================================================

    gr.Markdown(
        """
        ## 📖 Sources & Retrieved Context
        """
    )

    sources = gr.HTML(
        """
        <div class="answer-empty">

            <div class="answer-empty-icon">
                📚
            </div>

            <div class="answer-empty-title">
                No sources yet
            </div>

            <div class="answer-empty-text">
                Retrieved PDF content will appear here.
            </div>

        </div>
        """
    )


    # ========================================================
    # FOOTER
    # ========================================================

    gr.HTML(
        """
        <div style="
            text-align:center;
            padding:25px 10px;
            color:#64748b;
            font-size:14px;
            line-height:1.7;
        ">

            🔍 RAG
            &nbsp; • &nbsp;
            🧠 HuggingFace Embeddings
            &nbsp; • &nbsp;
            🗄️ ChromaDB
            &nbsp; • &nbsp;
            🤖 Groq Llama

        </div>
        """
    )


    # ========================================================
    # EVENTS
    # ========================================================

    process_button.click(
        fn=process_pdf,

        inputs=pdf_file,

        outputs=[
            status,
            pdf_info,
            pdf_preview
        ]
    )

    ask_button.click(
        fn=ask_question,

        inputs=question,

        outputs=[
            answer,
            sources
        ]
    )

    clear_button.click(
        fn=clear_app,

        inputs=[],

        outputs=[
            status,
            pdf_info,
            answer,
            pdf_preview
        ]
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🚀 PDF RAG APPLICATION STARTED")
    print("=" * 50)
    print("🌐 Open in your browser:")
    print("👉 http://localhost:7860")
    print("=" * 50 + "\n")

    demo.launch()
