import sys
sys.stdout.reconfigure(encoding='utf-8')

from backend.nlp.processors.cv_processor import CVProcessor

# Test full CV processor pipeline with your resume
result = CVProcessor.process_file(
    r"C:\Users\santi\Documents\Personal\cv-match\backend\nlp\cv_santiago_cardenas_student_english.pdf"
)

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
