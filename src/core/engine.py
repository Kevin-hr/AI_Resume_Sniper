"""
Resume Sniper Engine v1.3 / 简历狙击手引擎 v1.3

Plugin-based architecture for AI resume analysis.
"""

import os
import sys
import time
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# Load .env file
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).parent.parent.parent / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    pass

from src.core.config import get_config, AppConfig
from src.core.exceptions import (
    ResumeSniperError,
    PluginNotFoundError,
    LLMProviderError,
    UnsupportedFormatError,
    AnalysisError,
)
from src.interfaces.illm_provider import ILLMProvider, LLMResponse
from src.interfaces.idocument_parser import IDocumentParser, ParsedDocument
from src.interfaces.istorage import IStorage
from src.plugins.llm_providers import get_provider as get_llm_provider
from src.plugins.document_parsers import get_parser_for_file
from src.plugins.storage import get_storage


@dataclass
class AnalysisResult:
    """Result of resume analysis."""
    report: str
    score: Optional[int] = None
    model: str = ""
    tokens_used: int = 0
    latency_ms: float = 0.0
    cached: bool = False
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ResumeSniperEngine:
    """
    Main engine for AI Resume Sniper.

    v1.3 introduces plugin-based architecture supporting:
    - Multiple LLM providers (DeepSeek, OpenAI, Anthropic)
    - Multiple document parsers (PDF, DOCX, Text)
    - Multiple storage backends (Local, Memory)
    - Request caching for cost optimization
    - Automatic retry with exponential backoff
    """

    def __init__(self, config: AppConfig = None, **kwargs):
        """
        Initialize the Resume Sniper engine.

        Args:
            config: AppConfig object (uses global config if None)
            **kwargs: Override configuration parameters
        """
        self._config = config or get_config()
        self._llm_provider: Optional[ILLMProvider] = None
        self._storage: Optional[IStorage] = None
        self._personas = self._load_personas()

        # Initialize components
        self._setup_llm_provider(kwargs.get('llm_provider'))
        self._setup_storage()

    def _load_personas(self) -> Dict:
        """Load available analysis personas."""
        personas = self._config.analysis.get("personas", {})
        return {
            "hrbp": personas.get("hrbp", {
                "name": "Senior HRBP",
                "description": "Direct, result-oriented, harsh but professional",
                "system_prompt": self._get_default_hrbp_prompt()
            }),
            "candidate": personas.get("candidate", {
                "name": "Candidate Coach",
                "description": "Friendly, supportive, encouraging",
                "system_prompt": self._get_default_candidate_prompt()
            })
        }

    def _get_default_hrbp_prompt(self) -> str:
        """Get default HRBP system prompt."""
        return """
        You are a Senior HRBP (10+ years exp) at a top-tier Tech Giant (BAT/FAANG).
        Your personality is: Direct, Result-Oriented, Slightly Harsh, but Extremely Professional.
        You do NOT care about "effort", you only care about "VALUE" and "ROI".
        Your Goal: Help the candidate pass the ATS and the 6-second HR screening.
        """

    def _get_default_candidate_prompt(self) -> str:
        """Get default candidate advocate prompt."""
        return """
        You are a supportive career advocate with 15 years of experience helping professionals advance their careers.
        Your personality is: Encouraging, Empathetic, Practical.
        You focus on helping candidates identify their strengths and improvement areas in a constructive way.
        Your Goal: Empower the candidate, boost their confidence, and provide actionable advice to improve their resume matching the JD.
        """

    def _get_default_headhunter_prompt(self) -> str:
        """Get default Headhunter prompt (B-Side)."""
        return """
        You are a Top-Billing Agency Recruiter (Headhunter) serving high-end corporate clients.
        Your Client is the Hiring Manager, NOT the candidate.
        
        Your Mindset:
        1. **Speed**: Can I sell this candidate to the client in 3 sentences?
        2. **Risk**: What will make the client fire me if I recommend this guy? (Job hopping, fake resume, bad comms).
        3. **Placement Fee**: Is this candidate worth my 25% commission?

        Your Goal: Produce a "Candidate Presentation Note" that I can copy-paste to my Client.
        """

    def _get_diagnostic_prompt(self) -> str:
        """Get diagnostic prompt for deep resume analysis (No JD)."""
        return """
        You are a Senior HRBP (15+ years exp) and a Career Strategist.
        Your goal is to perform a "Deep Diagnostic" of the candidate based ONLY on their resume.
        You need to identify their "Hidden Value" and provide a strategy for "Skill Productization".
        
        Analyze the resume and output the following sections in Markdown:

        ## 1. 🔍 Professional Identity Audit (我是谁?)
        - **The Harsh Truth**: In one direct sentence, define who they are professionally (e.g., "A solid executor but lacks strategic leadership visibility").
        - **Market Value**: High / Medium / Low. Explain why in 1 bullet point.
        
        ## 2. 💎 Hidden Assets (隐性价值挖掘)
        - Identify 3 skills or experiences they have that are UNDERVALUED or poorly presented.
        - Explain *why* these are valuable (e.g., "Cross-functional coordination is actually Project Management").

        ## 3. 🚀 Skill Productization Priority (P0-P5) (技能变现路径)
        Rank their skills/assets by "Monetization Potential" (Ease of selling * Value).
        
        - **P0 (Cash Cow / Immediate)**: What can they sell NOW? (e.g., Consulting, specific tech stack implementation).
        - **P1 (High Potential)**: Needs packaging. (e.g., "Industry SOPs", "Team Management Methodology").
        - **P2 (Growth Area)**: Good but needs more proof.
        - **P3-P5 (Long Tail)**: Nice to have, but not a primary product.

        ## 4. 💡 Strategic Advice
        - One "Golden Rule" for this candidate to break through their current ceiling.

        TONE: Insightful, Strategic, Professional, "Tough Love".
        LANGUAGE: Chinese (Simplified).
        """

    def _setup_llm_provider(self, provider_name: str = None):
        """Initialize the LLM provider."""
        provider = provider_name or self._get_default_provider()

        # Check if provider is enabled
        provider_config = self._config.get_llm_provider_config(provider)
        if not provider_config or not provider_config.enabled:
            # Try DeepSeek as fallback
            fallback = self._config.get_llm_provider_config("deepseek")
            if fallback and fallback.enabled:
                provider = "deepseek"
                provider_config = fallback
            else:
                raise PluginNotFoundError(
                    f"No enabled LLM provider found. "
                    f"Please enable a provider in config or set DEEPSEEK_API_KEY."
                )

        try:
            self._llm_provider = get_llm_provider(
                provider,
                config=provider_config
            )
            self._current_provider = provider
        except Exception as e:
            raise PluginNotFoundError(f"Failed to initialize LLM provider '{provider}': {e}")

    def _get_default_provider(self) -> str:
        """Get the default provider from config."""
        enabled = self._config.get_enabled_providers()
        if not enabled:
            return "deepseek"
        return enabled[0]

    def _setup_storage(self):
        """Initialize the storage backend."""
        if not self._config.storage.enabled:
            self._storage = None
            return

        try:
            self._storage = get_storage(
                self._config.storage.backend,
                cache_dir=self._config.cache_dir
            )
        except Exception as e:
            print(f"Warning: Failed to initialize storage: {e}")
            self._storage = None

    def set_llm_provider(self, provider_name: str):
        """
        Switch to a different LLM provider at runtime.

        Args:
            provider_name: Name of the provider to use
        """
        self._setup_llm_provider(provider_name)

    def analyze(
        self,
        resume_text: str,
        jd_text: str,
        persona: str = "hrbp",
        use_cache: bool = True,
        **kwargs
    ) -> AnalysisResult:
        """
        Analyze resume against job description.

        Args:
            resume_text: Resume content as text
            jd_text: Job description content as text
            persona: Analysis persona ("hrbp" or "coach")
            use_cache: Whether to use cached results
            **kwargs: Additional parameters (temperature, model, etc.)

        Returns:
            AnalysisResult object with report and metadata
        """
        # Check cache first
        if use_cache and self._storage:
            cache_key = self._generate_cache_key(resume_text, jd_text, persona)
            cached = self._storage.load(cache_key)
            if cached:
                return AnalysisResult(
                    report=cached["report"],
                    score=cached.get("score"),
                    model=cached.get("model", ""),
                    tokens_used=cached.get("tokens_used", 0),
                    cached=True,
                    metadata={"cache_key": cache_key}
                )

        # Get persona
        if persona not in self._personas:
            persona = "hrbp"
        persona_data = self._personas[persona]

        # Construct prompt
        prompt = self._construct_prompt(resume_text, jd_text, persona_data)

        # Get model and temperature from kwargs or config
        model = kwargs.pop("model", None)
        temperature = kwargs.pop("temperature", 0.7)

        if self._config.get_model_config(self._current_provider):
            model_info = self._config.get_model_config(self._current_provider, model)
            if model_info:
                temperature = model_info.temperature
                model = model_info.name

        # Call LLM with retry
        start_time = time.time()
        try:
            response = self._call_llm_with_retry(
                messages=[
                    {"role": "system", "content": persona_data["system_prompt"]},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                temperature=temperature,
                **kwargs
            )

            latency_ms = (time.time() - start_time) * 1000
            report = response.content
            score = self._extract_score(report)

            result = AnalysisResult(
                report=report,
                score=score,
                model=response.model,
                tokens_used=response.tokens_used,
                latency_ms=latency_ms,
                cached=False,
                metadata={"persona": persona, "provider": self._current_provider}
            )

            # Save to cache
            if use_cache and self._storage:
                cache_key = self._generate_cache_key(resume_text, jd_text, persona)
                self._storage.save(
                    cache_key,
                    {
                        "report": report,
                        "score": score,
                        "model": response.model,
                        "tokens_used": response.tokens_used
                    },
                    ttl=self._config.storage.cache_ttl
                )

            return result

        except LLMProviderError as e:
            raise AnalysisError(f"LLM provider error: {e}")

    def analyze_resume_stream(
        self,
        resume_text: str,
        jd_text: str = None,
        persona: str = "hrbp",
        use_cache: bool = True,
        **kwargs
    ):
        """
        Analyze resume against JD with streaming response.
        Yields chunks of text.
        """
        # Check if cache exists
        if use_cache and self._storage:
            cache_key = self._generate_cache_key(resume_text, jd_text, persona)
            cached = self._storage.load(cache_key)
            if cached:
                yield cached["report"]
                return

        # Get persona
        if persona not in self._personas:
            persona = "hrbp"
        persona_data = self._personas[persona]

        # Construct prompt
        prompt = self._construct_prompt(resume_text, jd_text, persona_data)

        # Get model config
        model = kwargs.pop("model", None)
        temperature = kwargs.pop("temperature", 0.7)
        if self._config.get_model_config(self._current_provider):
            model_info = self._config.get_model_config(self._current_provider, model)
            if model_info:
                temperature = model_info.temperature
                model = model_info.name

        # Stream response
        full_report = []
        try:
            stream = self._llm_provider.chat_stream(
                messages=[
                    {"role": "system", "content": persona_data["system_prompt"]},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                temperature=temperature,
                **kwargs
            )

            for chunk in stream:
                full_report.append(chunk)
                yield chunk

        except Exception as e:
            # If streaming fails mid-way, we might yield an error message or raise
            # But the client might have already received partial data.
            # We'll log and re-raise.
            print(f"Streaming Error: {e}")
            raise AnalysisError(f"Streaming failed: {e}")

        # Save to cache after complete
        if use_cache and self._storage:
            report = "".join(full_report)
            score = self._extract_score(report)
            cache_key = self._generate_cache_key(resume_text, jd_text, persona)
            self._storage.save(
                cache_key,
                {
                    "report": report,
                    "score": score,
                    "model": model,
                    "tokens_used": 0 # Estimate or skip
                },
                ttl=self._config.storage.cache_ttl
            )

    def diagnose_resume(
        self,
        resume_text: str,
        persona: str = "hrbp",
        use_cache: bool = True,
        **kwargs
    ) -> AnalysisResult:
        """
        Perform a deep diagnostic of the resume (No JD required).
        """
        # Diagnostic Prompt
        system_prompt = self._get_diagnostic_prompt()
        user_prompt = f"Here is the candidate's resume:\n\n{resume_text}\n\nPlease perform the Deep Diagnostic."

        # Cache Key (Use "DIAGNOSTIC" as jd_text placeholder)
        if use_cache and self._storage:
            cache_key = self._generate_cache_key(resume_text, "DIAGNOSTIC", persona)
            cached = self._storage.load(cache_key)
            if cached:
                return AnalysisResult(
                    report=cached["report"],
                    score=None, # Diagnostic usually doesn't have a score
                    model=cached.get("model", ""),
                    tokens_used=cached.get("tokens_used", 0),
                    cached=True,
                    metadata={"cache_key": cache_key, "type": "diagnostic"}
                )

        # Get model config (pop to avoid passing to LLM twice)
        model = kwargs.pop("model", None)
        temperature = kwargs.pop("temperature", 0.7)
        if self._config.get_model_config(self._current_provider):
            model_info = self._config.get_model_config(self._current_provider, model)
            if model_info:
                temperature = model_info.temperature
                model = model_info.name

        # Call LLM
        start_time = time.time()
        try:
            response = self._call_llm_with_retry(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=model,
                temperature=temperature,
                **kwargs
            )

            latency_ms = (time.time() - start_time) * 1000
            report = response.content
            
            result = AnalysisResult(
                report=report,
                score=None,
                model=response.model,
                tokens_used=response.tokens_used,
                latency_ms=latency_ms,
                cached=False,
                metadata={"persona": persona, "provider": self._current_provider, "type": "diagnostic"}
            )

            # Save to cache
            if use_cache and self._storage:
                cache_key = self._generate_cache_key(resume_text, "DIAGNOSTIC", persona)
                self._storage.save(
                    cache_key,
                    {
                        "report": report,
                        "score": None,
                        "model": response.model,
                        "tokens_used": response.tokens_used
                    },
                    ttl=self._config.storage.cache_ttl
                )

            return result

        except LLMProviderError as e:
            raise AnalysisError(f"LLM provider error: {e}")

    def _call_llm_with_retry(
        self,
        messages: List[Dict],
        model: str = None,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Call LLM with automatic retry on failure.

        Implements exponential backoff for rate limits.
        """
        # Safety: Remove any remaining duplicate args
        kwargs.pop('model', None)
        kwargs.pop('temperature', None)

        provider_config = self._config.get_llm_provider_config(self._current_provider)
        max_retries = provider_config.max_retries if provider_config else 3

        last_error = None
        for attempt in range(max_retries):
            try:
                return self._llm_provider.chat(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    **kwargs
                )
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # Exponential backoff
                    time.sleep(wait_time)

        raise last_error

    def _construct_prompt(
        self,
        resume_text: str,
        jd_text: str,
        persona_data: Dict
    ) -> str:
        """Construct the analysis prompt."""
        # Check if this is a Headhunter persona
        if persona_data.get("name") == "B-Side Headhunter":
            return self._construct_headhunter_prompt(resume_text, jd_text)

        prompt = f"""
TASK:
Analyze the following Candidate Resume against the Target Job Description (JD).

TARGET JD:
{jd_text}

CANDIDATE RESUME:
{resume_text}

OUTPUT REQUIREMENTS (Markdown Format):

## 1. Match Score (0-100)
- Give a brutally honest score.
- < 60: Trash bin immediately.
- 60-80: Backup pile.
- > 80: Interview invite.

## 2. Fatal Red Flags (The "Why No")
- List top 3 reasons why an HR would REJECT this resume in 6 seconds.
- Be specific (e.g., "Vague descriptions", "No metrics", "Job hopping").

## 3. The "Money" Bullet Points (STAR Rewrite)
- Pick the ONE most relevant experience from the resume.
- Rewrite it into 3 bullet points using strict STAR format (Situation -> Task -> Action -> Result).
- MUST include quantitative metrics (%, $, time saved).
- If metrics are missing in source, use placeholders like [Increase by X%] and tell user to fill it.

## 4. Quick Fixes (Actionable Advice)
- 3 things the candidate can change RIGHT NOW to boost the score by 10 points.

## 5. Skill Radar (JSON)
Output a JSON block for radar chart visualization with exactly 6 dimensions:
```json
{{"radar": {{"专业技能": 0-100, "项目经验": 0-100, "学历背景": 0-100, "行业匹配": 0-100, "软技能": 0-100, "成长潜力": 0-100}}}}
```
Replace the values (0-100) with your actual assessment scores.

TONE: Professional but critical. No fluff. No "Good job". Focus on GAP analysis.
LANGUAGE: 全部使用中文输出 (All output must be in Simplified Chinese).
        """
        return prompt

    def _construct_headhunter_prompt(
        self,
        resume_text: str,
        jd_text: str
    ) -> str:
        """Construct the prompt specifically for Headhunters (B-Side)."""
        prompt = f"""
TASK:
You are preparing a Candidate Presentation for your Client (Hiring Manager).
Analyze the candidate's resume against the Job Description (JD).

TARGET JD:
{jd_text}

CANDIDATE RESUME:
{resume_text}

OUTPUT REQUIREMENTS (Markdown Format):

## 1. Executive Summary (The "Sell")
- Write a 3-sentence "Elevator Pitch" to the Hiring Manager.
- Focus on: Why this guy fits the PAIN POINT in the JD.

## 2. Match Analysis
- **Match Score**: 0-100
- **Key Selling Points**: 3 bullet points. Why should the client interview him?
- **Risk Assessment**: 3 bullet points. What concerns might the client have? (e.g., Job hopping, expensive, culture fit).

## 3. Interview Cheat Sheet
- 3 "Killer Questions" the Hiring Manager should ask to test the candidate's depth.
- Expected "Good Answer" vs "Red Flag Answer" for each.

## 4. Salary & Level Estimation
- Based on the experience, estimate the likely P-level (e.g., P6/P7) and salary expectation range (if inferable).

## 5. Skill Radar (JSON)
Output a JSON block for radar chart visualization with exactly 6 dimensions:
```json
{{"radar": {{"专业技能": 0-100, "项目经验": 0-100, "学历背景": 0-100, "行业匹配": 0-100, "稳定性": 0-100, "性价比": 0-100}}}}
```
(Note: "稳定性" and "性价比" are key for Headhunters).

TONE: Professional, Objective, Sales-driven.
LANGUAGE: Chinese (Simplified).
        """
        return prompt

    def _generate_cache_key(
        self,
        resume_text: str,
        jd_text: str,
        persona: str
    ) -> str:
        """Generate a cache key for the analysis request."""
        content = f"{resume_text}:{jd_text}:{persona}"
        return hashlib.md5(content.encode()).hexdigest()

    def _extract_score(self, report: str) -> Optional[int]:
        """Extract match score from the report."""
        import re
        try:
            # Look for patterns like "65/100", "Score: 65", "65分"
            patterns = [
                r"Score.*?(\d+)",
                r"(\d+)/100",
                r"(\d+)分",
                r"Match.*?(\d+)",
            ]
            for pattern in patterns:
                match = re.search(pattern, report, re.IGNORECASE)
                if match:
                    score = int(match.group(1))
                    if 0 <= score <= 100:
                        return score
        except Exception:
            pass
        return None

    def parse_document(self, file_path: str) -> ParsedDocument:
        """
        Parse a document file.

        Args:
            file_path: Path to the document

        Returns:
            ParsedDocument object
        """
        try:
            parser = get_parser_for_file(file_path)
            return parser.parse(file_path)
        except UnsupportedFormatError:
            raise
        except Exception as e:
            raise ResumeSniperError(f"Failed to parse document: {e}")

    def batch_analyze(
        self,
        resumes: List[str],
        jd_text: str,
        persona: str = "hrbp",
        use_cache: bool = True,
        show_progress: bool = True
    ) -> List[AnalysisResult]:
        """
        Analyze multiple resumes against a single JD.

        Args:
            resumes: List of resume texts
            jd_text: Job description text
            persona: Analysis persona
            use_cache: Whether to use cached results
            show_progress: Show progress bar

        Returns:
            List of AnalysisResult objects
        """
        results = []
        total = len(resumes)

        for i, resume in enumerate(resumes):
            if show_progress:
                print(f"Processing {i + 1}/{total}...")

            try:
                result = self.analyze(
                    resume_text=resume,
                    jd_text=jd_text,
                    persona=persona,
                    use_cache=use_cache
                )
                results.append(result)
            except Exception as e:
                results.append(AnalysisResult(
                    report=f"Analysis failed: {e}",
                    score=None,
                    metadata={"error": str(e)}
                ))

        return results

    def get_provider_info(self) -> Dict:
        """Get information about the current LLM provider."""
        if not self._llm_provider:
            return {}

        return {
            "provider": self._current_provider,
            "models": self._llm_provider.supported_models,
            "available": self._llm_provider.is_available()
        }

    def health_check(self) -> Dict:
        """Check the health of all components."""
        status = {
            "llm_provider": {
                "provider": self._current_provider,
                "healthy": False,
                "error": None
            },
            "storage": {
                "enabled": self._storage is not None,
                "healthy": False,
                "error": None
            }
        }

        # Check LLM provider
        try:
            if self._llm_provider and self._llm_provider.health_check():
                status["llm_provider"]["healthy"] = True
        except Exception as e:
            status["llm_provider"]["error"] = str(e)

        # Check storage
        if self._storage:
            try:
                test_key = "__health_check__"
                self._storage.save(test_key, {"test": True}, ttl=60)
                loaded = self._storage.load(test_key)
                if loaded:
                    status["storage"]["healthy"] = True
                    self._storage.delete(test_key)
            except Exception as e:
                status["storage"]["error"] = str(e)

        return status


def create_engine(config_path: str = None, **kwargs) -> ResumeSniperEngine:
    """
    Factory function to create a ResumeSniperEngine instance.

    Args:
        config_path: Path to config file
        **kwargs: Additional configuration overrides

    Returns:
        ResumeSniperEngine instance
    """
    if config_path:
        from src.core.config import reload_config
        reload_config(config_path)

    return ResumeSniperEngine(**kwargs)
