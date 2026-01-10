import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.engine import ResumeSniperEngine

OUTPUT_DIR = Path("tests/fixtures/resumes")

ROLES = [
    "Senior Java Backend Engineer",
    "Product Manager (B2B SaaS)",
    "Human Resources Director",
    "Frontend Developer (React/Vue)",
    "Data Scientist (NLP focus)"
]

async def generate_mock_resume(engine, role):
    print(f"Generating resume for: {role}...")
    
    prompt = f"""
    Generate a realistic, high-quality resume for a {role}.
    
    The resume should include:
    1.  **Contact Info**: Use FAKE data (e.g., John Doe, +86 13800000000, fake@email.com).
    2.  **Summary**: A professional summary.
    3.  **Experience**: 2-3 relevant job positions with dates and bullet points.
    4.  **Education**: Relevant degree and university.
    5.  **Skills**: Technical and soft skills.
    
    Format: Plain text or Markdown.
    Language: Chinese (Simplified) or English (mixed is fine).
    Length: ~500-800 words.
    
    Do NOT include any preamble or postscript. Just the resume content.
    """
    
    try:
        # We reuse the _call_llm_with_retry method via a public wrapper or just modify engine to expose it?
        # Since engine._call_llm_with_retry is protected, let's use a public method if available, 
        # or access it directly for this script since we are "devs".
        # Actually, let's use a "General Analysis" type call if possible, or just hack it.
        # Ideally, we should add a `generate_content` method to Engine, but I'll use `optimize_jd` hack or just access protected member.
        # Accessing protected member is fine for a script.
        
        response = engine._call_llm_with_retry(
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        content = response.content
        
        # Save to file
        filename = f"Resume_{role.replace(' ', '_').replace('/', '-')}.txt"
        file_path = OUTPUT_DIR / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"✅ Saved: {file_path}")
        
    except Exception as e:
        print(f"❌ Failed to generate for {role}: {e}")

async def main():
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)
        
    print("Initializing Engine...")
    engine = ResumeSniperEngine()
    
    tasks = []
    # Generate sequentially to avoid rate limits if any, or just loop
    for role in ROLES:
        await generate_mock_resume(engine, role)
        
    print("\nAll done! Check tests/fixtures/resumes/")

if __name__ == "__main__":
    asyncio.run(main())
