# /*
# FILE : test_real_cv.py
# PROJECT : CVMatch - CV Processing Module (Task 1)
# PROGRAMMER : Santiago Cardenas and Amel Sunil
# FIRST VERSION : 2025-02-27
# DESCRIPTION : Quick test script to process a real CV file or pasted text
#               using the CVProcessor pipeline. Requires a valid .env file
#               with OPENAI_API_KEY set.
# */

import json
import sys
from dotenv import load_dotenv

load_dotenv()

from cv_processor import CVProcessor


# /*
# * function name: test_file()
# * Description: Processes a CV file (PDF, DOCX, or TXT) and prints the result.
# * Parameter: file_path : str : Path to the CV file.
# * return: void
# */
def test_file(file_path):
    print(f"\nProcessing file: {file_path}\n")
    result = CVProcessor.process_file(file_path)
    print(json.dumps(result, indent=2, default=str))


# /*
# * function name: test_text()
# * Description: Processes raw CV text and prints the result.
# * Parameter: text : str : The raw CV text to parse.
# * return: void
# */
def test_text(text):
    print("\nProcessing pasted text...\n")
    result = CVProcessor.process_text(text)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Usage: python test_real_cv.py path/to/resume.pdf
        test_file(sys.argv[1])
    else:
        print("=" * 50)
        print("CVMatch - Real CV Test")
        print("=" * 50)
        print("\nOptions:")
        print("  1. Test with a file (PDF, DOCX, TXT)")
        print("  2. Test with pasted text")
        choice = input("\nChoose (1 or 2): ").strip()

        if choice == "1":
            path = input("Enter file path: ").strip()
            test_file(path)
        elif choice == "2":
            print("Paste your CV text below (type END on a new line when done):")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            test_text("\n".join(lines))
        else:
            print("Invalid choice.")
