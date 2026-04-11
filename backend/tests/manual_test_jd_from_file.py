"""
Quick test script to load a job description from a .txt file
and run it through the NLP preprocessing pipeline.

Usage:
    python -m tests.test_jd_from_file path/to/job_description.txt
"""

import sys
import json
import logging

from nlp_preprocessing import JobDescriptionPreprocessor

logging.basicConfig(level=logging.INFO)


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m tests.test_jd_from_file <path_to_jd.txt>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            jd_text = f.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        sys.exit(1)

    print(f"Loaded JD from: {file_path}")
    print(f"Text length: {len(jd_text)} characters")
    print("-" * 50)

    preprocessor = JobDescriptionPreprocessor()
    result = preprocessor.preprocess(jd_text)

    print("\n=== CLEANED TEXT ===")
    print(result["cleaned_text"][:300])

    print("\n=== REQUIRED SKILLS ===")
    print(result["required_skills"])

    print("\n=== PREFERRED SKILLS ===")
    print(result["preferred_skills"])

    print("\n=== EXPERIENCE ===")
    print(result["experience_years"])

    print("\n=== EDUCATION ===")
    print(result["education_level"])

    print("\n=== KEY PHRASES ===")
    print(result["key_phrases"])

    print("\n=== FULL JSON OUTPUT ===")
    output = {k: v for k, v in result.items() if k != "original_text"}
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
