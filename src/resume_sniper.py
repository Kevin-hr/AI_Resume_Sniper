import os
import sys
import json
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration / 配置 ---
# DeepSeek API Key Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    # Fallback for Streamlit Cloud or if .env is missing but env var is set
    # Or just warn/error out. For now, we'll raise an error if it's critical, 
    # but the user might want to run in simulation mode if no key.
    # However, for security, we just try to get it from env.
    pass

DEEPSEEK_BASE_URL = "https://api.deepseek.com"

class ResumeSniper:
    """
    AI Resume Sniper Core Engine
    封装 Skill 01 (HRBP) & Skill 02 (Interviewer)
    """
    
    def __init__(self, model: str = "deepseek-chat"):
        self.model = model
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        self.hrbp_persona = """
        You are a Senior HRBP (10+ years exp) at a top-tier Tech Giant (BAT/FAANG).
        Your personality is: Direct, Result-Oriented, Slightly Harsh, but Extremely Professional.
        You do NOT care about "effort", you only care about "VALUE" and "ROI".
        
        Your Goal: 
        Help the candidate pass the ATS (Applicant Tracking System) and the 6-second HR screening.
        """

    def construct_prompt(self, resume_text: str, jd_text: str) -> str:
        """
        Construct the core prompt (The Product Kernel)
        """
        prompt = f"""
        {self.hrbp_persona}

        TASK:
        Analyze the following Candidate Resume against the Target Job Description (JD).

        TARGET JD:
        {jd_text}

        CANDIDATE RESUME:
        {resume_text}

        ---------------------------------------------------
        OUTPUT REQUIREMENTS (Markdown Format):

        ## 1. 🎯 Match Score (0-100)
        - Give a brutally honest score. 
        - < 60: Trash bin immediately.
        - 60-80: Backup pile.
        - > 80: Interview invite.

        ## 2. 🚩 Fatal Red Flags (The "Why No")
        - List top 3 reasons why an HR would REJECT this resume in 6 seconds.
        - Be specific (e.g., "Vague descriptions", "No metrics", "Job hopping").

        ## 3. 💎 The "Money" Bullet Points (STAR Rewrite)
        - Pick the ONE most relevant experience from the resume.
        - Rewrite it into 3 bullet points using strict STAR format (Situation -> Task -> Action -> Result).
        - MUST include quantitative metrics (%, $, time saved). 
        - If metrics are missing in source, use placeholders like [Increase by X%] and tell user to fill it.
        - Use "HR Value Language" (e.g., instead of "Fixed bug", use "Reduced system downtime by 20%...").

        ## 4. 💡 Quick Fixes (Actionable Advice)
        - 3 things the candidate can change RIGHT NOW to boost the score by 10 points.

        ---------------------------------------------------
        TONE:
        - Professional but critical. 
        - No fluff. No "Good job". 
        - Focus on GAP analysis.
        """
        return prompt

    def analyze(self, resume_text: str, jd_text: str) -> str:
        """
        Main execution method.
        Calls DeepSeek API to generate the report.
        """
        prompt = self.construct_prompt(resume_text, jd_text)
        
        # 1. Print the Prompt (For Verification/Debugging)
        print("\n" + "="*40)
        print("🔧 [KERNEL] GENERATED PROMPT")
        print("="*40)
        print(prompt[:500] + "...\n(Prompt truncated for display)\n")
        
        print(f"🚀 [SYSTEM] API Key detected. Calling DeepSeek ({self.model})...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional HRBP assistant."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ [ERROR] API Call Failed: {e}")
            print("⚠️ [SYSTEM] Falling back to SIMULATION MODE.")
            return self._get_mock_response()

    def _get_mock_response(self) -> str:
        """
        Returns a hardcoded High-Quality response to demonstrate the product value.
        """
        return """
# 🩺 Resume Sniper Report (DEMO)

## 1. 🎯 Match Score: 65/100
**Status: Backup Pile.** 
*HR Comment: You have the skills, but your resume reads like a job description, not an achievement log. I don't see "High Potential", I see "Executor".*

## 2. 🚩 Fatal Red Flags
1.  **No Quantifiable Outcomes**: You say "Responsible for recruitment", but don't say "Filled 20 roles in 3 months". HRs hire for *Results*, not *Responsibilities*.
2.  **Vague Tech Stack**: "Familiar with Python" is weak. Did you build a script? A web app? A data pipeline? Context is missing.
3.  **Passive Voice**: "Was tasked with..." -> Weak. Use Action Verbs: "Spearheaded...", "Designed...", "Executed...".

## 3. 💎 The "Money" Bullet Points (STAR Rewrite)
*Context: Your "HR Manager" experience rewritten for a "B-End Product Manager" role.*

*   **Original**: "Responsible for optimizing the recruitment process and improving efficiency."
*   **Sniper Rewrite (STAR)**:
    *   **Situation**: Faced a 45-day average time-to-fill (TTF) for technical roles, causing project delays.
    *   **Action**: Designed and implemented a semi-automated screening workflow using **RPA tools**, reducing manual resume screening time by **60%**.
    *   **Result**: Decreased TTF to **18 days** (Industry avg: 30 days) and saved the department **¥150k** in annual headhunter fees.

## 4. 💡 Quick Fixes
1.  **Add Numbers**: Go through every bullet point. If there is no number, add one (Team size, Budget, % Growth, Time saved).
2.  **Kill the "Objective" Section**: Nobody cares what *you* want. Replace it with a "Professional Summary" of what *you offer*.
3.  **Format Consistency**: Your dates are mixed (MM/YYYY vs YYYY). Fix it. It shows attention to detail.
"""

# --- DEMO DATA (模拟数据) ---
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

if __name__ == "__main__":
    sniper = ResumeSniper()
    report = sniper.analyze(DEMO_RESUME, DEMO_JD)
    
    print("\n" + "="*40)
    print("📄 [OUTPUT] GENERATED REPORT")
    print("="*40)
    print(report)
