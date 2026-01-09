
import os
import sys
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.engine import ResumeSniperEngine
from src.core.config import get_config
from src.core.exceptions import ResumeSniperError, UnsupportedFormatError
from src.plugins.document_parsers import get_parser_for_file, get_parser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_server")

# Global Engine Instance
engine: Optional[ResumeSniperEngine] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize engine on startup."""
    global engine
    try:
        logger.info("Initializing Resume Sniper Engine...")
        engine = ResumeSniperEngine()
        logger.info("Engine initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize engine: {e}")
        # We don't raise here to allow the server to start, but health check will fail
    yield
    # Cleanup if necessary
    logger.info("Shutting down...")

app = FastAPI(
    title="AI Resume Sniper API",
    description="Backend API for AI Resume Sniper (WeChat Mini Program compatible)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
# For production, replace "*" with specific domains (e.g., "https://bmwuv.com")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow WeChat Mini Program and Web
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---

class AnalysisResponse(BaseModel):
    report: str
    score: Optional[int] = None
    model: str
    tokens_used: int
    latency_ms: float
    cached: bool
    metadata: Dict[str, Any]

class HealthCheckResponse(BaseModel):
    status: str
    engine_status: Dict[str, Any]
    version: str

# --- Helper Functions ---

def get_file_extension(filename: str) -> str:
    """Extract and validate file extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower()

async def _process_upload_request(
    resume_file: UploadFile,
    jd_file: Optional[UploadFile],
    jd_text: Optional[str]
) -> tuple[str, str]:
    """Helper to process uploaded files and text."""
    # 0. Process JD (Text or File)
    final_jd_text = ""
    
    if jd_file:
        # Parse JD file
        jd_ext = get_file_extension(jd_file.filename)
        logger.info(f"Received JD file: {jd_file.filename} ({jd_ext})")
        
        # Map extension to parser
        ext_map = {
            '.pdf': 'pdf',
            '.docx': 'docx',
            '.doc': 'docx',
            '.txt': 'text',
            '.md': 'text'
        }
        jd_parser_name = ext_map.get(jd_ext)
        if not jd_parser_name:
                raise HTTPException(
                status_code=400, 
                detail=f"Unsupported JD file format: {jd_ext}. Supported: PDF, DOCX, TXT, MD"
            )
        
        jd_parser = get_parser(jd_parser_name)
        jd_bytes = await jd_file.read()
        try:
            final_jd_text = jd_parser.parse_content(jd_bytes, jd_ext)
        except Exception as e:
            logger.error(f"JD Parsing error: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to parse JD file: {str(e)}")
    
    elif jd_text:
        final_jd_text = jd_text
    
    if not final_jd_text or len(final_jd_text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Job Description is required (text or file)")

    # 1. Validate resume file extension
    ext = get_file_extension(resume_file.filename)
    logger.info(f"Received file: {resume_file.filename} ({ext})")

    # 2. Get appropriate parser
    ext_map = {
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.doc': 'docx',
        '.txt': 'text',
        '.md': 'text'
    }
    
    parser_name = ext_map.get(ext)
    if not parser_name:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format: {ext}. Supported: PDF, DOCX, TXT, MD"
        )

    parser = get_parser(parser_name)

    # 3. Read file content
    content_bytes = await resume_file.read()
    
    # 4. Parse content
    try:
        resume_text = parser.parse_content(content_bytes, ext)
    except Exception as e:
        logger.error(f"Parsing error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if not resume_text or len(resume_text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Parsed resume content is empty")

    return resume_text, final_jd_text


# --- Endpoints ---

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Check system health."""
    if not engine:
        return HealthCheckResponse(
            status="unhealthy", 
            engine_status={"error": "Engine not initialized"},
            version="1.0.0"
        )
    
    try:
        health = engine.health_check()
        status_str = "healthy" if health.get("llm_provider", {}).get("healthy") else "degraded"
        return HealthCheckResponse(
            status=status_str,
            engine_status=health,
            version="1.0.0"
        )
    except Exception as e:
        return HealthCheckResponse(
            status="error",
            engine_status={"error": str(e)},
            version="1.0.0"
        )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume_file: UploadFile = File(...),
    jd_text: Optional[str] = Form(default=None),
    jd_file: Optional[UploadFile] = File(default=None),
    persona: str = Form("hrbp"),
):
    """
    Analyze a resume file against a job description.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    resume_text, final_jd_text = await _process_upload_request(resume_file, jd_file, jd_text)

    try:
        # 5. Call Engine
        result = engine.analyze_resume(
            resume_text=resume_text,
            jd_text=final_jd_text,
            persona=persona
        )
        
        return result
        
    except ResumeSniperError as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/analyze_stream")
async def analyze_resume_stream(
    resume_file: UploadFile = File(...),
    jd_text: Optional[str] = Form(default=None),
    jd_file: Optional[UploadFile] = File(default=None),
    persona: str = Form("hrbp"),
):
    """
    Analyze a resume file against a job description with streaming response.
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    resume_text, final_jd_text = await _process_upload_request(resume_file, jd_file, jd_text)

    try:
        def stream_with_ping(generator):
            """Yield a space immediately to establish connection."""
            yield " "
            yield from generator

        return StreamingResponse(
            stream_with_ping(engine.analyze_resume_stream(
                resume_text=resume_text,
                jd_text=final_jd_text,
                persona=persona,
                use_cache=False  # Disable cache for streaming to ensure reasoning/thinking process is shown
            )),
            media_type="text/event-stream"
        )
        
    except ResumeSniperError as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    # Allow running directly for testing
    uvicorn.run(app, host="0.0.0.0", port=8000)
