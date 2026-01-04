import os
import sys

# Add src to path to allow import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from resume_sniper import ResumeSniper

def generate_report():
    # Define base paths relative to this script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')

    # Paths
    resume_path = os.path.join(data_dir, "sample_resume_A.md")
    jd_path = os.path.join(data_dir, "sample_jd_A.md")
    output_path = os.path.join(data_dir, "sample_report_A.md")

    # Read files
    try:
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_content = f.read()
        print(f"Loaded Resume: {len(resume_content)} chars")
        
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_content = f.read()
        print(f"Loaded JD: {len(jd_content)} chars")

    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return

    # Initialize Sniper
    print("Initializing ResumeSniper...")
    sniper = ResumeSniper()

    # Analyze
    print("Running analysis... (This may take a few seconds)")
    try:
        report = sniper.analyze(resume_content, jd_content)
        
        # Save Report
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"✅ Success! Report saved to: {output_path}")
        print("Preview of Report:")
        print("-" * 50)
        print(report[:500] + "...")
        print("-" * 50)

    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    generate_report()
