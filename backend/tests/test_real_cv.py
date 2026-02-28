import json
import sys
from dotenv import load_dotenv

load_dotenv()

from cv_processor import CVProcessor

def test_file(file_path):
    print(f"\nProcessing file: {file_path}\n")
    result = CVProcessor.process_file(file_path)
    print(json.dumps(result, indent=2, default=str))

def test_text(text):
    print("\nProcessing pasted text...\n")
    result = CVProcessor.process_text(text)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    if len(sys.argv) > 1:
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
