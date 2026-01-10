import os
import requests
import json
import time

# Configuration
API_URL = "http://127.0.0.1:8000"
RESUME_CONTENT = """
John Doe
Software Engineer
Experience: 5 years in Python, FastAPI, React.
Skills: Python, JavaScript, SQL.
"""
JD_CONTENT = """
Senior Python Developer
Requirements:
- 5+ years experience with Python
- Experience with FastAPI and React
- Strong SQL skills
"""

def check_env_vars():
    print("\n[1/4] Checking Environment Variables...")
    # Load from .env if exists (simple parsing)
    if os.path.exists(".env"):
        print("Loading .env file...")
        with open(".env", "r", encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        key, val = parts
                        os.environ[key] = val.strip('"').strip("'")
    
    # Check config.yaml to see what env var is expected
    # Assuming DEEPSEEK_API_KEY based on previous read
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
    if deepseek_key:
        print(f"✅ DEEPSEEK_API_KEY found: {deepseek_key[:4]}...{deepseek_key[-4:]}")
    else:
        print("❌ DEEPSEEK_API_KEY NOT found in environment variables!")

def check_health():
    print("\n[2/4] Checking API Health...")
    try:
        resp = requests.get(f"{API_URL}/health")
        if resp.status_code == 200:
            print(f"✅ API is Healthy: {resp.json()}")
            return True
        else:
            print(f"❌ API Unhealthy: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return False

def test_analyze():
    print("\n[3/4] Testing /analyze Endpoint...")
    
    # Create temp files
    with open("temp_resume.txt", "w", encoding="utf-8") as f:
        f.write(RESUME_CONTENT)
    with open("temp_jd.txt", "w", encoding="utf-8") as f:
        f.write(JD_CONTENT)
        
    try:
        start_time = time.time()
        print("Sending request... (this may take a few seconds)")
        
        # Use context managers to ensure files are closed properly
        with open("temp_resume.txt", 'rb') as f_resume, open("temp_jd.txt", 'rb') as f_jd:
            files = {
                'resume_file': ('resume.txt', f_resume, 'text/plain'),
                'jd_file': ('jd.txt', f_jd, 'text/plain')
            }
            data = {
                'persona': 'hrbp'
            }
            
            resp = requests.post(f"{API_URL}/analyze", files=files, data=data)
        
        duration = time.time() - start_time
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"✅ Analysis Successful ({duration:.2f}s)")
            print(f"Model: {result.get('model')}")
            print(f"Score: {result.get('score')}")
            print(f"Report Preview: {result.get('report')[:100]}...")
            return True
        else:
            print(f"❌ Analysis Failed: {resp.status_code}")
            print(f"Detail: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return False
    finally:
        # Cleanup
        try:
            if os.path.exists("temp_resume.txt"): os.remove("temp_resume.txt")
            if os.path.exists("temp_jd.txt"): os.remove("temp_jd.txt")
        except Exception as e:
            print(f"Warning: Cleanup failed: {e}")

def main():
    print("\n" + "="*50)
    print("TalentOS Setup Verification")
    print("="*50 + "\n")
    check_env_vars()
    if check_health():
        test_analyze()
    else:
        print("Skipping analysis test due to health check failure.")

if __name__ == "__main__":
    main()
