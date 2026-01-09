import os
import sys

# Add src to path to allow import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from resume_sniper import ResumeSniper

def generate_report(resume_name="sample_resume_A.md", jd_name="sample_jd_A.md"):
    """Generate report for specified resume and JD files."""
    # Define base paths relative to this script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')

    # Paths
    resume_path = os.path.join(data_dir, resume_name)
    jd_path = os.path.join(data_dir, jd_name)
    output_name = resume_name.replace("sample_resume", "report").replace(".md", "") + ".md"
    output_path = os.path.join(data_dir, output_name)

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
    # Test Set A
    print("=" * 60)
    print("Test Set A: Sample Resume A vs Sample JD A")
    print("=" * 60)
    generate_report("sample_resume_A.md", "sample_jd_A.md")

    print("\n")
    # Test Set B (战斗策划 vs 系统策划)
    print("=" * 60)
    print("Test Set B: 战斗策划简历 vs 系统策划JD")
    print("=" * 60)
    generate_report("sample_resume_B.md", "sample_jd_B.md")
