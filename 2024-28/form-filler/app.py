import json
import os
import tempfile
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from pinecone import Pinecone, ServerlessSpec
    from langchain_pinecone import PineconeVectorStore
    from groq import Groq
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install: pip install -r requirements.txt")
    exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Smart Form Filler API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FormFillRequest(BaseModel):
    schema_json: str
    gemini_key: Optional[str] = None
    groq_key: Optional[str] = None
    pinecone_key: Optional[str] = None
    pinecone_env: Optional[str] = None
    pinecone_host: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str

INDEX_NAME = "smart-form-filler"
vector_store = None


def _resolve_key(value: Optional[str], headers: dict, header_name: str, env_name: str) -> Optional[str]:
    if value and isinstance(value, str) and value.strip():
        return value.strip()
    if headers:
        for k, v in headers.items():
            if k.lower() == header_name.lower() and v and v.strip():
                return v.strip()
    env_val = os.getenv(env_name)
    if env_val and env_val.strip():
        return env_val.strip()
    return None


@app.get("/", response_model=HealthResponse)
async def health_check():
    logger.info("Health check endpoint hit")
    return HealthResponse(status="healthy", message="Smart Form Filler API is up and running !")  # ✅ small change #1


@app.post("/upload-pdfs")
async def upload_and_process_pdfs(
    pdfs: List[UploadFile] = File(...),
    gemini_key: Optional[str] = Form(None),
    pinecone_key: Optional[str] = Form(None),
    pinecone_env: Optional[str] = Form(None),
    pinecone_host: Optional[str] = Form(None),
    http_request: Request = None,
):
    try:
        logger.info(f"🔄 Processing... {len(pdfs)} PDF(s)")  # ✅ small change #2

        if not pdfs:
            raise HTTPException(status_code=400, detail="No PDF files provided")

        headers = http_request.headers if http_request else {}
        resolved_gemini = _resolve_key(gemini_key, headers, "x-gemini-key", "GOOGLE_API_KEY")
        resolved_pinecone_key = _resolve_key(pinecone_key, headers, "x-pinecone-key", "PINECONE_API_KEY")
        resolved_pinecone_env = _resolve_key(pinecone_env, headers, "x-pinecone-env", "PINECONE_ENV")
        resolved_pinecone_host = _resolve_key(pinecone_host, headers, "x-pinecone-host", "PINECONE_HOST")

        if not resolved_gemini or not resolved_pinecone_key or not (resolved_pinecone_env or resolved_pinecone_host):
            raise HTTPException(status_code=400, detail="Missing required Pinecone or Gemini configuration")

        pc = Pinecone(api_key=resolved_pinecone_key)
        index = pc.Index(host=resolved_pinecone_host) if resolved_pinecone_host else pc.Index(INDEX_NAME)

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=resolved_gemini,
            task_type="RETRIEVAL_DOCUMENT"
        )

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

        all_documents = []

        for pdf_file in pdfs:
            if not pdf_file.filename.lower().endswith(".pdf"):
                continue

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(await pdf_file.read())
                temp_path = temp_file.name

            loader = PyPDFLoader(temp_path)
            pages = loader.load()

            chunks = text_splitter.split_documents(pages)
            all_documents.extend(chunks)

            os.unlink(temp_path)

        if not all_documents:
            raise HTTPException(status_code=400, detail="No valid text found in PDFs")

        contents = [doc.page_content for doc in all_documents]
        embeddings_list = embeddings.embed_documents(contents)

        vectors_to_upsert = []
        for i, (doc, embedding) in enumerate(zip(all_documents, embeddings_list)):
            vectors_to_upsert.append({
                "id": f"chunk_{i}",
                "values": embedding,
                "metadata": {"page_content": doc.page_content}
            })

        index.upsert(vectors=vectors_to_upsert)

        return {
            "status": "success",
            "message": "PDFs processed successfully",
            "chunks_count": len(all_documents)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fill-form")
async def fill_form(request: FormFillRequest, http_request: Request):
    try:
        logger.info("🔄 Processing form fill request")

        if not request.schema_json:
            raise HTTPException(status_code=400, detail="Schema JSON is required")

        headers = http_request.headers
        gemini_key = _resolve_key(request.gemini_key, headers, "x-gemini-key", "GOOGLE_API_KEY")
        groq_key = _resolve_key(request.groq_key, headers, "x-groq-key", "GROQ_API_KEY")
        pinecone_key = _resolve_key(request.pinecone_key, headers, "x-pinecone-key", "PINECONE_API_KEY")
        pinecone_env = _resolve_key(request.pinecone_env, headers, "x-pinecone-env", "PINECONE_ENV")
        pinecone_host = _resolve_key(request.pinecone_host, headers, "x-pinecone-host", "PINECONE_HOST")

        if not all([gemini_key, groq_key, pinecone_key, (pinecone_env or pinecone_host)]):
            raise HTTPException(status_code=400, detail="Missing credentials")

        try:
            form_schema = json.loads(request.schema_json)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid schema JSON")

        if not isinstance(form_schema, list):
            raise HTTPException(status_code=400, detail="Schema must be a list")

        pc = Pinecone(api_key=pinecone_key)
        index = pc.Index(host=pinecone_host) if pinecone_host else pc.Index(INDEX_NAME)

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=gemini_key,
            task_type="RETRIEVAL_QUERY"
        )

        field_labels = [field.get("label") for field in form_schema if isinstance(field, dict)]
        query_text = " ".join(field_labels)

        query_embedding = embeddings.embed_query(query_text)

        search_results = index.query(
            vector=query_embedding,
            top_k=10,
            include_metadata=True
        )

        context_chunks = [
            match.metadata.get("page_content", "")
            for match in search_results.matches
            if match.score > 0.5
        ]

        context = "\n\n".join(context_chunks) or "No relevant context found."

        groq_client = Groq(api_key=groq_key)

        prompt = f"""
Fill form fields using the given context.

FORM:
{json.dumps(form_schema, indent=2)}

CONTEXT:
{context}

Return valid JSON only.
"""

        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2048
        )

        ai_response = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(ai_response)
        except:
            parsed = {}

        return {
            "status": "success",
            "answers_json": json.dumps(parsed),
            "context_used": len(context_chunks) > 0,
            "answers_count": len(parsed)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    return {
        "status": "active",   # ✅ small change #3
        "index_name": INDEX_NAME,
        "version": "1.0.0",
        "timestamp": str(datetime.now())
    }


@app.get("/debug/index-stats")
async def debug_index_stats(pinecone_key: str = None, pinecone_host: str = None):
    if not pinecone_key:
        raise HTTPException(status_code=400, detail="Pinecone API key required")

    try:
        pc = Pinecone(api_key=pinecone_key)
        index = pc.Index(host=pinecone_host) if pinecone_host else pc.Index(INDEX_NAME)
        return index.describe_index_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
