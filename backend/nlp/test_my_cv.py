import sys
sys.stdout.reconfigure(encoding='utf-8')

from cv_processor.cv_processor import CVProcessor

# Test full CV processor pipeline with your resume
result = CVProcessor.process_file("santiago resume.pdf")

print("=== CONTACT ===")
for key, value in result["contact"].items():
    print(f"  {key}: {value}")

print("\n=== SKILLS ===")
for skill in sorted(result["skills"]):
    print(f"  - {skill}")
print(f"  Total: {len(result['skills'])}")

print("\n=== EXPERIENCE ===")
for i, exp in enumerate(result["experience"], 1):
    print(f"  [{i}] {exp.get('title', 'N/A')} @ {exp.get('company', 'N/A')}")
    print(f"      {exp.get('start_date', '?')} - {exp.get('end_date', '?')}")

print("\n=== EDUCATION ===")
for i, edu in enumerate(result["education"], 1):
    print(f"  [{i}] {edu.get('degree', 'N/A')}")
    print(f"      {edu.get('institution', 'N/A')}")
    print(f"      {edu.get('graduation_date', 'N/A')}")
