from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_chroma import Chroma

from embeddings import get_embedding_model


# Load embedding model once
embedding_model = get_embedding_model()


def create_chunks(pages):
    """
    Split PDF pages into smaller chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = []

    for page in pages:

        page_chunks = splitter.split_text(
            page["text"]
        )

        for chunk in page_chunks:

            chunks.append(
                {
                    "text": chunk,
                    "page": page["page"]
                }
            )

    return chunks


def create_vector_database(chunks):
    """
    Convert chunks into embeddings
    and store them in ChromaDB.
    """

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    metadatas = [
        {
            "page": chunk["page"]
        }
        for chunk in chunks
    ]

    vector_db = Chroma.from_texts(
        texts=texts,
        embedding=embedding_model,
        metadatas=metadatas,
        collection_name="pdf_rag_collection"
    )

    return vector_db


def search_documents(vector_db, question, k=4):
    """
    Find the most relevant chunks
    for the user's question.
    """

    if vector_db is None:

        return []

    results = vector_db.similarity_search(
        question,
        k=k
    )

    return results
