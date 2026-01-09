"""
Legacy Compatibility / 向后兼容模块

v1.3 provides backward compatibility for v1.2 code.
Use the new plugin architecture for new projects.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
_src_path = Path(__file__).parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

# Import from new architecture
from src.core.engine import ResumeSniperEngine, create_engine, AnalysisResult
from src.core.config import get_config
from src.plugins.document_parsers import get_parser_for_file

# --- Legacy Imports (保持与 v1.2 API 兼容) ---

# 模拟数据
DEMO_JD = """
职位：AI产品经理
1. 负责公司AI产品的规划与设计，能够独立完成PRD文档。
2. 熟悉大模型(LLM)应用场景，有RAG/Agent开发经验者优先。
3. 具备极强的逻辑思维能力和数据分析能力。
4. 3年以上互联网产品经验，有B端SaaS经验最佳。
"""

DEMO_RESUME = """
张三
经验：3年
职位：人事专员 -> 招聘经理
工作描述：
1. 负责公司的招聘工作，筛选简历，安排面试。
2. 优化了招聘流程，提高了效率。
3. 熟悉使用各种办公软件，Word, Excel。
4. 自学了Python，了解一些AI知识。
"""


class ResumeSniper:
    """
    Legacy Resume Sniper Class (v1.2 API)

    For new projects, use: from src.core.engine import ResumeSniperEngine
    """

    def __init__(self, model: str = "deepseek-chat"):
        """
        Initialize ResumeSniper (Legacy API).

        Args:
            model: Model name (default: deepseek-chat)
        """
        self.model = model
        self._engine = None
        self._setup_engine()

    def _setup_engine(self):
        """Initialize the engine."""
        try:
            self._engine = create_engine()
        except Exception:
            # Fallback to mock mode
            self._engine = None

    def construct_prompt(self, resume_text: str, jd_text: str) -> str:
        """
        Construct the core prompt (Legacy API).
        """
        # Use new engine's prompt construction
        if self._engine:
            return self._engine._construct_prompt(
                resume_text, jd_text,
                self._engine._personas.get("hrbp", {})
            )
        return self._get_mock_prompt(resume_text, jd_text)

    def _get_mock_prompt(self, resume_text: str, jd_text: str) -> str:
        """Get mock prompt for demo."""
        return f"TASK:\nAnalyze resume:\n{resume_text}\n\nVS JD:\n{jd_text}"

    def analyze(self, resume_text: str, jd_text: str) -> str:
        """
        Main execution method (Legacy API).

        Returns report as string (compatible with v1.2).
        """
        if self._engine:
            try:
                result = self._engine.analyze(
                    resume_text=resume_text,
                    jd_text=jd_text,
                    persona="hrbp",
                    use_cache=False
                )
                return result.report
            except Exception:
                pass

        # Fallback to mock response
        return self._get_mock_response()

    def _get_mock_response(self) -> str:
        """Returns a hardcoded response for demo."""
        return """
# 🩺 Resume Sniper Report (DEMO)

## 1. 🎯 Match Score: 65/100
**Status: Backup Pile.**

## 2. 🚩 Fatal Red Flags
1. No Quantifiable Outcomes
2. Vague Tech Stack
3. Passive Voice

## 3. 💎 The "Money" Bullet Points (STAR Rewrite)
- Situation: Faced a 45-day average time-to-fill...
- Action: Designed and implemented a semi-automated workflow...
- Result: Decreased TTF to 18 days...

## 4. 💡 Quick Fixes
1. Add Numbers
2. Kill the "Objective" Section
3. Format Consistency
"""

    # Backward compatibility: old method names
    def run_analysis(self, resume_text: str, jd_text: str) -> str:
        """Alias for analyze() (legacy API)."""
        return self.analyze(resume_text, jd_text)


class DocumentParser:
    """
    Legacy Document Parser Class (v1.2 API)
    """

    def __init__(self):
        """Initialize parser."""
        pass

    def parse_file(self, file_path: str) -> str:
        """
        Parse a file and return its content (Legacy API).
        """
        try:
            doc = get_parser_for_file(file_path)
            parsed = doc.parse(file_path)
            return parsed.content
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return ""

    def _parse_pdf(self, file_path: str) -> str:
        """Legacy method for PDF parsing."""
        return self.parse_file(file_path)

    def _parse_docx(self, file_path: str) -> str:
        """Legacy method for DOCX parsing."""
        return self.parse_file(file_path)

    def _parse_text(self, file_path: str) -> str:
        """Legacy method for text parsing."""
        return self.parse_file(file_path)


# --- Module Functions (Backward Compatible) ---

def load_dotenv():
    """Load environment variables (legacy compatibility)."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass


# Auto-load environment on import
load_dotenv()


# --- Main Entry Point (Backward Compatible) ---
if __name__ == "__main__":
    # New v1.3 API
    print("=" * 50)
    print("AI Resume Sniper v1.3")
    print("=" * 50)

    engine = create_engine()
    print(f"Provider: {engine.get_provider_info()}")

    # Legacy API
    print("\n" + "=" * 50)
    print("Legacy API Demo")
    print("=" * 50)

    sniper = ResumeSniper()
    report = sniper.analyze(DEMO_RESUME, DEMO_JD)
    print(report)
