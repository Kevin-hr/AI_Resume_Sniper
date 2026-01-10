
import os
import sys
import logging
import tempfile
import shutil
import json
from typing import Optional, Dict, Any, List
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

@app.post("/optimize_jd", response_model=AnalysisResponse)
async def optimize_jd(
    jd_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None)
):
    """
    Optimize a Job Description (Text or File).
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    final_jd_text = ""
    if jd_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(jd_file.filename)[1]) as tmp:
            shutil.copyfileobj(jd_file.file, tmp)
            tmp_path = tmp.name
        try:
            parser = get_parser_for_file(tmp_path)
            doc = parser.parse(tmp_path)
            final_jd_text = doc.content
        except Exception as e:
            logger.error(f"Error parsing JD file: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to parse JD file: {str(e)}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    elif jd_text:
        final_jd_text = jd_text
    
    if not final_jd_text or len(final_jd_text.strip()) < 10:
         raise HTTPException(status_code=400, detail="Valid JD content is required (min 10 chars)")

    try:
        result = engine.optimize_jd(jd_text=final_jd_text)
        return result
    except ResumeSniperError as e:
        logger.error(f"Optimization error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/batch_parse_resumes")
async def batch_parse_resumes(files: List[UploadFile] = File(...)):
    """
    Batch parse multiple resumes and extract structured data.
    """
    if not engine:
         raise HTTPException(status_code=503, detail="Engine not initialized")
    
    results = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            try:
                # Save uploaded file
                temp_path = os.path.join(temp_dir, file.filename)
                with open(temp_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # Parse document text
                # Note: get_parser_for_file might raise PluginNotFoundError if format not supported
                parser = get_parser_for_file(temp_path)
                parsed_doc = parser.parse(temp_path)
                resume_text = parsed_doc.content
                
                # Extract fields using Engine
                extraction_result = engine.extract_resume_fields(resume_text=resume_text)
                
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "data": extraction_result
                })
                
            except Exception as e:
                logger.error(f"Error processing {file.filename}: {e}")
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })
                
    return results

@app.post("/batch_analyze_match")
async def batch_analyze_match(
    files: List[UploadFile] = File(...),
    jd_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
    weights: Optional[str] = Form(None) # JSON string: {"skills":30, "experience":30...}
):
    """
    Batch analyze match between multiple resumes and a JD (Text or File).
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    # 1. Process JD
    final_jd_text = ""
    if jd_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(jd_file.filename)[1]) as tmp:
            shutil.copyfileobj(jd_file.file, tmp)
            tmp_path = tmp.name
        try:
            parser = get_parser_for_file(tmp_path)
            doc = parser.parse(tmp_path)
            final_jd_text = doc.content
        except Exception as e:
            logger.error(f"Error parsing JD file: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to parse JD file: {str(e)}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    elif jd_text:
        final_jd_text = jd_text
    
    if not final_jd_text or len(final_jd_text.strip()) < 10:
         raise HTTPException(status_code=400, detail="Valid JD content is required")

    # 2. Parse Weights
    match_weights = None
    if weights:
        try:
            match_weights = json.loads(weights)
        except:
            pass # Ignore invalid weights

    # 3. Process Resumes
    results = []
    
    # Process files sequentially (to avoid API rate limits if parallel)
    # For production, this should be a background task (Celery/Redis Queue)
    for file in files:
        # ... (file saving and parsing logic similar to parse_batch)
        # We reuse logic here for simplicity in this MVP
        
        tmp_path = None
        try:
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(file.file, tmp)
                tmp_path = tmp.name
            
            # Parse Resume Text
            parser = get_parser_for_file(tmp_path)
            doc = parser.parse(tmp_path)
            resume_text = doc.content
            
            # Evaluate Match
            analysis = engine.evaluate_match(
                resume_text=resume_text, 
                jd_text=final_jd_text,
                weights=match_weights
            )
            
            # Add filename
            analysis["filename"] = file.filename
            
            # Ensure ID
            if "id" not in analysis:
                analysis["id"] = os.path.splitext(file.filename)[0] # Fallback ID

            results.append(analysis)
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "status": "Error",
                "error": str(e),
                "score": 0,
                "reason": "Processing failed"
            })
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass
                    
    return results

class MessageRequest(BaseModel):
    candidates: List[Dict[str, Any]] # List of {name, reason, etc.}
    job_info: Dict[str, Any] # {role: "Java Dev"}
    msg_type: str # "reject" or "invite"
    options: Dict[str, Any] = {} # {style: "Professional", time: "...", ...}

@app.post("/generate_messages")
async def generate_messages(req: MessageRequest):
    """
    Generate bulk messages for candidates.
    """
    if not engine:
         raise HTTPException(status_code=503, detail="Engine not initialized")
    
    generated_messages = []
    for candidate in req.candidates:
        try:
            msg = engine.generate_message(
                msg_type=req.msg_type,
                candidate_data=candidate,
                job_data=req.job_info,
                options=req.options
            )
            generated_messages.append({
                "candidate_id": candidate.get("id", candidate.get("name")),
                "name": candidate.get("name"),
                "message": msg
            })
        except Exception as e:
            logger.error(f"Error generating message for {candidate.get('name')}: {e}")
            generated_messages.append({
                "candidate_id": candidate.get("id"),
                "error": str(e)
            })
            
    return generated_messages

class TranslationRequest(BaseModel):
    text: str
    target_lang: str = "Chinese"

@app.post("/translate")
async def translate_text(request: TranslationRequest):
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    try:
        translated = engine.translate_text(request.text, request.target_lang)
        return {"translated_text": translated}
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Allow running directly for testing
    uvicorn.run(app, host="0.0.0.0", port=8000)
