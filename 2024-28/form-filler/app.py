import json
import os
import tempfile
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

missing_packages = []

try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from pinecone import Pinecone, ServerlessSpec
    from langchain_pinecone import PineconeVectorStore
    from groq import Groq
except ImportError as e:
    # Collect missing package errors and continue in degraded mode so the app can start
    missing_packages.append(str(e))
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.error("Missing required package: %s", e)
    logger.error("Proceeding in degraded mode. To enable full functionality install: pip install -r requirements.txt")
    # Do not exit here so REST API can still respond with helpful error messages later

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

def ensure_deps_installed():
    if missing_packages:
        logger.error("Missing dependencies detected: %s", "; ".join(missing_packages))
        raise HTTPException(
            status_code=500,
            detail="Missing dependencies: " + "; ".join(missing_packages) + ". Install with: pip install -r requirements.txt"
        )

def _normalize_headers(http_request: Optional[Request]) -> dict:
    headers = {}
    if not http_request:
        return headers
    raw = getattr(http_request, "headers", None)
    if not raw:
        return headers
    try:
        headers = {k.lower(): v for k, v in dict(raw).items()}
    except Exception:
        try:
            headers = {k.lower(): v for k, v in raw.items()}
        except Exception:
            headers = {}
    return headers


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
        # pdf count validation
        if len(pdfs) == 0:
            raise HTTPException(status_code=400, detail="No PDF files provided")
        elif len(pdfs) > 10:
            logger.warning(f"⚠️ Large batch: Processing {len(pdfs)} PDF files")
        else:
            logger.info(f"🔄 Processing {len(pdfs)} PDF files")

         # Enhanced pdf validation with file type check and robust size detection
        total_size = 0
        for pdf in pdfs:
            if not pdf.filename:
                raise HTTPException(status_code=400, detail="Invalid PDF filename")
            if not pdf.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"Invalid file type: {pdf.filename} (must be PDF)")

            # Some UploadFile implementations might not expose size; guard against AttributeError
            file_size = getattr(pdf, "size", None)
            if file_size is None:
                # best-effort: read to compute size (dangerous for very large files)
                content = await pdf.read()
                file_size = len(content)
                # reset the file's internal pointer for later reuse
                try:
                    pdf.file.seek(0)
                except Exception:
                    pass
            if file_size == 0:
                raise HTTPException(status_code=400, detail=f"Empty file: {pdf.filename}")
            total_size += file_size

        # Size validation with more informative message 
        # 50MB total limit
        if total_size > 50_000_000:
            raise HTTPException(
                status_code=400, 
                detail=f"Total PDF size ({total_size/1_000_000:.1f}MB) exceeds 50MB limit"
)

# Normalize headers to a plain dict with lowercase keys for consistent lookups
headers = {}
if http_request and getattr(http_request, "headers", None):
    try:
        raw_headers = http_request.headers
        try:
            headers = {k.lower(): v for k, v in raw_headers.items()}
        except Exception:
            # Fallbacks in case headers isn't iterable as expected
            try:
                headers = dict(raw_headers)
                headers = {k.lower(): v for k, v in headers.items()}
            except Exception:
                headers = {}
    except Exception:
        headers = {}
else:
    headers = {}

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

            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(await pdf_file.read())
                    temp_path = temp_file.name

                loader = PyPDFLoader(temp_path)
                pages = loader.load()

                chunks = text_splitter.split_documents(pages)
                all_documents.extend(chunks)
                logger.info(f"✅ Created {len(chunks)} chunks from {pdf_file.filename}")

            except Exception as e:
                error_type = str(type(e).__name__)
                error_msg = str(e).lower()
                
                # Specific error handling for common PDF issues
                if "encrypted" in error_msg:
                    logger.error(f"❌ Cannot process encrypted PDF: {pdf_file.filename}")
                elif "password" in error_msg:
                    logger.error(f"❌ Password-protected PDF not supported: {pdf_file.filename}")
                elif "corrupted" in error_msg or "invalid" in error_msg:
                    logger.error(f"❌ Corrupted or invalid PDF: {pdf_file.filename}")
                elif "memory" in error_msg:
                    logger.error(f"❌ PDF too large to process: {pdf_file.filename}")
                else:
                    logger.error(f"❌ Error ({error_type}) processing PDF {pdf_file.filename}: {str(e)}")
                
                # Log stack trace for unexpected errors
                if error_type not in ["PDFSyntaxError", "PDFPasswordError", "PDFPageCountError"]:
                    logger.exception("Unexpected PDF processing error")
                continue
            
            finally:
                try:
                    if temp_path and os.path.exists(temp_path):
                        os.unlink(temp_path)
                except:
                    pass

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
        "status": "active",
        "index_name": INDEX_NAME,
        "version": "1.0.0",
        "timestamp": str(datetime.now())
    }


@app.get("/debug/index-stats")
async def debug_index_stats(pinecone_key: str = None, pinecone_host: str = None):
    try:
        # Ensure dependencies before introspecting Pinecone index
        ensure_deps_installed()

        if not pinecone_key:
            raise HTTPException(status_code=400, detail="Pinecone API key required")

        pc = Pinecone(api_key=pinecone_key)
        index = pc.Index(host=pinecone_host) if pinecone_host else pc.Index(INDEX_NAME)
        return index.describe_index_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
