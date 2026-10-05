from groq import Groq

from config import (
    GROQ_API_KEY,
    GROQ_MODEL
)


# Create Groq client
groq_client = Groq(
    api_key=GROQ_API_KEY
)


def generate_answer(
    question,
    retrieved_documents
):
    """
    Generate an answer using Groq.

    The retrieved PDF chunks are given
    to the LLM as context.
    """

    if not retrieved_documents:

        return (
            "I could not find relevant "
            "information in the PDF.",
            []
        )

    # --------------------------------------------------------
    # Create context
    # --------------------------------------------------------

    context_parts = []

    source_pages = []

    for document in retrieved_documents:

        page = document.metadata.get(
            "page",
            "Unknown"
        )

        source_pages.append(page)

        context_parts.append(
            f"[Page {page}]\n"
            f"{document.page_content}"
        )

    context = "\n\n".join(
        context_parts
    )

    # --------------------------------------------------------
    # Create prompt
    # --------------------------------------------------------

    prompt = f"""
You are a PDF question-answering assistant.

Answer the user's question using ONLY
the information provided in the PDF context.

If the answer is not available in the
context, say:

"The answer is not available in
the uploaded PDF."

Do not invent information.

Keep the answer clear and simple.

-------------------------
PDF CONTEXT
-------------------------

{context}

-------------------------
QUESTION
-------------------------

{question}

-------------------------
ANSWER
-------------------------
"""

    # --------------------------------------------------------
    # Call Groq
    # --------------------------------------------------------

    response = groq_client.chat.completions.create(

        model=GROQ_MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,

        max_tokens=1000
    )

    answer = response.choices[0].message.content

    return answer, sorted(set(source_pages))
